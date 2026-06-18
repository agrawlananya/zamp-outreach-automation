from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)

from app.db.database import Base


class Prospect(Base):
    __tablename__ = "prospects"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    company_domain = Column(String)
    linkedin_url = Column(String)
    created_at = Column(DateTime)


class Run(Base):
    __tablename__ = "runs"

    id = Column(String, primary_key=True)
    prospect_id = Column(String, ForeignKey("prospects.id"), nullable=False)
    status = Column(String, nullable=False)
    current_stage = Column(String)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    time_to_draft_ms = Column(Integer)
    escalation_reason = Column(Text)


class Signal(Base):
    __tablename__ = "signals"

    id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
    scope = Column(String)  # company | individual
    type = Column(String)
    claim = Column(Text)
    source_url = Column(String)
    source_snippet = Column(Text)
    signal_date = Column(Date)
    entity = Column(String)
    validated = Column(Boolean)
    validation_reason = Column(Text)
    relevance_score = Column(Float)
    specificity_score = Column(Float)
    recency_score = Column(Float)
    actionability_score = Column(Float)
    verifiability_score = Column(Float)
    hook_score = Column(Float)
    selected_as_hook = Column(Boolean)


class PersonaMapping(Base):
    __tablename__ = "persona_mappings"

    id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
    persona_name = Column(String)
    is_assumed = Column(Boolean)
    goals = Column(Text)  # JSON
    pains = Column(Text)  # JSON
    kpis = Column(Text)  # JSON


class PainMapping(Base):
    __tablename__ = "pain_mappings"

    id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
    signal_id = Column(String, ForeignKey("signals.id"), nullable=False)
    owned_pain = Column(String)
    owned_kpi = Column(String)
    zamp_value_prop = Column(Text)


class Draft(Base):
    __tablename__ = "drafts"

    id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
    version = Column(Integer)
    subject = Column(String)
    body = Column(Text)
    sources_used = Column(Text)  # JSON array of signal ids
    rubric_scores = Column(Text)  # JSON
    groundedness_pass = Column(Boolean)
    created_at = Column(DateTime)


class ReviewAction(Base):
    __tablename__ = "review_actions"

    id = Column(String, primary_key=True)
    draft_id = Column(String, ForeignKey("drafts.id"), nullable=False)
    action = Column(String)  # approve | approve_with_edits | reject
    edited_body = Column(Text)
    reason = Column(Text)
    reviewed_at = Column(DateTime)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
    stage = Column(String)
    input_snapshot = Column(Text)  # JSON
    output_snapshot = Column(Text)  # JSON
    model_used = Column(String)
    latency_ms = Column(Integer)
    status = Column(String)  # ok | degraded | failed
    error_message = Column(Text)
    created_at = Column(DateTime)
