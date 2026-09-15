import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.config import settings
from app.models.policy import CarenciaRule, InsuredPolicy
from app.models.resolution import PreAuthResolution

logger = logging.getLogger("auraqx.notion")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
POLICIES_FILE = DATA_DIR / "demo_policies.json"
CASES_FILE = DATA_DIR / "saved_cases.json"


class NotionBridge:
    """Conector bidireccional para bases de datos de Notion con soporte dual:
    - Modo Oficial Notion: Conexión vía notion-client cuando NOTION_API_KEY y DB_IDs están configurados.
    - Modo Reactivo Local: Almacén JSON en memoria y persistente para demostración 100% garantizada sin fallos de red.
    """

    def __init__(self):
        self.api_key = settings.notion_api_key
        self.policies_db_id = settings.notion_policies_db_id
        self.preauths_db_id = settings.notion_preauths_db_id
        self.client = None
        self._local_policies: List[InsuredPolicy] = []
        self._local_cases: List[Dict[str, Any]] = []

        self._load_local_data()
        self._init_notion_client()

    def _load_local_data(self):
        if POLICIES_FILE.exists():
            try:
                with open(POLICIES_FILE, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    self._local_policies = [InsuredPolicy(**p) for p in raw]
            except Exception as e:
                logger.error("Error cargando demo_policies.json: %s", e)

        if CASES_FILE.exists():
            try:
                with open(CASES_FILE, "r", encoding="utf-8") as f:
                    self._local_cases = json.load(f)
            except Exception as e:
                logger.error("Error cargando saved_cases.json: %s", e)

    def _init_notion_client(self):
        if self.api_key and (self.policies_db_id or self.preauths_db_id):
            try:
                from notion_client import Client
                self.client = Client(auth=self.api_key)
                logger.info("Notion Client inicializado con API Key provista.")
            except Exception as e:
                logger.warning("No se pudo inicializar Notion Client: %s. Operando en modo mock local.", e)
                self.client = None
        else:
            logger.info("Credenciales de Notion no provistas. Operando en modo local reactivo garantizado.")

    def is_live_notion_connected(self) -> bool:
        return self.client is not None and bool(self.api_key)

    async def get_policy_by_patient_id(self, patient_id: str) -> Optional[InsuredPolicy]:
        clean_id = patient_id.strip()

        # Si tenemos cliente de Notion y DB ID de pólizas, intentar consulta remota
        if self.client and self.policies_db_id:
            try:
                query = self.client.databases.query(
                    database_id=self.policies_db_id,
                    filter={
                        "property": "Cédula",
                        "rich_text": {
                            "equals": clean_id
                        }
                    }
                )
                results = query.get("results", [])
                if results:
                    page = results[0]
                    props = page.get("properties", {})
                    # Mapear propiedades de Notion a modelo
                    pol_num = props.get("Número de Póliza", {}).get("rich_text", [{}])[0].get("plain_text", "POL-NOTION")
                    name = props.get("Nombre", {}).get("title", [{}])[0].get("plain_text", "Asegurado")
                    start_date = props.get("Fecha Inicio", {}).get("date", {}).get("start", "2025-01-01")
                    plan = props.get("Plan", {}).get("select", {}).get("name", "Plan Oro")
                    status_pol = props.get("Estado", {}).get("select", {}).get("name", "Activa")

                    return InsuredPolicy(
                        policy_number=pol_num,
                        patient_id=clean_id,
                        patient_name=name,
                        plan_tier=plan,
                        start_date=start_date,
                        status=status_pol,
                        annual_deductible=250.0,
                        deductible_met=0.0,
                        coverage_percent_in_network=80.0,
                        coverage_percent_out_network=60.0,
                        network_hospitals=["Hospital Metropolitano", "Clínica Guayaquil", "Clínica Kennedy"],
                        notion_page_id=page.get("id"),
                    )
            except Exception as e:
                logger.warning("Error consultando póliza en Notion API (%s). Recurriendo al almacén local.", e)

        # Búsqueda en almacén local
        for pol in self._local_policies:
            if pol.patient_id.strip() == clean_id:
                return pol
        return None

    async def list_all_policies(self) -> List[InsuredPolicy]:
        return self._local_policies

    async def record_preauth_case(self, res: PreAuthResolution) -> Tuple[bool, Optional[str]]:
        """Guarda la pre-autorización en el almacén local y en Notion si está configurado."""
        notion_url = None
        synced = False

        record_dict = res.model_dump()
        self._local_cases.insert(0, record_dict)

        # Guardar en archivo local
        try:
            with open(CASES_FILE, "w", encoding="utf-8") as f:
                json.dump(self._local_cases[:100], f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error("Error guardando caso en JSON: %s", e)

        # Si Notion está activo, crear fila en la base de datos de Notion
        if self.client and self.preauths_db_id:
            try:
                properties = {
                    "ID Solicitud": {
                        "title": [{"text": {"content": res.case_id}}]
                    },
                    "Paciente": {
                        "rich_text": [{"text": {"content": f"{res.patient_name} ({res.patient_id})"}}]
                    },
                    "Póliza": {
                        "rich_text": [{"text": {"content": res.policy_number}}]
                    },
                    "Procedimiento": {
                        "rich_text": [{"text": {"content": res.procedure_name}}]
                    },
                    "Hospital": {
                        "rich_text": [{"text": {"content": res.hospital_name}}]
                    },
                    "Estado": {
                        "select": {"name": res.status.value}
                    },
                    "Monto Cubierto": {
                        "number": res.financials.insurer_pays
                    },
                    "Copago Paciente": {
                        "number": res.financials.patient_copay
                    },
                    "Carencia Cumplida": {
                        "checkbox": res.carencia_audit.is_satisfied
                    },
                    "Justificación": {
                        "rich_text": [{"text": {"content": res.clinical_justification[:1900]}}]
                    }
                }

                page = self.client.pages.create(
                    parent={"database_id": self.preauths_db_id},
                    properties=properties
                )
                notion_url = page.get("url")
                synced = True
                logger.info("Caso %s registrado exitosamente en Notion DB: %s", res.case_id, notion_url)
            except Exception as e:
                logger.warning("No se pudo escribir en Notion DB (%s). Guardado en almacén local exitosamente.", e)

        return synced, notion_url

    async def list_all_cases(self) -> List[Dict[str, Any]]:
        return self._local_cases


# Singleton
notion_bridge = NotionBridge()
