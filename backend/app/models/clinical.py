from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class UrgencyLevel(str, Enum):
    ELECTIVA = "ELECTIVA"
    URGENCIA = "URGENCIA"
    EMERGENCIA_VITAL = "EMERGENCIA_VITAL"


class DocumentAttachment(BaseModel):
    name: str = Field(..., description="Nombre del archivo o estudio")
    doc_type: str = Field(..., description="Categoría clínica (ecografia, laboratorio, riesgo_quirurgico, presupuesto, biopsia, etc.)")
    is_present: bool = Field(True, description="Indica si el documento fue adjuntado")
    file_url: Optional[str] = None
    notes: Optional[str] = None


class MedicalReport(BaseModel):
    patient_name: str = Field(..., description="Nombre completo del paciente")
    patient_id: str = Field(..., description="Cédula o ID del asegurado")
    patient_age: int = Field(..., description="Edad en años")
    patient_gender: str = Field("No especificado", description="Género del paciente (M/F/Otro)")
    hospital_name: str = Field(..., description="Hospital o clínica solicitante")
    treating_physician: str = Field(..., description="Médico o cirujano tratante")
    diagnosis_icd10: str = Field(..., description="Diagnóstico CIE-10 (código y/o descripción clínica)")
    procedure_name: str = Field(..., description="Procedimiento quirúrgico propuesto")
    procedure_cpt: Optional[str] = Field(None, description="Código CPT opcional del procedimiento")
    urgency: UrgencyLevel = Field(UrgencyLevel.ELECTIVA, description="Nivel de prioridad o urgencia quirúrgica")
    request_date: str = Field(..., description="Fecha de solicitud quirúrgica (YYYY-MM-DD)")
    estimated_cost: float = Field(2500.0, description="Presupuesto o costo estimado de la cirugía en USD")
    clinical_summary: str = Field("", description="Resumen de historia clínica, hallazgos y justificación")
    attachments: List[DocumentAttachment] = Field(default_factory=list, description="Lista de estudios y documentos adjuntos")
    raw_text: Optional[str] = Field(None, description="Texto transcrito u obtenido mediante OCR/Docling")
