import json
from pathlib import Path
from typing import Any, List
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/demo", tags=["Casos de Demostración"])

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "demo_cases.json"
PACKAGES_DIR = Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "public" / "case_packages"


def ensure_packages_exist():
    """Genera automáticamente los paquetes descargables si aún no existen."""
    master_zip = PACKAGES_DIR / "AuraQx_Todos_Los_Casos_Clinicos.zip"
    if not master_zip.exists():
        try:
            from scripts.generate_case_packages import create_all_packages
            create_all_packages()
        except Exception:
            pass


@router.get("/cases", response_model=List[Any])
async def get_demo_cases():
    """Retorna los 4 casos clínicos de prueba con metadatos de paquetes de documentos descargables."""
    ensure_packages_exist()
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


@router.get("/cases/{case_id}/package")
async def download_case_package(case_id: str):
    """Descarga el paquete completo de documentos (.ZIP) para un caso clínico específico."""
    ensure_packages_exist()
    case_zips = {
        "case-alfa": "AuraQx_Caso_Alfa_Colecistectomia_Mendoza.zip",
        "case-beta": "AuraQx_Caso_Beta_Hernioplastia_Silva.zip",
        "case-gamma": "AuraQx_Caso_Gamma_Cesarea_Ramos.zip",
        "case-delta": "AuraQx_Caso_Delta_Apendicectomia_Morales.zip",
    }
    zip_name = case_zips.get(case_id)
    if not zip_name:
        raise HTTPException(status_code=404, detail=f"Caso no encontrado: {case_id}")

    file_path = PACKAGES_DIR / zip_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Archivo ZIP no encontrado: {zip_name}")

    return FileResponse(
        path=str(file_path),
        filename=zip_name,
        media_type="application/zip",
    )


@router.get("/packages/all")
async def download_all_packages():
    """Descarga el bundle maestro (.ZIP) con todos los expedientes y casos clínicos del Reto 1."""
    ensure_packages_exist()
    zip_name = "AuraQx_Todos_Los_Casos_Clinicos.zip"
    file_path = PACKAGES_DIR / zip_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Paquete maestro no encontrado")

    return FileResponse(
        path=str(file_path),
        filename=zip_name,
        media_type="application/zip",
    )


@router.get("/documents/{case_id}/{doc_name}")
async def download_single_document(case_id: str, doc_name: str):
    """Descarga un documento PDF individual del expediente clínico (informe, ecografía, póliza, etc.)."""
    ensure_packages_exist()
    file_path = PACKAGES_DIR / case_id / doc_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Documento no encontrado: {doc_name}")

    return FileResponse(
        path=str(file_path),
        filename=doc_name,
        media_type="application/pdf",
    )
