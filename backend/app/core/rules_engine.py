import re
from datetime import datetime
from typing import Dict, List, Tuple
from app.models.clinical import MedicalReport, UrgencyLevel
from app.models.policy import InsuredPolicy
from app.models.resolution import (
    CarenciaAuditResult,
    FinancialBreakdown,
    MissingDocumentRequirement,
    PreAuthResolution,
    ResolutionStatus,
)


def _parse_date(date_str: str) -> datetime:
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return datetime.now()


def _get_required_documents(procedure_lower: str, patient_age: int) -> List[MissingDocumentRequirement]:
    requirements: List[MissingDocumentRequirement] = []

    # 1. Presupuesto detallado (requerido para toda cirugía electiva)
    requirements.append(
        MissingDocumentRequirement(
            doc_type="presupuesto",
            title="Presupuesto Quirúrgico Detallado",
            mandatory=True,
            medical_rationale="Desglose formal de honorarios médicos, derecho de quirófano, insumos y días de hospitalización.",
            suggested_action="Adjuntar proforma emitida por el departamento de admisiones o facturación del hospital.",
        )
    )

    # 2. Laboratorio prequirúrgico (Biometría y Coagulación)
    requirements.append(
        MissingDocumentRequirement(
            doc_type="laboratorio",
            title="Biometría Hemática y Tiempos de Coagulación (TP / TTP)",
            mandatory=True,
            medical_rationale="Indispensable para evaluar riesgo de sangrado intraoperatorio, recuento plaquetario y descartar anemia o infección oculta.",
            suggested_action="Adjuntar reporte de laboratorio con antigüedad no mayor a 30 días.",
        )
    )

    # 3. Reglas específicas por patología
    if any(k in procedure_lower for k in ["colecist", "vesicula", "vesícula", "biliar"]):
        requirements.append(
            MissingDocumentRequirement(
                doc_type="ecografia",
                title="Ecografía de Abdomen Superior",
                mandatory=True,
                medical_rationale="Evidencia imagenológica del cálculo o pólipo vesicular, grosor de pared y estado de vías biliares.",
                suggested_action="Subir informe ecográfico firmado por radiólogo certificado.",
            )
        )
    elif any(k in procedure_lower for k in ["hernia", "hernioplastia", "inguinal", "umbilical"]):
        requirements.append(
            MissingDocumentRequirement(
                doc_type="ecografia",
                title="Ecografía de Partes Blandas / Pared Abdominal",
                mandatory=True,
                medical_rationale="Demostración objetiva del defecto herniario y anillo fascial para justificar el uso de malla protésica.",
                suggested_action="Adjuntar estudio ecográfico de la región herniaria.",
            )
        )
    elif any(k in procedure_lower for k in ["cesarea", "cesárea", "parto", "obstetric"]):
        requirements.append(
            MissingDocumentRequirement(
                doc_type="informe_obstetrico",
                title="Informe Obstétrico con Semanas Gestacionales",
                mandatory=True,
                medical_rationale="Justificación médica de la vía de resolución de parto (cesárea) y edad gestacional fidedigna.",
                suggested_action="Subir nota del gineco-obstetra con indicación de cesárea.",
            )
        )
        requirements.append(
            MissingDocumentRequirement(
                doc_type="ecografia",
                title="Ecografía Obstétrica del 3er Trimestre",
                mandatory=True,
                medical_rationale="Estimación de biometría fetal, placenta y líquido amniótico.",
                suggested_action="Adjuntar último eco obstétrico.",
            )
        )
    elif any(k in procedure_lower for k in ["apendic", "urgencia"]):
        requirements.append(
            MissingDocumentRequirement(
                doc_type="informe_urgencia",
                title="Nota de Evolución de Emergencia / Score de Alvarado",
                mandatory=True,
                medical_rationale="Criterios clínicos de abdomen agudo quirúrgico que motivan la intervención inmediata.",
                suggested_action="Adjuntar nota de ingreso a emergencias del cirujano de guardia.",
            )
        )

    # 4. Riesgo Quirúrgico / Valoración Cardiológica (Obligatorio para mayores de 40 años)
    if patient_age >= 40:
        requirements.append(
            MissingDocumentRequirement(
                doc_type="riesgo_quirurgico",
                title="Valoración Cardiológica y Riesgo Quirúrgico (ECG)",
                mandatory=True,
                medical_rationale=f"Normativa de seguridad perioperatoria: Pacientes de {patient_age} años (>=40 años) requieren evaluación de riesgo cardiovascular según criterios ASA / Goldman.",
                suggested_action="Subir informe cardiológico prequirúrgico con electrocardiograma (ECG).",
            )
        )

    return requirements


