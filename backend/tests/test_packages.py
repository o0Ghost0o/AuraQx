import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_get_demo_cases_with_packages():
    """Verifica que /api/demo/cases incluya los metadatos de paquetes de documentos descargables."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/demo/cases")
        assert resp.status_code == 200
        cases = resp.json()
        assert len(cases) == 4
        for c in cases:
            assert "package" in c
            assert "zip_url" in c["package"]
            assert len(c["package"]["documents"]) >= 4


@pytest.mark.asyncio
async def test_download_case_package_zip():
    """Verifica la descarga del paquete .ZIP para el caso alfa."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/demo/cases/case-alfa/package")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/zip"
        assert len(resp.content) > 1000


@pytest.mark.asyncio
async def test_download_all_packages_master_zip():
    """Verifica la descarga del archivo maestro con todos los paquetes clínicos."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/demo/packages/all")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/zip"
        assert len(resp.content) > 5000


@pytest.mark.asyncio
async def test_download_individual_document_pdf():
    """Verifica la descarga de un PDF clínico individual del expediente."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/demo/documents/case-alfa/01_Informe_Quirurgico_Colecistectomia.pdf")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        assert resp.content.startswith(b"%PDF")
