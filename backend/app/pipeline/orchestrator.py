import json
import time
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.db_models import AuditLog, Draft, PainMapping, PersonaMapping, Run, Signal
from app.models.schemas import NormalizedProspect, RawCorpus
from app.pipeline import (
    stage1_intake,
    stage2_company_research,
    stage3_individual_research,
    stage4_extract_signals,
    stage5_validate_signals,
    stage6_persona_mapping,
    stage7_pain_mapping,
    stage8_hook_scoring,
    stage9_draft_generation,
    stage10_quality_scoring,
    stage11_routing,
)
from app.pipeline.stage8_hook_scoring import HookSelection
from app.pipeline.stage10_quality_scoring import RubricScore


def _signal_snapshot(signal: Signal) -> dict:
    return {
        "id": signal.id,
        "type": signal.type,
        "claim": signal.claim,
        "validated": signal.validated,
        "hook_score": signal.hook_score,
        "selected_as_hook": signal.selected_as_hook,
    }


def _corpus_snapshot(corpus: RawCorpus) -> dict:
    return {
        "source": corpus.source,
        "item_count": len(corpus.items),
        "thin_corpus": corpus.thin_corpus,
        "role_change_detected": corpus.role_change_detected,
    }


def _persona_snapshot(persona: PersonaMapping) -> dict:
    return {"persona_name": persona.persona_name, "is_assumed": persona.is_assumed}


def _pain_mapping_snapshot(pain_mapping: PainMapping) -> dict:
    return {"signal_id": pain_mapping.signal_id, "owned_pain": pain_mapping.owned_pain, "owned_kpi": pain_mapping.owned_kpi}


def _hook_selection_snapshot(hook_selection: HookSelection) -> dict:
    return {
        "selected_signal_id": hook_selection.selected_signal.id if hook_selection.selected_signal else None,
        "top_score_sufficient": hook_selection.top_score_sufficient,
        "candidate_count": len(hook_selection.all_scores),
    }


def _draft_snapshot(draft: Draft) -> dict:
    return {"id": draft.id, "version": draft.version, "subject": draft.subject}


def _rubric_score_snapshot(rubric_score: RubricScore) -> dict:
    return {"scores": rubric_score.scores, "groundedness_pass": rubric_score.groundedness_pass}