def evaluate_carencia(report: MedicalReport, policy: InsuredPolicy) -> CarenciaAuditResult:
    start_dt = _parse_date(policy.start_date)
    req_dt = _parse_date(report.request_date)

    elapsed_days = max(0, (req_dt - start_dt).days)
    elapsed_months = round(elapsed_days / 30.4375, 1)

    proc_lower = f"{report.procedure_name} {report.diagnosis_icd10}".lower()

    # 1. ¿Es emergencia quirúrgica vital?
    is_emergency = (
        report.urgency == UrgencyLevel.EMERGENCIA_VITAL
        or any(w in proc_lower for w in ["apendic", "perforad", "trauma", "hemorragia", "shock", "obstruccion intestinal"])
    )

    if is_emergency:
        return CarenciaAuditResult(
            category_evaluated="Emergencias y Accidentes Quirúrgicos",
            required_months=0,
            elapsed_days=elapsed_days,
            elapsed_months=elapsed_months,
            is_satisfied=True,
            exception_applied="Excepción de Emergencia Quirúrgica Vital (Carencia 0 Días)",
            explanation=(
                f"El cuadro clínico ({report.procedure_name}) califica como emergencia médica vital no diferible. "
                "La póliza estipula carencia de 0 días para este diagnóstico. Cobertura inmediata concedida."
            ),
        )

    # 2. Mapeo a categorías contractuales
    required_months = 10  # Por defecto cirugías electivas
    category_name = "Cirugía Electiva General"

    if any(w in proc_lower for w in ["colecist", "vesicula", "vesícula", "hernia", "hernioplastia"]):
        required_months = 10
        category_name = "Vesícula Biliar y Hernias Abdominales"
    elif any(w in proc_lower for w in ["cesarea", "cesárea", "maternidad", "parto"]):
        required_months = 10
        category_name = "Maternidad y Parto por Cesárea"
    elif any(w in proc_lower for w in ["protesis", "prótesis", "rodilla", "cadera", "artroplastia", "columna"]):
        required_months = 18
        category_name = "Cirugías de Alta Complejidad y Ortopedia Mayor"

    # Verificar si la póliza tiene regla específica personalizada
    for rule in policy.carencia_rules:
        if rule.category.lower() in category_name.lower():
            required_months = rule.required_months

    is_satisfied = elapsed_months >= required_months

    if is_satisfied:
        explanation = (
            f"La póliza cuenta con {elapsed_months} meses de vigencia activa (antigüedad desde {policy.start_date}). "
            f"El procedimiento '{category_name}' requiere un período de carencia de {required_months} meses. Requisito CUMPLIDO satisfactoriamente."
        )
    else:
        remaining_months = round(required_months - elapsed_months, 1)
        explanation = (
            f"La póliza tiene {elapsed_months} meses de vigencia activa ({elapsed_days} días desde {policy.start_date}). "
            f"Para '{category_name}' se exige un período contractual de carencia de {required_months} meses. "
            f"Faltan {remaining_months} meses para adquirir derecho de cobertura electiva."
        )

    return CarenciaAuditResult(
        category_evaluated=category_name,
        required_months=required_months,
        elapsed_days=elapsed_days,
        elapsed_months=elapsed_months,
        is_satisfied=is_satisfied,
        explanation=explanation,
    )


def calculate_financials(report: MedicalReport, policy: InsuredPolicy) -> FinancialBreakdown:
    # Determinar si el hospital está en la red de convenios
    hosp_clean = report.hospital_name.strip().lower()
    in_network = any(net_hosp.strip().lower() in hosp_clean or hosp_clean in net_hosp.strip().lower() for net_hosp in policy.network_hospitals)

    # Si la lista de hospitales está vacía, asumir in_network
    if not policy.network_hospitals:
        in_network = True

    cov_rate = (policy.coverage_percent_in_network if in_network else policy.coverage_percent_out_network) / 100.0

    total_cost = report.estimated_cost
    deductible_left = max(0.0, policy.annual_deductible - policy.deductible_met)
    deductible_applied = min(deductible_left, total_cost)

    amount_after_deductible = max(0.0, total_cost - deductible_applied)
    insurer_pays = round(amount_after_deductible * cov_rate, 2)
    patient_copay = round(total_cost - insurer_pays, 2)

    return FinancialBreakdown(
        estimated_total=round(total_cost, 2),
        in_network=in_network,
        coverage_percent=round(cov_rate * 100, 1),
        deductible_applied=round(deductible_applied, 2),
        insurer_pays=insurer_pays,
        patient_copay=patient_copay,
        currency="USD",
    )


