import json
import os
import tempfile
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

from app.core.agent import preauth_agent
from app.core.auth import get_current_user
from app.core.docling_extractor import docling_extractor
from app.core.notion_bridge import notion_bridge
from app.core.rules_engine import audit_preauthorization
from app.models.auth import UserProfile
from app.models.clinical import DocumentAttachment, MedicalReport, UrgencyLevel
from app.models.resolution import PreAuthResolution

router = APIRouter(prefix="/api/preauth", tags=["Pre-Autorizaciones Quirúrgicas"])


@router.post("/analyze", response_model=PreAuthResolution)
async def analyze_preauthorization(
    report: MedicalReport,
    current_user: UserProfile = Depends(get_current_user),
):
    """Evalúa un informe médico digital contra la póliza del paciente en Notion en tiempo real."""
    policy = await notion_bridge.get_policy_by_patient_id(report.patient_id)
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró póliza activa en Notion para el paciente con cédula {report.patient_id}."
        )

    resolution = audit_preauthorization(report, policy)
    synced, notion_url = await notion_bridge.record_preauth_case(resolution)
    resolution.notion_synced = synced
    resolution.notion_url = notion_url

    return resolution


@router.post("/analyze-upload", response_model=PreAuthResolution)
async def analyze_uploaded_document(
    file: UploadFile = File(...),
    patient_id: Optional[str] = Form(None),
    current_user: UserProfile = Depends(get_current_user),
):
    """Recibe un archivo PDF escaneado o digital de informe médico, lo procesa con IBM Docling y emite la resolución."""
    suffix = os.path.splitext(file.filename or "report.pdf")[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Extraer con IBM Docling
        raw_text = docling_extractor.extract_text_from_file(tmp_path)
        report = docling_extractor.parse_clinical_report(raw_text, fallback_patient_id=patient_id)

        # Consultar póliza
        policy = await notion_bridge.get_policy_by_patient_id(report.patient_id)
        if not policy:
            # Si el ID extraído no está en las pólizas demo, intentar con la primera activa
            all_policies = await notion_bridge.list_all_policies()
            if all_policies:
                policy = all_policies[0]
                report.patient_id = policy.patient_id
                report.patient_name = policy.patient_name
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"No se encontró póliza para C.I. {report.patient_id} en Notion."
                )

        resolution = audit_preauthorization(report, policy)
        synced, notion_url = await notion_bridge.record_preauth_case(resolution)
        resolution.notion_synced = synced
        resolution.notion_url = notion_url
        return resolution
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.post("/stream")
async def stream_preauthorization_telemetry(
    report: MedicalReport,
    current_user: UserProfile = Depends(get_current_user),
):
    """Transmite en vivo vía Server-Sent Events (SSE) cada uno de los 6 pasos del razonamiento agéntico."""
    return StreamingResponse(
        preauth_agent.run_pipeline_streaming(report),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


class SubmitMissingDocRequest(MedicalReport):
    resolved_doc_type: str
    uploaded_file_name: str


@router.post("/submit-missing-doc", response_model=PreAuthResolution)
async def submit_missing_document(
    req: SubmitMissingDocRequest,
    current_user: UserProfile = Depends(get_current_user),
):
    """Permite al hospital o paciente adjuntar un documento faltante y re-evaluar la solicitud inmediatamente."""
    # Añadir o marcar el documento como presente
    doc_exists = False
    for att in req.attachments:
        if att.doc_type.lower() == req.resolved_doc_type.lower():
            att.is_present = True
            att.name = req.uploaded_file_name
            doc_exists = True
            break

    if not doc_exists:
        req.attachments.append(
            DocumentAttachment(
                name=req.uploaded_file_name,
                doc_type=req.resolved_doc_type,
                is_present=True,
                notes="Documento subsanado y cargado en tiempo real."
            )
        )

    policy = await notion_bridge.get_policy_by_patient_id(req.patient_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Póliza no encontrada.")

    resolution = audit_preauthorization(req, policy)
    synced, notion_url = await notion_bridge.record_preauth_case(resolution)
    resolution.notion_synced = synced
    resolution.notion_url = notion_url

    return resolution
