import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.config import settings
from app.core.tasks import extract_and_analyze_document_task, broker, results_backend


def test_dramatiq_actor_direct():
    """Verifica que el actor de Dramatiq procese un documento clínico en segundo plano."""
    from dramatiq import Worker
    worker = Worker(broker, worker_threads=1)
    worker.start()
    try:
        test_pdf = "../frontend/public/sample_reports/informe_colecistectomia_aprobado.pdf"
        msg = extract_and_analyze_document_task.send(test_pdf, "0928374102")
        
        # Obtener resultado
        res = results_backend.get_result(msg, block=True, timeout=5000)
        assert res is not None
        assert res["status"] == "COMPLETED"
        assert res["case_id"].startswith("AUTH-2026-")
        assert res["resolution"]["status"] == "PRE_APROBADO"
    finally:
        worker.stop()


@pytest.mark.asyncio
async def test_upload_analyze_endpoint_fast():
    """Verifica que /api/preauth/analyze-upload responda en milisegundos sin congelar el servidor."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Login
        login_resp = await client.post(
            "/api/auth/login",
            json={"username": settings.auth_username, "password": settings.auth_password}
        )
        token = login_resp.json()["access_token"]

        # 2. Upload file
        test_pdf = "../frontend/public/sample_reports/informe_colecistectomia_aprobado.pdf"
        with open(test_pdf, "rb") as f:
            files = {"file": ("informe.pdf", f, "application/pdf")}
            resp = await client.post(
                "/api/preauth/analyze-upload",
                files=files,
                data={"patient_id": "0928374102"},
                headers={"Authorization": f"Bearer {token}"}
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "PRE_APROBADO"
        assert data["patient_name"] == "María Carmen Mendoza"
        assert data["carencia_audit"]["is_satisfied"] is True
