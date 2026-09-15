import os
import shutil
import zipfile
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = BASE_DIR / "frontend" / "public" / "case_packages"
PUBLIC_SAMPLE_DIR = BASE_DIR / "frontend" / "public" / "sample_reports"

styles = getSampleStyleSheet()

# Estilos personalizados
header_title_style = ParagraphStyle(
    "HeaderTitle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=14,
    textColor=colors.HexColor("#0f172a"),
    leading=18,
    alignment=1,
)
header_sub_style = ParagraphStyle(
    "HeaderSub",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=9,
    textColor=colors.HexColor("#475569"),
    leading=12,
    alignment=1,
)
section_heading_style = ParagraphStyle(
    "SectionHeading",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=11,
    textColor=colors.HexColor("#0369a1"),
    leading=14,
    spaceAfter=4,
)
body_bold_style = ParagraphStyle(
    "BodyBold",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=9,
    textColor=colors.HexColor("#1e293b"),
    leading=13,
)
body_text_style = ParagraphStyle(
    "BodyText",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=9,
    textColor=colors.HexColor("#334155"),
    leading=13,
)
footer_style = ParagraphStyle(
    "FooterStyle",
    parent=styles["Normal"],
    fontName="Helvetica-Oblique",
    fontSize=8,
    textColor=colors.HexColor("#64748b"),
    leading=11,
    alignment=1,
)


def create_header(doc_title: str, institution: str = "HOSPITAL METROPOLITANO DE GUAYAQUIL", dept: str = "DEPARTAMENTO DE ADMISIONES Y AUDITORÍA MÉDICA"):
    elements = [
        Paragraph(institution, header_title_style),
        Paragraph(dept, header_sub_style),
        Paragraph(f"<b>DOCUMENTO:</b> {doc_title.upper()} | FECHA: 2026-09-15", header_sub_style),
        Spacer(1, 6),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=10),
    ]
    return elements


def create_patient_box(patient_data: dict):
    table_data = [
        [
            Paragraph(f"<b>Paciente:</b> {patient_data['name']}", body_text_style),
            Paragraph(f"<b>Cédula / ID:</b> {patient_data['id']}", body_text_style),
        ],
        [
            Paragraph(f"<b>Edad / Sexo:</b> {patient_data['age']} años | {patient_data['gender']}", body_text_style),
            Paragraph(f"<b>Póliza N°:</b> {patient_data['policy']}", body_text_style),
        ],
        [
            Paragraph(f"<b>Médico Solicitante:</b> {patient_data['doctor']}", body_text_style),
            Paragraph(f"<b>Institución:</b> {patient_data['hospital']}", body_text_style),
        ],
    ]
    t = Table(table_data, colWidths=[270, 270])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    return [t, Spacer(1, 10)]


