import json
from pathlib import Path
from typing import Any, List
from fastapi import APIRouter

router = APIRouter(prefix="/api/demo", tags=["Casos de Demostración"])

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "demo_cases.json"


@router.get("/cases", response_model=List[Any])
async def get_demo_cases():
    """Retorna los 4 casos clínicos de prueba rápida para la evaluación del Hackathon."""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
