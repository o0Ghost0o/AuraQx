from typing import Any, Dict, List
from fastapi import APIRouter

from app.core.notion_bridge import notion_bridge
from app.models.policy import InsuredPolicy

router = APIRouter(prefix="/api/notion", tags=["Notion Database"])


@router.get("/status")
async def get_notion_status():
    """Retorna el estado de la conexión con Notion (API oficial en vivo vs Almacén reactivo garantizado)."""
    is_live = notion_bridge.is_live_notion_connected()
    policies = await notion_bridge.list_all_policies()
    cases = await notion_bridge.list_all_cases()

    return {
        "is_connected": is_live,
        "connection_mode": "Notion Cloud API Oficial" if is_live else "Almacén Reactivo Local (Mock Store Garantizado)",
        "policies_count": len(policies),
        "cases_count": len(cases),
        "database_targets": {
            "policies_database_id": notion_bridge.policies_db_id or "local_policies_store",
            "preauths_database_id": notion_bridge.preauths_db_id or "local_preauths_store",
        }
    }


@router.get("/policies", response_model=List[InsuredPolicy])
async def list_policies():
    """Retorna las pólizas de asegurados registradas en Notion."""
    return await notion_bridge.list_all_policies()


@router.get("/cases", response_model=List[Dict[str, Any]])
async def list_cases():
    """Retorna el historial de resoluciones y pre-autorizaciones emitidas y sincronizadas."""
    return await notion_bridge.list_all_cases()
