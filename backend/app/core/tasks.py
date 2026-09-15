import logging
import os
from typing import Any, Dict, Optional
import dramatiq
from dramatiq import Worker
from dramatiq.brokers.stub import StubBroker
from dramatiq.results import Results
from dramatiq.results.backends.stub import StubBackend

from app.config import settings

logger = logging.getLogger("auraqx.tasks")

# Configurar backend de resultados y broker de Dramatiq
# Soporta RedisBroker si REDIS_URL está configurado, o StubBroker para ejecución local autónoma
results_backend = StubBackend()
broker = StubBroker()
broker.add_middleware(Results(backend=results_backend))
dramatiq.set_broker(broker)

# Worker en segundo plano para procesar tareas de Dramatiq sin bloquear el event loop
_worker: Optional[Worker] = None


def start_dramatiq_worker():
    global _worker
    if _worker is None:
        try:
            _worker = Worker(broker, worker_threads=2)
            _worker.start()
            logger.info("Dramatiq worker iniciado con 2 hilos en segundo plano.")
        except Exception as e:
            logger.warning("No se pudo iniciar worker de Dramatiq: %s", e)


def stop_dramatiq_worker():
    global _worker
    if _worker is not None:
        try:
            _worker.stop()
            logger.info("Dramatiq worker detenido.")
        except Exception:
            pass
        _worker = None


@dramatiq.actor(store_results=True)
def extract_and_analyze_document_task(file_path: str, patient_id: Optional[str] = None) -> Dict[str, Any]:
    """Actor de Dramatiq: Procesa en segundo plano la extracción multimodal (Docling/OCR)

    y la auditoría de la pre-autorización, liberando completamente el loop de FastAPI.
    """
    from app.core.docling_extractor import docling_extractor
    from app.core.notion_bridge import notion_bridge
    from app.core.rules_engine import audit_preauthorization

    logger.info("Dramatiq Actor ejecutando extracción para: %s", file_path)

    # 1. Extracción multimodal
    raw_text = docling_extractor.extract_text_from_file(file_path)
    report = docling_extractor.parse_clinical_report(raw_text, fallback_patient_id=patient_id)

    # 2. Búsqueda de póliza (sincrónico para el worker)
    # En el worker local usamos el almacén local
    for pol in notion_bridge._local_policies:
        if pol.patient_id.strip() == report.patient_id.strip():
            policy = pol
            break
    else:
        policy = notion_bridge._local_policies[0] if notion_bridge._local_policies else None

    if not policy:
        return {"status": "ERROR", "message": f"Póliza no encontrada para {report.patient_id}"}

    # 3. Auditoría de reglas
    resolution = audit_preauthorization(report, policy)

    # 4. Guardar caso
    notion_bridge._local_cases.insert(0, resolution.model_dump())

    logger.info("Dramatiq Actor finalizó exitosamente caso: %s (%s)", resolution.case_id, resolution.status.value)
    return {
        "status": "COMPLETED",
        "case_id": resolution.case_id,
        "resolution": resolution.model_dump(),
    }