# --- Generador 1: Informe Quirúrgico Principal ---
def generate_clinical_report(path: Path, patient: dict, case_info: dict):
    doc = SimpleDocTemplate(str(path), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story = create_header("Informe Médico de Solicitud Quirúrgica", patient["hospital"])
    story.extend(create_patient_box(patient))

    # Diagnóstico y Procedimiento
    diag_data = [
        [Paragraph("<b>DIAGNÓSTICO CIE-10:</b>", body_bold_style), Paragraph(case_info["diagnosis_icd10"], body_text_style)],
        [Paragraph("<b>PROCEDIMIENTO:</b>", body_bold_style), Paragraph(f"{case_info['procedure_name']} (CPT: {case_info.get('cpt', 'N/A')})", body_text_style)],
        [Paragraph("<b>PRIORIDAD QUIRÚRGICA:</b>", body_bold_style), Paragraph(case_info["urgency"], body_bold_style)],
        [Paragraph("<b>PRESUPUESTO ESTIMADO:</b>", body_bold_style), Paragraph(f"USD ${case_info['cost']:,.2f}", body_bold_style)],
    ]
    diag_table = Table(diag_data, colWidths=[160, 380])
    diag_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(diag_table)
    story.append(Spacer(1, 10))

    # Resumen Clínico
    story.append(Paragraph("RESUMEN CLÍNICO Y CRITERIO DE INTERVENCIÓN", section_heading_style))
    story.append(Paragraph(case_info["clinical_summary"], body_text_style))
    story.append(Spacer(1, 10))

    # Estudios Adjuntos
    story.append(Paragraph("DOCUMENTACIÓN Y ESTUDIOS ADJUNTOS EN EXPEDIENTE:", section_heading_style))
    for idx, doc_item in enumerate(case_info["docs_attached"], start=1):
        story.append(Paragraph(f"<b>{idx}. {doc_item['name']}</b>: {doc_item['detail']}", body_text_style))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94a3b8"), spaceAfter=8))
    
    # Firmas
    sig_data = [
        [
            Paragraph(f"<b>{patient['doctor']}</b><br/>Cirujano Tratante - Reg. Senescyt 1008-2015-8941<br/>Firma y Sello Hospitalario", footer_style),
            Paragraph("<b>Dr. Roberto Carrera V.</b><br/>Director de Auditoría Médica Hospitalaria<br/>Aprobación de Admisión", footer_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[270, 270])
    story.append(sig_table)
    doc.build(story)


# --- Generador 2: Certificado de Póliza de Salud (Notion Insurance Bridge) ---
def generate_policy_certificate(path: Path, patient: dict, policy_data: dict):
    doc = SimpleDocTemplate(str(path), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story = create_header("Certificado Individual de Póliza de Asistencia Médica", "VIAMATICA SEGUROS & SALUD S.A.", "DIVISIÓN NACIONAL DE EMISIONES Y SUSCRIPCIÓN")
    
    # Datos póliza
    pol_info = [
        [Paragraph(f"<b>Titular / Asegurado:</b> {patient['name']}", body_text_style), Paragraph(f"<b>Cédula:</b> {patient['id']}", body_text_style)],
        [Paragraph(f"<b>Póliza N°:</b> {policy_data['policy_number']}", body_text_style), Paragraph(f"<b>Plan:</b> {policy_data['plan_name']}", body_bold_style)],
        [Paragraph(f"<b>Inicio de Vigencia:</b> {policy_data['start_date']}", body_text_style), Paragraph(f"<b>Estado:</b> <font color='green'><b>VIGENTE Y ACTIVA</b></font>", body_text_style)],
        [Paragraph(f"<b>Antigüedad Acumulada:</b> <b>{policy_data['months_active']} meses</b>", body_bold_style), Paragraph(f"<b>Límite Anual Máximo:</b> USD ${policy_data['max_limit']:,}", body_text_style)],
    ]
    t = Table(pol_info, colWidths=[270, 270])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # Reglas y Carencias
    story.append(Paragraph("CUADRO OFICIAL DE CONDICIONES Y PERÍODOS DE CARENCIA", section_heading_style))
    carencias_table_data = [
        [Paragraph("<b>Cobertura / Procedimiento</b>", body_bold_style), Paragraph("<b>Carencia Requerida</b>", body_bold_style), Paragraph("<b>Estado del Paciente</b>", body_bold_style), Paragraph("<b>Copago Asegurado</b>", body_bold_style)],
        [Paragraph("Cirugía General y Laparoscopía", body_text_style), Paragraph("10 meses", body_text_style), Paragraph(f"{policy_data['months_active']} meses cumplidos", body_text_style), Paragraph("20% (Cobertura 80%)", body_text_style)],
        [Paragraph("Maternidad y Parto / Cesárea", body_text_style), Paragraph("10 meses", body_text_style), Paragraph("10 meses requeridos", body_text_style), Paragraph("20% (Cobertura 80%)", body_text_style)],
        [Paragraph("Emergencias Médicas / Urgencia Vital", body_text_style), Paragraph("0 DÍAS (Inmediata)", body_bold_style), Paragraph("Aplica sin carencia", body_bold_style), Paragraph("0% a 20% según convenio", body_text_style)],
        [Paragraph("Deducible Anual no Hospitalario", body_text_style), Paragraph("N/A", body_text_style), Paragraph("USD $500.00 anual", body_text_style), Paragraph("Pagado al 100%", body_text_style)],
    ]
    ct = Table(carencias_table_data, colWidths=[180, 110, 130, 120])
    ct.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0284c7")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(ct)
    story.append(Spacer(1, 10))

    story.append(Paragraph("CLÁUSULAS ESPECIALES Y PROTOCOLO DE PRE-AUTORIZACIÓN", section_heading_style))
    clauses = [
        "1. <b>Pre-autorización Obligatoria:</b> Todo procedimiento quirúrgico electivo requiere informe médico formal y estudios diagnósticos aprobados antes del ingreso.",
        "2. <b>Excepción de Urgencia Vital:</b> Procedimientos calificados como Emergencia Vital (CIE-10 urgente) serán pre-autorizados inmediatamente con 0 carencia.",
        "3. <b>Liquidación y Copago:</b> La cobertura estándar cubre el 80% de gastos hospitalarios y honorarios médicos en red de clínicas asociadas.",
    ]
    for c in clauses:
        story.append(Paragraph(c, body_text_style))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 20))
    story.append(Paragraph("Certificado emitido electrónicamente por el Sistema de Suscripción AuraQx con sincronización en Notion.", footer_style))
    doc.build(story)


# --- Generador 3: Ecografía / Estudio de Imagen ---
def generate_imaging_report(path: Path, patient: dict, study_data: dict):
    doc = SimpleDocTemplate(str(path), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story = create_header(f"Informe de Radiología e Imágenes: {study_data['title']}", patient["hospital"], "SERVICIO DE DIAGNÓSTICO POR IMÁGENES")
    story.extend(create_patient_box(patient))

    story.append(Paragraph(f"TÉCNICA DE ESTUDIO: {study_data['technique']}", section_heading_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("HALLAZGOS ECOGRÁFICOS / RADIOLÓGICOS:", section_heading_style))
    for item in study_data["findings"]:
        story.append(Paragraph(f"• {item}", body_text_style))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 8))
    conclusion_data = [
        [Paragraph("<b>IMPRESIÓN DIAGNÓSTICA / CONCLUSIÓN:</b>", body_bold_style)],
        [Paragraph(study_data["conclusion"], body_bold_style)],
    ]
    concl_table = Table(conclusion_data, colWidths=[540])
    concl_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor("#22c55e")),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(concl_table)
    story.append(Spacer(1, 25))

    sig_data = [
        [
            Paragraph(f"<b>Dra. Patricia Andrade G.</b><br/>Especialista en Imagenología Médica<br/>Reg. 0910-2018-4412", footer_style),
            Paragraph("<b>Equipo Radiológico:</b> GE Healthcare Voluson Expert E10<br/>Estudio digital verificado", footer_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[270, 270])
    story.append(sig_table)
    doc.build(story)


# --- Generador 4: Biometría y Pruebas de Laboratorio ---
def generate_lab_report(path: Path, patient: dict, lab_tests: list):
    doc = SimpleDocTemplate(str(path), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story = create_header("Reporte de Laboratorio Clínico y Coagulación", patient["hospital"], "LABORATORIO CLÍNICO Y BIOMOLECULAR AUTOMATIZADO")
    story.extend(create_patient_box(patient))

    story.append(Paragraph("RESULTADOS DE PRUEBAS PRE-QUIRÚRGICAS:", section_heading_style))
    table_data = [
        [
            Paragraph("<b>Prueba / Parámetro</b>", body_bold_style),
            Paragraph("<b>Resultado</b>", body_bold_style),
            Paragraph("<b>Unidad</b>", body_bold_style),
            Paragraph("<b>Rango de Referencia</b>", body_bold_style),
            Paragraph("<b>Estado</b>", body_bold_style),
        ]
    ]
    for row in lab_tests:
        table_data.append([
            Paragraph(row["test"], body_text_style),
            Paragraph(f"<b>{row['val']}</b>", body_text_style),
            Paragraph(row["unit"], body_text_style),
            Paragraph(row["ref"], body_text_style),
            Paragraph(row["status"], body_bold_style),
        ])

    lab_table = Table(table_data, colWidths=[160, 90, 80, 130, 80])
    lab_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(lab_table)
    story.append(Spacer(1, 20))

    sig_data = [
        [
            Paragraph(f"<b>Lic. Lorena Valenzuela M.</b><br/>Bioquímica Farmacéutica - Reg. 1290-2016-11<br/>Analizador Cobas 6000 / Sysmex XN", footer_style),
            Paragraph("<b>Muestra:</b> Sangre Total con EDTA + Citrato de Sodio<br/>Validación técnica completada", footer_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[270, 270])
    story.append(sig_table)
    doc.build(story)


# --- Generador 5: Valoración Cardiológica (Riesgo Quirúrgico) ---
def generate_cardiac_clearance(path: Path, patient: dict, risk_data: dict):
    doc = SimpleDocTemplate(str(path), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story = create_header("Valoración Cardiológica y Riesgo Quirúrgico", patient["hospital"], "SERVICIO DE CARDIOLOGÍA CLÍNICA")
    story.extend(create_patient_box(patient))

    story.append(Paragraph("EVALUACIÓN CLÍNICA Y ELECTROCARDIOGRAMA:", section_heading_style))
    eval_data = [
        [Paragraph("<b>Presión Arterial:</b>", body_bold_style), Paragraph(risk_data["bp"], body_text_style)],
        [Paragraph("<b>Frecuencia Cardíaca:</b>", body_bold_style), Paragraph(risk_data["hr"], body_text_style)],
        [Paragraph("<b>Electrocardiograma (ECG):</b>", body_bold_style), Paragraph(risk_data["ecg"], body_text_style)],
        [Paragraph("<b>Antecedentes Cardiovasculares:</b>", body_bold_style), Paragraph(risk_data["history"], body_text_style)],
    ]
    eval_table = Table(eval_data, colWidths=[180, 360])
    eval_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(eval_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("ESTRATIFICACIÓN DE RIESGO CARDIOVASCULAR:", section_heading_style))
    score_box = [
        [Paragraph(f"<b>CLASIFICACIÓN DE GOLDMAN:</b> {risk_data['goldman_class']}", body_bold_style)],
        [Paragraph(f"<b>RIESGO ESTIMADO:</b> {risk_data['risk_level']} (Complicación cardiovascular estimada < 1%)", body_text_style)],
        [Paragraph(f"<b>CONCLUSIÓN:</b> {risk_data['recommendation']}", body_bold_style)],
    ]
    st = Table(score_box, colWidths=[540])
    st.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor("#3b82f6")),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(st)
    story.append(Spacer(1, 20))

    sig_data = [
        [
            Paragraph(f"<b>Dr. Xavier Moncayo H.</b><br/>Especialista en Cardiología e Intervencionismo<br/>Reg. Senescyt 0904-2012-7712", footer_style),
            Paragraph("<b>Monitoreo intraoperatorio sugerido:</b> Tipo I estándar<br/>Sin contraindicación cardiovascular", footer_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[270, 270])
    story.append(sig_table)
    doc.build(story)


# --- Generador 6: Presupuesto Quirúrgico Hospitalario ---
def generate_budget_breakdown(path: Path, patient: dict, budget_data: dict):
    doc = SimpleDocTemplate(str(path), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story = create_header("Presupuesto Quirúrgico y Proforma Hospitalaria", patient["hospital"], "DEPARTAMENTO DE COSTOS Y FACTURACIÓN MÉDICA")
    story.extend(create_patient_box(patient))

    story.append(Paragraph(f"PROCEDIMIENTO PRESUPUESTADO: {budget_data['procedure']}", section_heading_style))
    
    table_data = [
        [
            Paragraph("<b>Rubro / Concepto Hospitalario</b>", body_bold_style),
            Paragraph("<b>Detalle de Cobertura</b>", body_bold_style),
            Paragraph("<b>Valor (USD)</b>", body_bold_style),
        ]
    ]
    for item in budget_data["items"]:
        table_data.append([
            Paragraph(item["concept"], body_text_style),
            Paragraph(item["desc"], body_text_style),
            Paragraph(f"${item['val']:,.2f}", body_text_style),
        ])
    
    table_data.append([
        Paragraph("<b>TOTAL ESTIMADO DE LA INTERVENCIÓN:</b>", body_bold_style),
        Paragraph("<b>Paquete Quirúrgico Integral</b>", body_bold_style),
        Paragraph(f"<b>${budget_data['total']:,.2f}</b>", body_bold_style),
    ])

    bt = Table(table_data, colWidths=[200, 240, 100])
    bt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#e2e8f0")),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(bt)
    story.append(Spacer(1, 15))

    story.append(Paragraph("CONDICIONES DEL PRESUPUESTO:", section_heading_style))
    terms = [
        "• Validez de la proforma: 30 días a partir de la emisión.",
        "• Incluye derechos de quirófano con torre de laparoscopía, estancia hospitalaria estándar (1 día) y honorarios profesionales.",
        "• Sujeto a la cobertura de la póliza de seguros y copago del afiliado.",
    ]
    for t in terms:
        story.append(Paragraph(t, body_text_style))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 20))
    doc.build(story)


def create_all_packages():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

    print("🚀 Generando paquetes descargables de documentos clínicos para cada caso...")

    # =========================================================================
    # CASO ALFA: Colecistectomía Laparoscópica (Pre-Aprobación Exitosa)
    # =========================================================================
    case_alfa_dir = OUTPUT_DIR / "case-alfa"
    case_alfa_dir.mkdir(exist_ok=True)

    p_alfa = {
        "name": "María Carmen Mendoza",
        "id": "0928374102",
        "age": 45,
        "gender": "Femenino",
        "policy": "POL-2024-8831",
        "doctor": "Dr. Fernando Morales (Cirugía Laparoscópica)",
        "hospital": "Hospital Metropolitano",
    }

    # 1. Informe Clínico
    generate_clinical_report(
        case_alfa_dir / "01_Informe_Quirurgico_Colecistectomia.pdf",
        p_alfa,
        {
            "diagnosis_icd10": "K80.2 - Calculosis de la vesícula biliar sin colecistitis",
            "procedure_name": "Colecistectomía laparoscópica",
            "cpt": "47562",
            "urgency": "ELECTIVA PROGRAMADA",
            "cost": 2800.0,
            "clinical_summary": "Paciente con cuadro de dolor en hipocondrio derecho postprandial de 4 meses de evolución. Ecografía evidencia múltiples litos vesiculares de 6 a 8 mm con pared fina de 2 mm. Vía biliar normal de 4 mm. Se indica colecistectomía programada.",
            "docs_attached": [
                {"name": "Ecografía Abdominal", "detail": "Colelitiasis múltiple sin colecistitis aguda."},
                {"name": "Biometría y Coagulación", "detail": "Hemograma, TP 11.8s (100%), TTP 29s normales."},
                {"name": "Riesgo Cardiológico", "detail": "ECG ritmo sinusal, Goldman Clase I (Bajo)."},
                {"name": "Presupuesto Quirúrgico", "detail": "Proforma paquete laparoscópico USD $2,800.00."},
            ]
        }
    )
    # Copiar también al sample_reports para compatibilidad
    shutil.copy(case_alfa_dir / "01_Informe_Quirurgico_Colecistectomia.pdf", PUBLIC_SAMPLE_DIR / "informe_colecistectomia_aprobado.pdf")

    # 2. Póliza de Seguro
    generate_policy_certificate(
        case_alfa_dir / "02_Certificado_Poliza_Asegurado.pdf",
        p_alfa,
        {
            "policy_number": "POL-2024-8831",
            "plan_name": "Plan Platinum Global Corporativo",
            "start_date": "2024-03-10",
            "months_active": 18,
            "max_limit": 50000,
        }
    )

    # 3. Ecografía
    generate_imaging_report(
        case_alfa_dir / "03_Ecografia_Abdominal.pdf",
        p_alfa,
        {
            "title": "Ecografía Hepatobiliar y Abdominal Superior",
            "technique": "Transductor convexo multifrecuencia 3.5 - 5.0 MHz en tiempo real.",
            "findings": [
                "Hígado de tamaño, morfología y ecogenicidad habitual, sin lesiones focales.",
                "Vesícula biliar distendida, de paredes finas y regulares (2.1 mm).",
                "En su luz se aprecian múltiples imágenes hiperecogénicas móviles de 6 a 8 mm con sombra acústica posterior neta.",
                "Colédoco de calibre normal (3.8 mm) sin evidencia de litos intraluminales.",
                "Páncreas y bazo sin alteraciones ecográficas demostrables.",
            ],
            "conclusion": "COLELITIASIS MÚLTIPLE SIN SIGNOS DE COLECISTITIS AGUDA NI DILATACIÓN DE LA VÍA BILIAR.",
        }
    )

    # 4. Laboratorio
    generate_lab_report(
        case_alfa_dir / "04_Biometria_y_Coagulacion.pdf",
        p_alfa,
        [
            {"test": "Leucocitos Totales", "val": "7,450", "unit": "/uL", "ref": "4,500 - 10,000", "status": "Normal"},
            {"test": "Hemoglobina", "val": "13.8", "unit": "g/dL", "ref": "12.0 - 15.5", "status": "Normal"},
            {"test": "Hematocrito", "val": "41.2", "unit": "%", "ref": "36.0 - 46.0", "status": "Normal"},
            {"test": "Plaquetas", "val": "242,000", "unit": "/uL", "ref": "150,000 - 450,000", "status": "Normal"},
            {"test": "Tiempo de Protrombina (TP)", "val": "11.8", "unit": "seg", "ref": "11.0 - 13.5", "status": "Normal (100%)"},
            {"test": "Tiempo Parcial Tromboplastina (TTP)", "val": "29.4", "unit": "seg", "ref": "25.0 - 35.0", "status": "Normal"},
            {"test": "Glucosa Basal", "val": "88", "unit": "mg/dL", "ref": "70 - 100", "status": "Normal"},
            {"test": "Creatinina Sérica", "val": "0.78", "unit": "mg/dL", "ref": "0.6 - 1.1", "status": "Normal"},
        ]
    )

    # 5. Riesgo Cardiológico
    generate_cardiac_clearance(
        case_alfa_dir / "05_Valoracion_Cardiologica_Riesgo_Quirurgico.pdf",
        p_alfa,
        {
            "bp": "120/75 mmHg",
            "hr": "68 lpm",
            "ecg": "Ritmo sinusal normal, eje QRS +60°, intervalos PR y QT dentro de límites normales, sin alteraciones de repolarización.",
            "history": "Sin antecedentes de hipertensión, diabetes ni cardiopatía coronaria previa.",
            "goldman_class": "CLASE I (0 a 5 puntos)",
            "risk_level": "BAJO RIESGO CARDIOVASCULAR",
            "recommendation": "Paciente apta para colecistectomía laparoscópica bajo anestesia general. Monitoreo habitual.",
        }
    )

    # 6. Presupuesto
    generate_budget_breakdown(
        case_alfa_dir / "06_Presupuesto_Hospitalario_Detallado.pdf",
        p_alfa,
        {
            "procedure": "Colecistectomía Laparoscópica (Paquete Todo Incluido)",
            "items": [
                {"concept": "Derechos de Quirófano y Torre Laparoscópica", "desc": "2 horas de sala de operaciones + instrumental HD", "val": 950.0},
                {"concept": "Honorarios Equipo Quirúrgico", "desc": "Cirujano Principal y Primer Ayudante", "val": 1100.0},
                {"concept": "Honorarios Anestesiología", "desc": "Médico Anestesiólogo y monitorización", "val": 350.0},
                {"concept": "Medicamentos e Insumos Transquirúrgicos", "desc": "Clips de titanio, trocar, suturas, anestésicos", "val": 250.0},
                {"concept": "Habitación y Cuidados de Enfermería", "desc": "1 noche de hospitalización en suite estándar", "val": 150.0},
            ],
            "total": 2800.0,
        }
    )

    # =========================================================================
    # CASO BETA: Hernioplastia Inguinal (Documentos Faltantes)
    # =========================================================================
    case_beta_dir = OUTPUT_DIR / "case-beta"
    case_beta_dir.mkdir(exist_ok=True)

    p_beta = {
        "name": "Carlos Andrés Silva",
        "id": "1719283041",
        "age": 48,
        "gender": "Masculino",
        "policy": "POL-2025-4420",
        "doctor": "Dr. Roberto Baquerizo (Cirugía General)",
        "hospital": "Clínica Kennedy",
    }

    # 1. Informe Clínico (con faltantes)
    generate_clinical_report(
        case_beta_dir / "01_Informe_Quirurgico_Hernioplastia.pdf",
        p_beta,
        {
            "diagnosis_icd10": "K40.9 - Hernia inguinal unilateral no especificada, sin obstrucción ni gangrena",
            "procedure_name": "Hernioplastia inguinal con colocación de malla protésica",
            "cpt": "49505",
            "urgency": "ELECTIVA PROGRAMADA",
            "cost": 2100.0,
            "clinical_summary": "Paciente masculino de 48 años refiere tumoración inguinal derecha reducible con maniobras de Valsalva de 6 meses de evolución. Examen físico compatible con hernia indirecta reducible. Se solicita pre-autorización para reparación con malla de polipropileno.",
            "docs_attached": [
                {"name": "Presupuesto Quirúrgico", "detail": "USD $2,100 incluye malla protésica y derechos de sala."},
                {"name": "Biometría Hemática", "detail": "Leucocitos 7,200, Plaquetas 210,000 dentro de rango."},
            ]
        }
    )
    shutil.copy(case_beta_dir / "01_Informe_Quirurgico_Hernioplastia.pdf", PUBLIC_SAMPLE_DIR / "informe_hernioplastia_faltantes.pdf")

    # 2. Póliza
    generate_policy_certificate(
        case_beta_dir / "02_Certificado_Poliza_Asegurado.pdf",
        p_beta,
        {
            "policy_number": "POL-2025-4420",
            "plan_name": "Plan Gold Plus",
            "start_date": "2024-07-01",
            "months_active": 14,
            "max_limit": 40000,
        }
    )

    # 3. Laboratorio
    generate_lab_report(
        case_beta_dir / "03_Biometria_Hematica.pdf",
        p_beta,
        [
            {"test": "Leucocitos Totales", "val": "7,200", "unit": "/uL", "ref": "4,500 - 10,000", "status": "Normal"},
            {"test": "Hemoglobina", "val": "14.9", "unit": "g/dL", "ref": "13.5 - 17.5", "status": "Normal"},
            {"test": "Hematocrito", "val": "44.5", "unit": "%", "ref": "41.0 - 50.0", "status": "Normal"},
            {"test": "Plaquetas", "val": "210,000", "unit": "/uL", "ref": "150,000 - 450,000", "status": "Normal"},
            {"test": "Tiempo de Protrombina (TP)", "val": "12.1", "unit": "seg", "ref": "11.0 - 13.5", "status": "Normal"},
        ]
    )

    # 4. Presupuesto
    generate_budget_breakdown(
        case_beta_dir / "04_Presupuesto_Quirurgico.pdf",
        p_beta,
        {
            "procedure": "Hernioplastia Inguinal con Malla de Polipropileno",
            "items": [
                {"concept": "Derechos de Quirófano y Anestesia", "desc": "1.5 horas de sala de operaciones", "val": 750.0},
                {"concept": "Honorarios Cirujano y Ayudantía", "desc": "Dr. Roberto Baquerizo", "val": 850.0},
                {"concept": "Malla Quirúrgica de Polipropileno y Suturas", "desc": "Malla 15x15 cm + fijación", "val": 350.0},
                {"concept": "Recuperación Postanestésica", "desc": "Cuidado ambulatorio (alta mismo día)", "val": 150.0},
            ],
            "total": 2100.0,
        }
    )

    # 5. DOCUMENTO FALTANTE PARA SUBSANAR (Prueba Interactiva)
    generate_cardiac_clearance(
        case_beta_dir / "05_FALTANTE_A_SUBIR_Riesgo_Cardiologico_Silva.pdf",
        p_beta,
        {
            "bp": "125/80 mmHg",
            "hr": "72 lpm",
            "ecg": "Ritmo sinusal regular a 72 lpm. Sin signos de isquemia miocárdica ni bloqueos.",
            "history": "Paciente masculino de 48 años sin antecedentes patológicos cardiovasculares.",
            "goldman_class": "CLASE I (0 a 5 puntos)",
            "risk_level": "BAJO RIESGO QUIRÚRGICO",
            "recommendation": "Apto para hernioplastia inguinal bajo anestesia raquídea o general.",
        }
    )

    # =========================================================================
    # CASO GAMMA: Parto por Cesárea (Carencia Insuficiente)
    # =========================================================================
    case_gamma_dir = OUTPUT_DIR / "case-gamma"
    case_gamma_dir.mkdir(exist_ok=True)

    p_gamma = {
        "name": "Valeria Sofía Ramos",
        "id": "0911223344",
        "age": 29,
        "gender": "Femenino",
        "policy": "POL-2026-1192",
        "doctor": "Dra. Cecilia Alvear (Ginecología y Obstetricia)",
        "hospital": "Hospital Metropolitano",
    }

    # 1. Informe Clínico
    generate_clinical_report(
        case_gamma_dir / "01_Informe_Obstetrico_Cesarea.pdf",
        p_gamma,
        {
            "diagnosis_icd10": "O82 - Parto único por cesárea",
            "procedure_name": "Cesárea electiva con salpingectomía o monitorización neonatal",
            "cpt": "59510",
            "urgency": "ELECTIVA PROGRAMADA",
            "cost": 3200.0,
            "clinical_summary": "Gestante primigesta de 38.4 semanas de gestación con estrechez pélvica demostrada clínicamente y feto en presentación podálica confirmada por ecografía. Se programa cesárea electiva para salvaguardar bienestar materno-fetal.",
            "docs_attached": [
                {"name": "Informe Obstétrico", "detail": "Indicación por Desproporción Céfalo-Pélvica (DCP)."},
                {"name": "Ecografía Obstétrica 3T", "detail": "Presentación podálica, placenta fúndica posterior."},
                {"name": "Laboratorio Prequirúrgico", "detail": "Hemograma completo, tiempos de coagulación y tipificación sanguínea."},
                {"name": "Presupuesto de Maternidad", "detail": "USD $3,200.00 incluye derechos de nursery y atención neonatal."},
            ]
        }
    )
    shutil.copy(case_gamma_dir / "01_Informe_Obstetrico_Cesarea.pdf", PUBLIC_SAMPLE_DIR / "informe_cesarea_carencia.pdf")

    # 2. Póliza (Carencia reciente: 4 meses)
    generate_policy_certificate(
        case_gamma_dir / "02_Certificado_Poliza_Asegurado.pdf",
        p_gamma,
        {
            "policy_number": "POL-2026-1192",
            "plan_name": "Plan Silver Care Maternity",
            "start_date": "2026-05-15",
            "months_active": 4,
            "max_limit": 30000,
        }
    )

    # 3. Ecografía Obstétrica
    generate_imaging_report(
        case_gamma_dir / "03_Ecografia_Obstetrica_Tercer_Trimestre.pdf",
        p_gamma,
        {
            "title": "Ecografía Obstétrica del Tercer Trimestre y Biometría Fetal",
            "technique": "Transabdominal con sonda volumétrica 3D/4D.",
            "findings": [
                "Feto único vivo, situación longitudinal, presentación PODÁLICA (pelviana).",
                "Diámetro biparietal (DBP) 93 mm, Longitud femoral (LF) 73 mm (Acorde a 38 semanas).",
                "Peso fetal estimado por Hadlock: 3,250 gramos (+/- 200g).",
                "Líquido amniótico de volumen normal (ILA: 13.5 cm). Placenta grado II sin calcificaciones patológicas.",
            ],
            "conclusion": "GESTACIÓN ÚNICA DE 38.4 SEMANAS EN PRESENTACIÓN PODÁLICA. CRITERIO DE RESOLUCIÓN POR CESÁREA.",
        }
    )

    # 4. Laboratorio
    generate_lab_report(
        case_gamma_dir / "04_Laboratorios_Prequirurgicos.pdf",
        p_gamma,
        [
            {"test": "Hemoglobina", "val": "12.4", "unit": "g/dL", "ref": "11.5 - 15.0", "status": "Normal"},
            {"test": "Plaquetas", "val": "235,000", "unit": "/uL", "ref": "150,000 - 450,000", "status": "Normal"},
            {"test": "Grupo y Factor Rh", "val": "O Positivo", "unit": "N/A", "ref": "A/B/AB/O", "status": "Confirmado"},
            {"test": "Tiempo de Protrombina (TP)", "val": "11.6", "unit": "seg", "ref": "11.0 - 13.5", "status": "Normal"},
            {"test": "Serología VDRL / VIH", "val": "NO REACTIVO", "unit": "N/A", "ref": "No reactivo", "status": "Negativo"},
        ]
    )

    # 5. Presupuesto Maternidad
    generate_budget_breakdown(
        case_gamma_dir / "05_Presupuesto_Maternidad.pdf",
        p_gamma,
        {
            "procedure": "Paquete Integral de Maternidad y Parto por Cesárea",
            "items": [
                {"concept": "Quirófano Obstétrico y Neonatal", "desc": "Sala de cirugía + cuna térmica", "val": 1100.0},
                {"concept": "Honorarios Gineco-Obstetra", "desc": "Dra. Cecilia Alvear", "val": 1150.0},
                {"concept": "Honorarios Pediatra Neonatólogo", "desc": "Recepción y adaptación de recién nacido", "val": 400.0},
                {"concept": "Anestesia Obstétrica", "desc": "Bloqueo peridural continuo", "val": 350.0},
                {"concept": "Hospitalización Materno-Infantil", "desc": "2 días en suite privada", "val": 200.0},
            ],
            "total": 3200.0,
        }
    )

    # =========================================================================
    # CASO DELTA: Apendicectomía de Urgencia Vital (Carencia 0 Días)
    # =========================================================================
    case_delta_dir = OUTPUT_DIR / "case-delta"
    case_delta_dir.mkdir(exist_ok=True)

    p_delta = {
        "name": "Juan Diego Morales",
        "id": "1705544332",
        "age": 34,
        "gender": "Masculino",
        "policy": "POL-2026-9901",
        "doctor": "Dr. Marcelo Pazmiño (Cirujano de Emergencias)",
        "hospital": "Hospital Metropolitano",
    }

    # 1. Nota de Ingreso de Urgencia
    generate_clinical_report(
        case_delta_dir / "01_Nota_Ingreso_Emergencia_Apendicectomia.pdf",
        p_delta,
        {
            "diagnosis_icd10": "K35.2 - Apendicitis aguda con peritonitis generalizada / perforación",
            "procedure_name": "Apendicectomía laparoscópica de urgencia y lavado peritoneal",
            "cpt": "44970",
            "urgency": "EMERGENCIA_VITAL (URGENCIA INMEDIATA)",
            "cost": 3100.0,
            "clinical_summary": "Paciente acude a emergencias con dolor periumbilical migrado a fosa ilíaca derecha de 24h, fiebre de 38.8°C, signo de Blumberg francamente positivo y leucocitosis de 18,500 con 85% neutrófilos. Se indica intervención quirúrgica de urgencia inmediata por riesgo inminente de sepsis.",
            "docs_attached": [
                {"name": "Nota de Ingreso de Urgencia", "detail": "Score de Alvarado 9/10, signos peritoneales."},
                {"name": "Laboratorio Urgente", "detail": "Leucocitosis 18,500/uL con neutrofilia del 85%."},
                {"name": "Presupuesto de Emergencia", "detail": "USD $3,100.00 de quirófano de urgencia y lavado."},
            ]
        }
    )
    shutil.copy(case_delta_dir / "01_Nota_Ingreso_Emergencia_Apendicectomia.pdf", PUBLIC_SAMPLE_DIR / "informe_apendicectomia_urgencia.pdf")

    # 2. Póliza (Nueva: 15 días, aplica excepción de urgencia vital)
    generate_policy_certificate(
        case_delta_dir / "02_Certificado_Poliza_Asegurado.pdf",
        p_delta,
        {
            "policy_number": "POL-2026-9901",
            "plan_name": "Plan Emergency Elite",
            "start_date": "2026-08-31",
            "months_active": 0.5,
            "max_limit": 60000,
        }
    )

    # 3. Laboratorio Urgente
    generate_lab_report(
        case_delta_dir / "03_Laboratorio_Urgente_Leucocitosis.pdf",
        p_delta,
        [
            {"test": "Leucocitos Totales", "val": "18,500", "unit": "/uL", "ref": "4,500 - 10,000", "status": "ALTO (Infección)"},
            {"test": "Neutrófilos Segmentados", "val": "85.2", "unit": "%", "ref": "50.0 - 70.0", "status": "ALTO (Desv. Izq.)"},
            {"test": "Proteína C Reactiva (PCR)", "val": "68.4", "unit": "mg/L", "ref": "0.0 - 5.0", "status": "ALTO (Inflamatorio)"},
            {"test": "Hemoglobina", "val": "15.1", "unit": "g/dL", "ref": "13.5 - 17.5", "status": "Normal"},
            {"test": "Plaquetas", "val": "285,000", "unit": "/uL", "ref": "150,000 - 450,000", "status": "Normal"},
            {"test": "Tiempo de Protrombina (TP)", "val": "12.3", "unit": "seg", "ref": "11.0 - 13.5", "status": "Normal"},
        ]
    )

    # 4. Presupuesto Emergencia
    generate_budget_breakdown(
        case_delta_dir / "04_Presupuesto_Emergencia.pdf",
        p_delta,
        {
            "procedure": "Apendicectomía Laparoscópica de Urgencia y Lavado Quirúrgico",
            "items": [
                {"concept": "Quirófano de Emergencia y Torre", "desc": "Disponibilidad nocturna inmediata", "val": 1200.0},
                {"concept": "Honorarios Equipo Quirúrgico Urgencia", "desc": "Cirujano de guardia y ayudante", "val": 1200.0},
                {"concept": "Anestesia y Recuperación Urgente", "desc": "Anestesia general balanceada", "val": 400.0},
                {"concept": "Antibioticoterapia e Insumos Peritonitis", "desc": "Soluciones de lavado y apósitos", "val": 300.0},
            ],
            "total": 3100.0,
        }
    )

    # =========================================================================
    # EMPAQUETADO EN ARCHIVOS .ZIP INDIVIDUALES Y MASTER BUNDLE
    # =========================================================================
    packages = [
        ("case-alfa", "AuraQx_Caso_Alfa_Colecistectomia_Mendoza.zip"),
        ("case-beta", "AuraQx_Caso_Beta_Hernioplastia_Silva.zip"),
        ("case-gamma", "AuraQx_Caso_Gamma_Cesarea_Ramos.zip"),
        ("case-delta", "AuraQx_Caso_Delta_Apendicectomia_Morales.zip"),
    ]

    for folder_name, zip_name in packages:
        folder_path = OUTPUT_DIR / folder_name
        zip_path = OUTPUT_DIR / zip_name
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.endswith(".pdf"):
                        full_file_path = os.path.join(root, file)
                        arcname = os.path.join(folder_name, file)
                        zf.write(full_file_path, arcname=arcname)
        print(f"📦 Paquete ZIP creado: {zip_path.name} ({zip_path.stat().st_size / 1024:.1f} KB)")

    # Master Bundle
    master_zip_path = OUTPUT_DIR / "AuraQx_Todos_Los_Casos_Clinicos.zip"
    with zipfile.ZipFile(master_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for folder_name, _ in packages:
            folder_path = OUTPUT_DIR / folder_name
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.endswith(".pdf"):
                        full_file_path = os.path.join(root, file)
                        arcname = os.path.join("Expedientes_AuraQx", folder_name, file)
                        zf.write(full_file_path, arcname=arcname)
    print(f"🌟 Master Bundle ZIP creado: {master_zip_path.name} ({master_zip_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    create_all_packages()
