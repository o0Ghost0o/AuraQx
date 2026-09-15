from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ResolutionStatus(str, Enum):
    PRE_APROBADO = "PRE_APROBADO"
    DOCUMENTOS_FALTANTES = "DOCUMENTOS_FALTANTES"
    RECHAZADO = "RECHAZADO"
    EN_AUDITORIA_MANUAL = "EN_AUDITORIA_MANUAL"


class CarenciaAuditResult(BaseModel):
    category_evaluated: str
    required_months: int
    elapsed_days: int
    elapsed_months: float
    is_satisfied: bool
    exception_applied: Optional[str] = None
    explanation: str


class FinancialBreakdown(BaseModel):
    estimated_total: float
    in_network: bool
    coverage_percent: float
    deductible_applied: float
    insurer_pays: float
    patient_copay: float
    currency: str = "USD"


class MissingDocumentRequirement(BaseModel):
    doc_type: str
    title: str
    mandatory: bool
    medical_rationale: str
    suggested_action: str


class TelemetryEvent(BaseModel):
    step: int
    title: str
    status: str = Field("running", description="'running', 'success', 'warning', 'error'")
    detail: str
    timestamp: str


class PreAuthResolution(BaseModel):
    case_id: str
    status: ResolutionStatus
    patient_id: str
    patient_name: str
    policy_number: str
    procedure_name: str
    hospital_name: str
    request_date: str
    carencia_audit: CarenciaAuditResult
    financials: FinancialBreakdown
    missing_documents: List[MissingDocumentRequirement] = Field(default_factory=list)
    clinical_justification: str
    authorization_code: Optional[str] = None
    qr_data: str
    created_at: str
    notion_synced: bool = False
    notion_url: Optional[str] = None
