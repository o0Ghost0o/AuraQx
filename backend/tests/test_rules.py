import pytest
from app.core.rules_engine import audit_preauthorization, evaluate_carencia, calculate_financials
from app.models.clinical import DocumentAttachment, MedicalReport, UrgencyLevel
from app.models.policy import CarenciaRule, InsuredPolicy
from app.models.resolution import ResolutionStatus


@pytest.fixture
def mock_policy_oro():
    return InsuredPolicy(
        policy_number="POL-TEST-001",
        patient_id="0928374102",
        patient_name="María Carmen Mendoza",
        plan_tier="Plan Oro",
        start_date="2025-01-01",  # >18 meses
        status="Activa",
        annual_deductible=250.0,
        deductible_met=100.0,
        coverage_percent_in_network=80.0,
        coverage_percent_out_network=60.0,
        network_hospitals=["Hospital Metropolitano"],
        carencia_rules=[
            CarenciaRule(category="vesicula_hernias", required_months=10, description="10 meses")
        ],
        exclusions=["estética"],
    )


@pytest.fixture
def mock_policy_new():
    return InsuredPolicy(
        policy_number="POL-TEST-NEW",
        patient_id="0911223344",
        patient_name="Valeria Ramos",
        plan_tier="Plan Esmeralda",
        start_date="2026-06-01",  # ~3.5 meses
        status="Activa",
        annual_deductible=150.0,
        deductible_met=0.0,
        coverage_percent_in_network=85.0,
        coverage_percent_out_network=65.0,
        network_hospitals=["Hospital Metropolitano"],
        carencia_rules=[
            CarenciaRule(category="maternidad_cesarea", required_months=10, description="10 meses")
        ],
        exclusions=[],
    )


def test_emergency_carencia_zero_exception(mock_policy_new):
    report = MedicalReport(
        patient_name="Juan Morales",
        patient_id="0911223344",
        patient_age=34,
        patient_gender="M",
        hospital_name="Hospital Metropolitano",
        treating_physician="Dr. Guardia",
        diagnosis_icd10="K35.2 - Apendicitis aguda perforada",
        procedure_name="Apendicectomía laparoscópica de urgencia",
        urgency=UrgencyLevel.EMERGENCIA_VITAL,
        request_date="2026-09-15",
        estimated_cost=3000.0,
        attachments=[
            DocumentAttachment(name="lab.pdf", doc_type="laboratorio", is_present=True),
            DocumentAttachment(name="urgencia.pdf", doc_type="informe_urgencia", is_present=True),
            DocumentAttachment(name="presupuesto.pdf", doc_type="presupuesto", is_present=True),
        ]
    )

    carencia_eval = evaluate_carencia(report, mock_policy_new)
    assert carencia_eval.is_satisfied is True
    assert carencia_eval.required_months == 0
    assert carencia_eval.exception_applied is not None

    resolution = audit_preauthorization(report, mock_policy_new)
    assert resolution.status == ResolutionStatus.PRE_APROBADO
    assert resolution.authorization_code is not None


def test_cesarean_insufficient_carencia(mock_policy_new):
    report = MedicalReport(
        patient_name="Valeria Ramos",
        patient_id="0911223344",
        patient_age=29,
        patient_gender="F",
        hospital_name="Hospital Metropolitano",
        treating_physician="Dra. Alvear",
        diagnosis_icd10="O82 - Parto por cesárea",
        procedure_name="Cesárea programada",
        urgency=UrgencyLevel.ELECTIVA,
        request_date="2026-09-15",
        estimated_cost=3200.0,
        attachments=[
            DocumentAttachment(name="eco.pdf", doc_type="ecografia", is_present=True),
            DocumentAttachment(name="lab.pdf", doc_type="laboratorio", is_present=True),
            DocumentAttachment(name="obs.pdf", doc_type="informe_obstetrico", is_present=True),
            DocumentAttachment(name="presupuesto.pdf", doc_type="presupuesto", is_present=True),
        ]
    )

    carencia_eval = evaluate_carencia(report, mock_policy_new)
    assert carencia_eval.is_satisfied is False
    assert carencia_eval.required_months == 10

    resolution = audit_preauthorization(report, mock_policy_new)
    assert resolution.status == ResolutionStatus.RECHAZADO
    assert "Faltan" in resolution.clinical_justification


