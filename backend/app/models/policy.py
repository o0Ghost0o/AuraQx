from typing import List, Optional
from pydantic import BaseModel, Field


class CarenciaRule(BaseModel):
    category: str = Field(..., description="Categoría de procedimiento (ej. 'vesicula_hernias', 'maternidad_cesarea', 'emergencias', 'ortopedia_mayor')")
    required_months: int = Field(..., description="Meses mínimos de vigencia de póliza requeridos")
    description: str = Field(..., description="Descripción contractual de la carencia")


class InsuredPolicy(BaseModel):
    policy_number: str = Field(..., description="Número de póliza único")
    patient_id: str = Field(..., description="Cédula de identidad del asegurado")
    patient_name: str = Field(..., description="Nombre del asegurado titular o dependiente")
    plan_tier: str = Field("Plan Oro", description="Nivel de plan (Oro, Plata, Esmeralda, Platino)")
    start_date: str = Field(..., description="Fecha de inicio de vigencia de la póliza (YYYY-MM-DD)")
    status: str = Field("Activa", description="Estado de la póliza: Activa, Suspendida, Cancelada")
    annual_deductible: float = Field(250.0, description="Deducible anual total en USD")
    deductible_met: float = Field(0.0, description="Monto del deducible consumido en el año")
    coverage_percent_in_network: float = Field(80.0, description="Porcentaje de cobertura en hospitales de la red (ej. 80%)")
    coverage_percent_out_network: float = Field(60.0, description="Porcentaje de cobertura fuera de red (ej. 60%)")
    network_hospitals: List[str] = Field(default_factory=list, description="Lista de hospitales y clínicas en convenio")
    carencia_rules: List[CarenciaRule] = Field(default_factory=list, description="Reglas contractuales de carencias")
    exclusions: List[str] = Field(default_factory=list, description="Exclusiones expresas de la póliza")
    notion_page_id: Optional[str] = Field(None, description="ID del registro en Notion si está sincronizado")
