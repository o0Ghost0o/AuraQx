import io
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.config import settings


@pytest.mark.asyncio
async def test_incomplete_cases_and_curing_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Login
        login_resp = await client.post(
            "/api/auth/login",
            json={"username": settings.auth_username, "password": settings.auth_password}
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Iniciar caso de Carlos Andrés Silva (Hernioplastia, faltan ecografía y riesgo quirúrgico)
        initial_report = {
            "patient_name": "Carlos Andrés Silva",
            "patient_id": "1719283041",
            "patient_age": 48,
            "patient_gender": "M",
            "hospital_name": "Clínica Kennedy",
            "treating_physician": "Dr. Roberto Baquerizo",
            "diagnosis_icd10": "K40.9 - Hernia inguinal",
            "procedure_name": "Hernioplastia inguinal con colocación de malla protésica",
            "procedure_cpt": "49505",
            "urgency": "ELECTIVA",
            "request_date": "2026-09-15",
            "estimated_cost": 2100.0,
            "attachments": [
                {"name": "Presupuesto.pdf", "doc_type": "presupuesto", "is_present": True},
                {"name": "Biometria.pdf", "doc_type": "laboratorio", "is_present": True}
            ]
        }

        resp_analyze = await client.post("/api/preauth/analyze", json=initial_report, headers=headers)
        assert resp_analyze.status_code == 200
        data_initial = resp_analyze.json()
        assert data_initial["status"] == "DOCUMENTOS_FALTANTES"
        case_id = data_initial["case_id"]
        assert len(data_initial["missing_documents"]) == 2

        # 3. Consultar /api/preauth/cases/incomplete
        resp_incomplete = await client.get("/api/preauth/cases/incomplete", headers=headers)
        assert resp_incomplete.status_code == 200
        incomplete_cases = resp_incomplete.json()
        assert isinstance(incomplete_cases, list)
        matched = next((c for c in incomplete_cases if c.get("case_id") == case_id), None)
        assert matched is not None
        assert matched["status"] == "DOCUMENTOS_FALTANTES"

        # 4. Subir archivo propio para subsanar 'ecografia'
        dummy_pdf_content = b"%PDF-1.4 Mock Ecografia de Pared Abdominal para Hernia Inguinal"
        files = {
            "file": ("mi_ecografia_propia.pdf", io.BytesIO(dummy_pdf_content), "application/pdf")
        }
        form_data = {
            "case_id": case_id,
            "patient_id": "1719283041",
            "doc_type": "ecografia",
        }
        resp_upload = await client.post(
            "/api/preauth/upload-missing-file",
            files=files,
            data=form_data,
            headers=headers
        )
        assert resp_upload.status_code == 200
        data_upload = resp_upload.json()
        assert data_upload["case_id"] == case_id
        # Ahora solo debe faltar riesgo_quirurgico
        assert data_upload["status"] == "DOCUMENTOS_FALTANTES"
        assert len(data_upload["missing_documents"]) == 1
        assert data_upload["missing_documents"][0]["doc_type"] == "riesgo_quirurgico"

        # 5. Subsanar el segundo documento (riesgo_quirurgico) con submit-missing-doc
        updated_report = {
            **initial_report,
            "case_id": case_id,
            "attachments": [
                {"name": "Presupuesto.pdf", "doc_type": "presupuesto", "is_present": True},
                {"name": "Biometria.pdf", "doc_type": "laboratorio", "is_present": True},
                {"name": "mi_ecografia_propia.pdf", "doc_type": "ecografia", "is_present": True}
            ],
            "resolved_doc_type": "riesgo_quirurgico",
            "uploaded_file_name": "Valoracion_Cardiologica_Firma.pdf"
        }
        resp_solve = await client.post(
            "/api/preauth/submit-missing-doc",
            json=updated_report,
            headers=headers
        )
        assert resp_solve.status_code == 200
        data_final = resp_solve.json()
        assert data_final["case_id"] == case_id
        # Debe haber resuelto el caso a PRE_APROBADO
        assert data_final["status"] == "PRE_APROBADO"
        assert len(data_final["missing_documents"]) == 0
        assert data_final["authorization_code"] == case_id
