import asyncio
import json
import logging
from datetime import datetime
from typing import AsyncGenerator, Dict, Optional, Tuple

from app.core.docling_extractor import docling_extractor
from app.core.llm_client import llm_client
from app.core.notion_bridge import notion_bridge
from app.core.rules_engine import audit_preauthorization
from app.models.clinical import MedicalReport
from app.models.resolution import PreAuthResolution, ResolutionStatus, TelemetryEvent

logger = logging.getLogger("auraqx.agent")


class PreAuthAgent:
    """Orquestador agéntico de pre-autorización quirúrgica en tiempo real.
    Ejecuta el pipeline de 6 pasos emitiendo telemetría en vivo vía SSE.
    """

    async def run_pipeline_streaming(
        self,
        report: MedicalReport,
        raw_document_path: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Generador asíncrono que emite eventos de telemetría SSE en cada etapa."""

        # Helper para formatear eventos SSE
        def sse_pack(event: TelemetryEvent, payload: Optional[Dict] = None) -> str:
            data = {"telemetry": event.model_dump()}
            if payload:
                data["payload"] = payload
            return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

        now = lambda: datetime.now().strftime("%H:%M:%S")

        # PASO 1: Ingestión y Extracción Multimodal (Docling)
        yield sse_pack(
            TelemetryEvent(
                step=1,
                title="Extracción Multimodal de Informe Médico (IBM Docling)",
                status="running",
                detail=f"Analizando documento clínico de {report.hospital_name}...",
                timestamp=now(),
            )
        )
        await asyncio.sleep(0.3)

        if raw_document_path:
            extracted_text = docling_extractor.extract_text_from_file(raw_document_path)
            report.raw_text = extracted_text
            # Intentar extracción mejorada con LLM Together.ai si está configurado
            llm_entities = await llm_client.extract_clinical_entities_with_llm(extracted_text)
            if llm_entities:
                if llm_entities.get("patient_name"):
                    report.patient_name = llm_entities["patient_name"]
                if llm_entities.get("diagnosis_icd10"):
                    report.diagnosis_icd10 = llm_entities["diagnosis_icd10"]
                if llm_entities.get("procedure_name"):
                    report.procedure_name = llm_entities["procedure_name"]

        yield sse_pack(
            TelemetryEvent(
                step=1,
                title="Extracción Multimodal Completada",
                status="success",
                detail=f"Paciente: {report.patient_name} ({report.patient_id}) | Cirugía: {report.procedure_name} | CIE-10: {report.diagnosis_icd10}",
                timestamp=now(),
            )
        )
        await asyncio.sleep(0.4)

        # PASO 2: Consulta de Póliza en Notion DB
        yield sse_pack(
            TelemetryEvent(
                step=2,
                title="Búsqueda de Póliza en Base de Datos de Notion",
                status="running",
                detail=f"Consultando registros de asegurado C.I. {report.patient_id} en Notion...",
                timestamp=now(),
            )
        )
        await asyncio.sleep(0.4)

        policy = await notion_bridge.get_policy_by_patient_id(report.patient_id)
        if not policy:
            yield sse_pack(
                TelemetryEvent(
                    step=2,
                    title="Póliza No Encontrada en Notion",
                    status="error",
                    detail=f"No se localizó ninguna póliza activa para la cédula {report.patient_id} en Notion.",
                    timestamp=now(),
                )
            )
            return

        yield sse_pack(
            TelemetryEvent(
                step=2,
                title="Póliza Localizada en Notion DB",
                status="success",
                detail=f"Póliza N° {policy.policy_number} | {policy.plan_tier} | Vigencia desde: {policy.start_date} | Estado: {policy.status}",
                timestamp=now(),
            )
        )
        await asyncio.sleep(0.4)

        # PASO 3: Auditoría Cronológica de Carencias
        yield sse_pack(
            TelemetryEvent(
                step=3,
                title="Auditoría de Períodos de Carencia y Antigüedad",
                status="running",
                detail=f"Calculando meses transcurridos vs requisitos de carencia contractual para '{report.procedure_name}'...",
                timestamp=now(),
            )
        )
        await asyncio.sleep(0.5)

        # PASO 4: Verificación de Exclusiones y Red Hospitalaria
        yield sse_pack(
            TelemetryEvent(
                step=4,
                title="Verificación de Red Hospitalaria y Exclusiones",
                status="running",
                detail=f"Comprobando convenio con {report.hospital_name} y catálogo de exclusiones del plan...",
                timestamp=now(),
            )
        )
        await asyncio.sleep(0.3)

        # PASO 5: Auditoría de Documentos y Checklist Quirúrgico
        yield sse_pack(
            TelemetryEvent(
                step=5,
                title="Auditoría de Pruebas y Documentación Quirúrgica",
                status="running",
                detail=f"Auditando {len(report.attachments)} documento(s) adjunto(s) frente al protocolo clínico requerido...",
                timestamp=now(),
            )
        )
        await asyncio.sleep(0.4)

        # Ejecutar evaluación clínica mediante el motor de reglas
        resolution = audit_preauthorization(report, policy)

        # Si LLM está disponible, enriquecer fundamentación clínica
        if llm_client.is_configured():
            llm_just = await llm_client.generate_clinical_reasoning(
                report_summary=report.clinical_summary,
                procedure_name=report.procedure_name,
                carencia_summary=resolution.carencia_audit.explanation,
                is_approved=resolution.status == ResolutionStatus.PRE_APROBADO,
                missing_docs=[d.title for d in resolution.missing_documents],
            )
            if llm_just:
                resolution.clinical_justification = llm_just

        # PASO 6: Emisión de Resolución y Sincronización con Notion
        yield sse_pack(
            TelemetryEvent(
                step=6,
                title="Sincronización en Tiempo Real con Notion DB",
                status="running",
                detail="Escribiendo resolución, voucher y desglose financiero en la base de datos de Notion...",
                timestamp=now(),
            )
        )

        synced, notion_url = await notion_bridge.record_preauth_case(resolution, report=report)
        resolution.notion_synced = synced
        resolution.notion_url = notion_url

        final_status_text = (
            "PRE-APROBADO EXITOSAMENTE"
            if resolution.status == ResolutionStatus.PRE_APROBADO
            else ("DOCUMENTOS FALTANTES REQUERIDOS" if resolution.status == ResolutionStatus.DOCUMENTOS_FALTANTES else "SOLICITUD RECHAZADA")
        )

        yield sse_pack(
            TelemetryEvent(
                step=6,
                title=f"Resolución Emitida: {final_status_text}",
                status="success" if resolution.status == ResolutionStatus.PRE_APROBADO else ("warning" if resolution.status == ResolutionStatus.DOCUMENTOS_FALTANTES else "error"),
                detail=f"Caso {resolution.case_id} registrado. Cobertura: {resolution.financials.coverage_percent}% (${resolution.financials.insurer_pays:,.2f} USD)",
                timestamp=now(),
            ),
            payload=resolution.model_dump(),
        )


preauth_agent = PreAuthAgent()
