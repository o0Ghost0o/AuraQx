import json
import logging
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger("auraqx.llm")


class LLMClient:
    """Cliente para endpoints OpenAI-compatibles (Together.ai, Groq, vLLM, OpenAI).
    Soporta extracción estructurada y fundamentación clínica agéntica.
    """

    def __init__(self):
        self.base_url = settings.openai_base_url
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model
        self.client: Optional[AsyncOpenAI] = None
        self._init_client()

    def _init_client(self):
        if self.api_key and len(self.api_key.strip()) > 5:
            try:
                self.client = AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
                    timeout=20.0,
                )
                logger.info("Cliente OpenAI-Compatible inicializado en %s con modelo %s", self.base_url, self.model)
            except Exception as e:
                logger.warning("No se pudo instanciar cliente OpenAI: %s", e)
                self.client = None
        else:
            logger.info("OPENAI_API_KEY no provista. Operando en modo determinista local ultra-rápido.")

    def is_configured(self) -> bool:
        return self.client is not None

    async def extract_clinical_entities_with_llm(self, text: str) -> Optional[Dict[str, Any]]:
        if not self.client:
            return None

        prompt = f"""Eres un médico auditor experto en seguros de salud.
Analiza el siguiente informe médico quirúrgico extraído de un hospital y extrae los siguientes datos en formato JSON estrictamente válido:
- patient_name: nombre del paciente
- patient_id: cédula de identidad o ID
- patient_age: edad numérica en años
- patient_gender: 'M' o 'F'
- hospital_name: nombre del hospital o clínica
- treating_physician: médico o cirujano tratante
- diagnosis_icd10: código CIE-10 y descripción diagnóstica
- procedure_name: nombre de la cirugía o procedimiento solicitado
- urgency: 'ELECTIVA', 'URGENCIA' o 'EMERGENCIA_VITAL'
- estimated_cost: presupuesto estimado en números
- attached_docs: lista de nombres de estudios o documentos adjuntos mencionados (ej. ecografia, laboratorio, riesgo_quirurgico, presupuesto)

Texto del informe médico:
\"\"\"
{text[:4000]}
\"\"\"

Responde ÚNICAMENTE con el objeto JSON."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un asistente médico forense y de auditoría de seguros. Responde sólo JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"} if "llama" in self.model.lower() or "gpt" in self.model.lower() else None,
            )
            content = response.choices[0].message.content or "{}"
            parsed = json.loads(content)
            return parsed
        except Exception as e:
            logger.warning("Error llamando a LLM para extracción clínica (%s). Utilizando extractor determinista.", e)
            return None

    async def generate_clinical_reasoning(
        self,
        report_summary: str,
        procedure_name: str,
        carencia_summary: str,
        is_approved: bool,
        missing_docs: List[str]
    ) -> Optional[str]:
        if not self.client:
            return None

        prompt = f"""Genera una fundamentación técnica y médica para una resolución de pre-autorización quirúrgica en un hospital.
Datos:
- Cirugía: {procedure_name}
- Estado: {'PRE-APROBADO' if is_approved else ('DOCUMENTOS FALTANTES' if missing_docs else 'RECHAZADO')}
- Evaluación de Carencia: {carencia_summary}
- Documentos Faltantes (si aplica): {', '.join(missing_docs) if missing_docs else 'Ninguno, expediente completo'}
- Cuadro Clínico: {report_summary}

Escribe un párrafo formal, conciso y normativo (máximo 4 oraciones) para ser emitido al hospital y al paciente."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres el Agente Inteligente de Pre-Autorizaciones Quirúrgicas de la Aseguradora."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=250,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.warning("Fallo al generar reasoning con LLM: %s", e)
            return None


llm_client = LLMClient()