class PipelineOrchestrator:
    def run(self, run_id: str, db: Session) -> None:
        run = db.query(Run).filter(Run.id == run_id).one()
        start_time = time.time()
        run.status = "running"
        db.commit()

        # Stage 1 — intake (not continuable: nothing downstream is possible without a normalized prospect)
        normalized, ok = self._execute_stage(
            db, run, "stage1_intake", None, {"prospect_id": run.prospect_id},
            lambda: stage1_intake.intake_and_normalize(run.prospect_id, db),
            output_snapshot_fn=lambda r: r.model_dump(),
        )
        if not ok:
            self._fail_run(db, run, start_time)
            return

        # Stage 2 — company research (continuable: degrades to an empty corpus)
        company_corpus, ok = self._execute_stage(
            db, run, "stage2_company_research", None, {"domain": normalized.company_domain},
            lambda: stage2_company_research.research_company(
                normalized.company_domain, normalized.company_name, normalized.name
            ),
            output_snapshot_fn=_corpus_snapshot,
            continuable=True,
            fallback=RawCorpus(source="company", items=[]),
        )

        # Stage 3 — individual research (continuable: degrades to an empty corpus)
        individual_corpus, ok = self._execute_stage(
            db, run, "stage3_individual_research", None, {"name": normalized.name},
            lambda: stage3_individual_research.research_individual(normalized.name, normalized.company_name),
            output_snapshot_fn=_corpus_snapshot,
            continuable=True,
            fallback=RawCorpus(source="individual", items=[]),
        )

        # EC-3: prospect appears to have moved to a different company than submitted — too
        # ambiguous to draft confidently, so escalate to a human rather than guess.
        if individual_corpus.role_change_detected:
            detection = individual_corpus.role_change_detected
            run.escalation_reason = (
                f"Possible role change detected: prospect may have moved to "
                f"'{detection['new_company']}' (source: {detection.get('source_url', 'unknown')})."
            )
            run.status = "needs_human_research"
            run.completed_at = datetime.utcnow()
            run.time_to_draft_ms = int((time.time() - start_time) * 1000)
            db.commit()
            return

        # Stage 4 — extract signals (continuable: degrades to no signals -> naturally routes to insufficient_signal)
        extracted_signals, ok = self._execute_stage(
            db, run, "stage4_extract_signals", "extractor",
            {"company_items": len(company_corpus.items), "individual_items": len(individual_corpus.items)},
            lambda: stage4_extract_signals.extract_signals([company_corpus, individual_corpus], run_id, db),
            output_snapshot_fn=lambda r: {"signal_count": len(r)},
            continuable=True,
            fallback=[],
        )

        # Stage 5 — validate signals (continuable)
        validated_signals, ok = self._execute_stage(
            db, run, "stage5_validate_signals", "verifier", {"signal_count": len(extracted_signals)},
            lambda: stage5_validate_signals.validate_signals(extracted_signals, run_id, db),
            output_snapshot_fn=lambda r: {"validated_count": len(r)},
            continuable=True,
            fallback=[],
        )

        # Stage 6 — persona mapping (not continuable: downstream pain mapping/draft need a persona)
        persona_mapping, ok = self._execute_stage(
            db, run, "stage6_persona_mapping", None, {"title": normalized.title},
            lambda: stage6_persona_mapping.map_persona(normalized.title, run_id, db),
            output_snapshot_fn=_persona_snapshot,
        )
        if not ok:
            self._fail_run(db, run, start_time)
            return

        # Stage 7 — pain mapping (continuable: degrades to no pain mappings, lowers relevance scores)
        pain_mappings, ok = self._execute_stage(
            db, run, "stage7_pain_mapping", None, {"signal_count": len(validated_signals)},
            lambda: stage7_pain_mapping.map_pain(validated_signals, persona_mapping, run_id, db),
            output_snapshot_fn=lambda r: {"pain_mapping_count": len(r)},
            continuable=True,
            fallback=[],
        )

        # Stage 8 — hook scoring (not continuable: deterministic, an exception here is unexpected)
        # EC-1: if both research corpora came back thin, force low confidence rather than let a
        # single thin signal masquerade as a strong hook.
        force_low_confidence = company_corpus.thin_corpus and individual_corpus.thin_corpus
        hook_selection, ok = self._execute_stage(
            db, run, "stage8_hook_scoring", None,
            {"signal_count": len(validated_signals), "force_low_confidence": force_low_confidence},
            lambda: stage8_hook_scoring.score_and_select_hook(
                validated_signals, pain_mappings, run_id, db, force_low_confidence=force_low_confidence
            ),
            output_snapshot_fn=_hook_selection_snapshot,
        )
        if not ok:
            self._fail_run(db, run, start_time)
            return

        if not hook_selection.top_score_sufficient or hook_selection.selected_signal is None:
            run.status = "insufficient_signal"
            run.completed_at = datetime.utcnow()
            run.time_to_draft_ms = int((time.time() - start_time) * 1000)
            db.commit()
            return

        # Stage 9 — draft generation (not continuable: no draft means nothing to review)
        draft, ok = self._execute_stage(
            db, run, "stage9_draft_generation", "writer",
            {"hook_signal_id": hook_selection.selected_signal.id, "version": 1},
            lambda: stage9_draft_generation.generate_draft(
                hook_selection.selected_signal, persona_mapping, pain_mappings, run_id, db, version=1
            ),
            output_snapshot_fn=_draft_snapshot,
        )
        if not ok:
            self._fail_run(db, run, start_time)
            return

        # Stage 10 — quality scoring (not continuable: can't route without knowing groundedness)
        rubric_score, ok = self._execute_stage(
            db, run, "stage10_quality_scoring", "critic", {"draft_id": draft.id},
            lambda: stage10_quality_scoring.score_draft(draft, validated_signals, run_id, db),
            output_snapshot_fn=_rubric_score_snapshot,
        )
        if not ok:
            self._fail_run(db, run, start_time)
            return

        if not rubric_score.groundedness_pass:
            # One regeneration cap — no further retries after this.
            draft, ok = self._execute_stage(
                db, run, "stage9_draft_generation", "writer",
                {"hook_signal_id": hook_selection.selected_signal.id, "version": 2, "reason": "groundedness_retry"},
                lambda: stage9_draft_generation.generate_draft(
                    hook_selection.selected_signal, persona_mapping, pain_mappings, run_id, db, version=2
                ),
                output_snapshot_fn=_draft_snapshot,
            )
            if not ok:
                self._fail_run(db, run, start_time)
                return

            rubric_score, ok = self._execute_stage(
                db, run, "stage10_quality_scoring", "critic", {"draft_id": draft.id, "version": 2},
                lambda: stage10_quality_scoring.score_draft(draft, validated_signals, run_id, db),
                output_snapshot_fn=_rubric_score_snapshot,
            )
            if not ok:
                self._fail_run(db, run, start_time)
                return

        # Stage 11 — routing (pure, deterministic, no DB calls)
        status, ok = self._execute_stage(
            db, run, "stage11_routing", None,
            {"top_score_sufficient": hook_selection.top_score_sufficient, "groundedness_pass": rubric_score.groundedness_pass},
            lambda: stage11_routing.route(hook_selection, rubric_score),
            output_snapshot_fn=lambda r: {"status": r},
        )
        if not ok:
            self._fail_run(db, run, start_time)
            return

        run.status = status
        run.completed_at = datetime.utcnow()
        run.time_to_draft_ms = int((time.time() - start_time) * 1000)
        db.commit()

    def _fail_run(self, db: Session, run: Run, start_time: float) -> None:
        run.status = "failed"
        run.completed_at = datetime.utcnow()
        run.time_to_draft_ms = int((time.time() - start_time) * 1000)
        db.commit()

    def _execute_stage(
        self,
        db: Session,
        run: Run,
        stage_name: str,
        model_used,
        input_snapshot: dict,
        fn,
        output_snapshot_fn=lambda r: {},
        continuable: bool = False,
        fallback=None,
    ):
        run.current_stage = stage_name
        db.commit()

        t0 = time.time()
        try:
            result = fn()
        except Exception as e:
            latency_ms = int((time.time() - t0) * 1000)
            status = "degraded" if continuable else "failed"
            self._log_audit(db, run.id, stage_name, input_snapshot, None, model_used, latency_ms, status, str(e))
            if continuable:
                return fallback, True
            return None, False

        latency_ms = int((time.time() - t0) * 1000)
        self._log_audit(db, run.id, stage_name, input_snapshot, output_snapshot_fn(result), model_used, latency_ms, "ok")
        return result, True

    def _log_audit(
        self,
        db: Session,
        run_id: str,
        stage: str,
        input_snapshot: dict,
        output_snapshot,
        model_used,
        latency_ms: int,
        status: str,
        error_message: str = None,
    ) -> None:
        audit = AuditLog(
            id=str(uuid.uuid4()),
            run_id=run_id,
            stage=stage,
            input_snapshot=json.dumps(input_snapshot, default=str),
            output_snapshot=json.dumps(output_snapshot, default=str) if output_snapshot is not None else None,
            model_used=model_used,
            latency_ms=latency_ms,
            status=status,
            error_message=error_message,
            created_at=datetime.utcnow(),
        )
        db.add(audit)
        db.commit()


def run_pipeline_in_background(run_id: str) -> None:
    db = SessionLocal()
    try:
        PipelineOrchestrator().run(run_id, db)
    finally:
        db.close()
