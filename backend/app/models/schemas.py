from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class ProspectCreate(BaseModel):
    name: str
    title: str
    company_name: str


class RunStatusResponse(BaseModel):
    status: str
    current_stage: Optional[str] = None
    percent_complete: int


class NormalizedProspect(BaseModel):
    id: str
    name: str
    title: str
    company_name: str
    company_domain: str


class CorpusItem(BaseModel):
    url: str
    title: str
    body_text: str
    published_date: Optional[str] = None


class RawCorpus(BaseModel):
    source: Literal["company", "individual"]
    items: list[CorpusItem] = []
    thin_corpus: bool = False
    role_change_detected: Optional[dict] = None


class SignalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    run_id: str
    scope: Optional[str] = None
    type: Optional[str] = None
    claim: Optional[str] = None
    source_url: Optional[str] = None
    source_snippet: Optional[str] = None
    signal_date: Optional[date] = None
    entity: Optional[str] = None
    validated: Optional[bool] = None
    validation_reason: Optional[str] = None
    relevance_score: Optional[float] = None
    specificity_score: Optional[float] = None
    recency_score: Optional[float] = None
    actionability_score: Optional[float] = None
    verifiability_score: Optional[float] = None
    hook_score: Optional[float] = None
    selected_as_hook: Optional[bool] = None


class PersonaMappingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    run_id: str
    persona_name: Optional[str] = None
    is_assumed: Optional[bool] = None
    goals: Optional[str] = None
    pains: Optional[str] = None
    kpis: Optional[str] = None


class PainMappingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    run_id: str
    signal_id: str
    owned_pain: Optional[str] = None
    owned_kpi: Optional[str] = None
    zamp_value_prop: Optional[str] = None


class DraftOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    run_id: str
    version: Optional[int] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    sources_used: Optional[str] = None
    rubric_scores: Optional[str] = None
    groundedness_pass: Optional[bool] = None
    created_at: Optional[datetime] = None


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    run_id: str
    stage: Optional[str] = None
    input_snapshot: Optional[str] = None
    output_snapshot: Optional[str] = None
    model_used: Optional[str] = None
    latency_ms: Optional[int] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None


class RunDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    prospect_id: str
    status: str
    current_stage: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    time_to_draft_ms: Optional[int] = None
    escalation_reason: Optional[str] = None
    signals: list[SignalOut] = []
    persona_mapping: Optional[PersonaMappingOut] = None
    pain_mappings: list[PainMappingOut] = []
    draft: Optional[DraftOut] = None
    audit_log: list[AuditLogOut] = []


class ReviewRequest(BaseModel):
    action: Literal["approve", "approve_with_edits", "reject"]
    edited_body: Optional[str] = None
    reason: Optional[str] = None


class MetricsResponse(BaseModel):
    acceptance_rate: float
    groundedness_pct: float
    escalation_rate: float
    avg_time_to_draft_ms: float
    avg_personalization_depth: float