def test_colecistectomia_approved_when_all_docs_present(mock_policy_oro):
    report = MedicalReport(
        patient_name="María Carmen Mendoza",
        patient_id="0928374102",
        patient_age=45,  # >= 40 años, requiere riesgo quirúrgico
        patient_gender="F",
        hospital_name="Hospital Metropolitano",
        treating_physician="Dr. Morales",
        diagnosis_icd10="K80.2 - Calculosis de vesícula biliar",
        procedure_name="Colecistectomía laparoscópica",
        urgency=UrgencyLevel.ELECTIVA,
        request_date="2026-09-15",
        estimated_cost=2800.0,
        attachments=[
            DocumentAttachment(name="eco.pdf", doc_type="ecografia", is_present=True),
            DocumentAttachment(name="lab.pdf", doc_type="laboratorio", is_present=True),
            DocumentAttachment(name="riesgo.pdf", doc_type="riesgo_quirurgico", is_present=True),
            DocumentAttachment(name="presupuesto.pdf", doc_type="presupuesto", is_present=True),
        ]
    )

    resolution = audit_preauthorization(report, mock_policy_oro)
    assert resolution.status == ResolutionStatus.PRE_APROBADO
    assert len(resolution.missing_documents) == 0
    assert resolution.financials.coverage_percent == 80.0
    assert resolution.authorization_code is not None


def test_colecistectomia_missing_docs_when_cardiac_risk_omitted(mock_policy_oro):
    report = MedicalReport(
        patient_name="María Carmen Mendoza",
        patient_id="0928374102",
        patient_age=45,  # Requiere riesgo quirúrgico por ser mayor de 40 años
        patient_gender="F",
        hospital_name="Hospital Metropolitano",
        treating_physician="Dr. Morales",
        diagnosis_icd10="K80.2 - Calculosis de vesícula biliar",
        procedure_name="Colecistectomía laparoscópica",
        urgency=UrgencyLevel.ELECTIVA,
        request_date="2026-09-15",
        estimated_cost=2800.0,
        attachments=[
            # Falta riesgo_quirurgico y ecografia
            DocumentAttachment(name="lab.pdf", doc_type="laboratorio", is_present=True),
            DocumentAttachment(name="presupuesto.pdf", doc_type="presupuesto", is_present=True),
        ]
    )

    resolution = audit_preauthorization(report, mock_policy_oro)
    assert resolution.status == ResolutionStatus.DOCUMENTOS_FALTANTES
    assert len(resolution.missing_documents) >= 1
    doc_types_missing = [d.doc_type for d in resolution.missing_documents]
    assert "riesgo_quirurgico" in doc_types_missing
    assert "ecografia" in doc_types_missing


def test_case_beta_sequential_curing_resolves_to_approved():
    policy_silva = InsuredPolicy(
        policy_number="POL-SILVA-002",
        patient_id="1719283041",
        patient_name="Carlos Andrés Silva",
        plan_tier="Plan Plata",
        start_date="2025-07-01",  # 14 meses (carencia 10m cumplida)
        status="Activa",
        annual_deductible=200.0,
        deductible_met=200.0,
        coverage_percent_in_network=75.0,
        coverage_percent_out_network=55.0,
        network_hospitals=["Clínica Kennedy"],
        carencia_rules=[
            CarenciaRule(category="vesicula_hernias", required_months=10, description="10 meses")
        ],
        exclusions=[],
    )

    report_silva = MedicalReport(
        patient_name="Carlos Andrés Silva",
        patient_id="1719283041",
        patient_age=48,
        patient_gender="M",
        hospital_name="Clínica Kennedy",
        treating_physician="Dr. Baquerizo",
        diagnosis_icd10="K40.9 - Hernia inguinal",
        procedure_name="Hernioplastia inguinal con colocación de malla protésica",
        urgency=UrgencyLevel.ELECTIVA,
        request_date="2026-09-15",
        estimated_cost=2100.0,
        attachments=[
            DocumentAttachment(name="Presupuesto.pdf", doc_type="presupuesto", is_present=True),
            DocumentAttachment(name="Biometria.pdf", doc_type="laboratorio", is_present=True),
        ]
    )

    # Paso 1: Auditoría inicial -> DOCUMENTOS_FALTANTES (ecografía + riesgo_quirúrgico)
    res_1 = audit_preauthorization(report_silva, policy_silva)
    assert res_1.status == ResolutionStatus.DOCUMENTOS_FALTANTES
    assert len(res_1.missing_documents) == 2
    case_id = res_1.case_id

    # Paso 2: Subsanar ecografía
    report_silva.attachments.append(
        DocumentAttachment(name="Ecografia_Pared_Abdominal.pdf", doc_type="ecografia", is_present=True)
    )
    res_2 = audit_preauthorization(report_silva, policy_silva, existing_case_id=case_id)
    assert res_2.case_id == case_id
    assert res_2.status == ResolutionStatus.DOCUMENTOS_FALTANTES
    assert len(res_2.missing_documents) == 1
    assert res_2.missing_documents[0].doc_type == "riesgo_quirurgico"

    # Paso 3: Subsanar riesgo quirúrgico
    report_silva.attachments.append(
        DocumentAttachment(name="Valoracion_Cardiologica.pdf", doc_type="riesgo_quirurgico", is_present=True)
    )
    res_3 = audit_preauthorization(report_silva, policy_silva, existing_case_id=case_id)
    assert res_3.case_id == case_id
    assert res_3.status == ResolutionStatus.PRE_APROBADO
    assert len(res_3.missing_documents) == 0
    assert res_3.authorization_code == case_id