def audit_preauthorization(report: MedicalReport, policy: InsuredPolicy) -> PreAuthResolution:
    import uuid
    case_number = f"AUTH-2026-{uuid.uuid4().hex[:6].upper()}"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Comprobar vigencia de póliza
    if policy.status.lower() not in ["activa", "activo", "vigente"]:
        return PreAuthResolution(
            case_id=case_number,
            status=ResolutionStatus.RECHAZADO,
            patient_id=report.patient_id,
            patient_name=report.patient_name,
            policy_number=policy.policy_number,
            procedure_name=report.procedure_name,
            hospital_name=report.hospital_name,
            request_date=report.request_date,
            carencia_audit=CarenciaAuditResult(
                category_evaluated="Estado de Póliza",
                required_months=0,
                elapsed_days=0,
                elapsed_months=0.0,
                is_satisfied=False,
                explanation=f"La póliza N° {policy.policy_number} se encuentra en estado '{policy.status}', por lo que no cuenta con cobertura activa.",
            ),
            financials=FinancialBreakdown(
                estimated_total=report.estimated_cost,
                in_network=False,
                coverage_percent=0.0,
                deductible_applied=0.0,
                insurer_pays=0.0,
                patient_copay=report.estimated_cost,
            ),
            clinical_justification=f"Rechazo formal: Póliza N° {policy.policy_number} en estado {policy.status}.",
            qr_data=f"INVALID|CASE={case_number}|STATUS=REJECTED|POLICY={policy.policy_number}",
            created_at=now_str,
        )

    # 2. Evaluar carencias
    carencia_result = evaluate_carencia(report, policy)

    # 3. Comprobar exclusiones de póliza
    proc_lower = f"{report.procedure_name} {report.diagnosis_icd10}".lower()
    for excl in policy.exclusions:
        if excl.lower() in proc_lower:
            return PreAuthResolution(
                case_id=case_number,
                status=ResolutionStatus.RECHAZADO,
                patient_id=report.patient_id,
                patient_name=report.patient_name,
                policy_number=policy.policy_number,
                procedure_name=report.procedure_name,
                hospital_name=report.hospital_name,
                request_date=report.request_date,
                carencia_audit=carencia_result,
                financials=FinancialBreakdown(
                    estimated_total=report.estimated_cost,
                    in_network=False,
                    coverage_percent=0.0,
                    deductible_applied=0.0,
                    insurer_pays=0.0,
                    patient_copay=report.estimated_cost,
                ),
                clinical_justification=f"Procedimiento expresamente excluido según cláusula contractual: '{excl}'.",
                qr_data=f"EXCLUDED|CASE={case_number}|STATUS=REJECTED",
                created_at=now_str,
            )

    # Si la carencia no se cumple, se rechaza fundamentadamente
    if not carencia_result.is_satisfied:
        return PreAuthResolution(
            case_id=case_number,
            status=ResolutionStatus.RECHAZADO,
            patient_id=report.patient_id,
            patient_name=report.patient_name,
            policy_number=policy.policy_number,
            procedure_name=report.procedure_name,
            hospital_name=report.hospital_name,
            request_date=report.request_date,
            carencia_audit=carencia_result,
            financials=FinancialBreakdown(
                estimated_total=report.estimated_cost,
                in_network=False,
                coverage_percent=0.0,
                deductible_applied=0.0,
                insurer_pays=0.0,
                patient_copay=report.estimated_cost,
            ),
            clinical_justification=carencia_result.explanation,
            qr_data=f"CARENCIA_FAIL|CASE={case_number}|REQ={carencia_result.required_months}M|ACTUAL={carencia_result.elapsed_months}M",
            created_at=now_str,
        )

    # 4. Auditoría de Documentos Obligatorios
    required_docs = _get_required_documents(proc_lower, report.patient_age)
    present_doc_types = {att.doc_type.lower() for att in report.attachments if att.is_present}

    missing_docs: List[MissingDocumentRequirement] = []
    for req in required_docs:
        if req.mandatory and req.doc_type.lower() not in present_doc_types:
            missing_docs.append(req)

    # Calcular desglose financiero
    financials = calculate_financials(report, policy)

    # 5. Emisión de Resolución
    if missing_docs:
        status_eval = ResolutionStatus.DOCUMENTOS_FALTANTES
        auth_code = None
        clinical_justification = (
            f"El procedimiento '{report.procedure_name}' está amparado y el paciente cumple con los requisitos de carencia ({carencia_result.elapsed_months} meses vigentes). "
            f"Sin embargo, para emitir la pre-aprobación definitiva se requiere subsanar {len(missing_docs)} documento(s) clínico(s) indispensable(s)."
        )
        qr_data = f"PENDING_DOCS|CASE={case_number}|COUNT={len(missing_docs)}"
    else:
        status_eval = ResolutionStatus.PRE_APROBADO
        auth_code = case_number
        clinical_justification = (
            f"Pre-aprobación quirúrgica concedida. El paciente cumple la carencia contractual requerida ({carencia_result.elapsed_months} meses vs {carencia_result.required_months} meses exigidos). "
            f"Toda la documentación y pruebas prequirúrgicas han sido auditadas conforme a la norma técnica médica. "
            f"Cobertura autorizada al {financials.coverage_percent}% en {report.hospital_name}."
        )
        qr_data = f"APPROVED|CODE={auth_code}|PATIENT={report.patient_id}|PROC={report.procedure_name}|COV={financials.insurer_pays}USD"

    return PreAuthResolution(
        case_id=case_number,
        status=status_eval,
        patient_id=report.patient_id,
        patient_name=report.patient_name,
        policy_number=policy.policy_number,
        procedure_name=report.procedure_name,
        hospital_name=report.hospital_name,
        request_date=report.request_date,
        carencia_audit=carencia_result,
        financials=financials,
        missing_documents=missing_docs,
        clinical_justification=clinical_justification,
        authorization_code=auth_code,
        qr_data=qr_data,
        created_at=now_str,
    )
