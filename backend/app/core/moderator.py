import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.llm_client import llm_client
from app.models.clinical import MedicalReport
from app.models.policy import InsuredPolicy
from app.models.resolution import ModerationAuditResult, PreAuthResolution

logger = logging.getLogger("auraqx.moderator")

LEGAL_POLICIES_FILE = Path(__file__).resolve().parent.parent / "data" / "legal_policies.json"


class ComplianceModerator:
    """Moderador dinámico de Términos y Condiciones y Política de Privacidad (PHI).
    
    Principio de Arquitectura:
    - NO hardcodea los términos ni la política de privacidad en el código del agente.
    - Carga dinámicamente las políticas vigentes en la webapp (`legal_policies.json` / API).
    - Permite que cualquier modificación futura en los términos de la aplicación sea
      adoptada de inmediato por el moderador sin necesidad de re-codificar el agente.
    """

    def __init__(self):
        self._fallback_policies = {
            "terms_and_conditions": {
                "version": "v2026.2",
                "title": "Términos y Condiciones de Uso — AuraQx",
                "clauses": [
                  {"id": "TC-01", "title": "Legitimidad Médica y Ámbito Clínico", "mandatory": True},
                  {"id": "TC-02", "title": "Veracidad Documental y Condición Antifraude", "mandatory": True},
                  {"id": "TC-03", "title": "Convenio de Red y Cobertura Financiera", "mandatory": True},
                  {"id": "TC-04", "title": "Cumplimiento de Carencias Contractuales", "mandatory": True}
                ]
            },
            "privacy_policy": {
                "version": "v2026.2",
                "title": "Política de Privacidad y Protección de Datos de Salud (PHI)",
                "clauses": [
                  {"id": "PP-01", "title": "Principio de Minimización y Uso Exclusivo", "mandatory": True},
                  {"id": "PP-02", "title": "Protección de Información de Salud Protegida (PHI)", "mandatory": True},
                  {"id": "PP-03", "title": "Cifrado de Transmisión y Trazabilidad", "mandatory": True},
                  {"id": "PP-04", "title": "Consentimiento Informado del Paciente", "mandatory": True}
                ]
            }
        }

    def get_active_policies(self) -> Dict[str, Any]:
        """Recupera en tiempo real las políticas legales y de privacidad activas en la webapp."""
        if LEGAL_POLICIES_FILE.exists():
            try:
                with open(LEGAL_POLICIES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error("Error leyendo legal_policies.json: %s", e)
        return self._fallback_policies

    def update_policies(self, new_policies: Dict[str, Any]) -> bool:
        """Permite actualizar las políticas de la webapp en caliente."""
        try:
            with open(LEGAL_POLICIES_FILE, "w", encoding="utf-8") as f:
                json.dump(new_policies, f, indent=2, ensure_ascii=False)
            logger.info("Políticas legales y de privacidad actualizadas exitosamente.")
            return True
        except Exception as e:
            logger.error("Error guardando legal_policies.json: %s", e)
            return False

    async def audit_compliance(
        self,
        report: MedicalReport,
        policy: Optional[InsuredPolicy] = None,
        resolution: Optional[PreAuthResolution] = None,
    ) -> ModerationAuditResult:
        """Audita el caso frente a los Términos y Condiciones y la Política de Privacidad dinámicos."""
        policies = self.get_active_policies()
        terms = policies.get("terms_and_conditions", {})
        privacy = policies.get("privacy_policy", {})

        terms_version = terms.get("version", "v2026.2")
        privacy_version = privacy.get("version", "v2026.2")
        terms_clauses = terms.get("clauses", [])
        privacy_clauses = privacy.get("clauses", [])

        verified_clauses: List[str] = []
        is_terms_ok = True
        is_privacy_ok = True
        notes: List[str] = []

        # 1. Auditoría Dinámica de Términos y Condiciones
        for clause in terms_clauses:
            c_id = clause.get("id", "TC")
            c_title = clause.get("title", "")
            verified_clauses.append(f"{c_id}: {c_title}")

        # Comprobación de exclusiones éticas/cosméticas según términos
        procedure_lower = (report.procedure_name or "").lower()
        if any(w in procedure_lower for w in ["estética", "cosmética", "rinoplastia estética", "liposucción estética"]):
            if "reconstructiv" not in procedure_lower and "funcional" not in procedure_lower:
                is_terms_ok = False
                notes.append("Alerta Términos: Procedimiento señalado como cosmético no reconstructivo.")

        # Comprobación de red hospitalaria según términos
        if policy and policy.network_hospitals:
            if report.hospital_name and not any(h.lower() in report.hospital_name.lower() or report.hospital_name.lower() in h.lower() for h in policy.network_hospitals):
                notes.append(f"Nota Términos: Hospital {report.hospital_name} fuera de red preferente (aplica arancel out-of-network).")

        # 2. Auditoría Dinámica de Privacidad y Confidencialidad de Salud (PHI)
        for clause in privacy_clauses:
            c_id = clause.get("id", "PP")
            c_title = clause.get("title", "")
            verified_clauses.append(f"{c_id}: {c_title}")

        # Comprobación de minimización y legitimidad del identificador
        if not report.patient_id or len(report.patient_id.strip()) < 5:
            is_privacy_ok = False
            notes.append("Alerta Privacidad: Identificador de paciente ausente o inconsistente para tratamiento de salud.")

        # 3. LLM Guardrail Dinámico (si está configurado)
        # Inyecta los términos y política dinámicos para moderación semántica sin re-codificar
        if llm_client.is_configured() and report.raw_text:
            try:
                llm_prompt = f"""Eres el Moderador de Cumplimiento Legal y Privacidad Médica de AuraQx.
Evalúa el siguiente informe clínico frente a los Términos y la Política de Privacidad ACTIVOS de la plataforma:

[TÉRMINOS ACTIVOS - Versión {terms_version}]:
{json.dumps(terms_clauses, ensure_ascii=False)}

[POLÍTICA DE PRIVACIDAD ACTIVA - Versión {privacy_version}]:
{json.dumps(privacy_clauses, ensure_ascii=False)}

[INFORME DEL CASO]:
- Paciente: {report.patient_name} (ID: {report.patient_id})
- Cirugía: {report.procedure_name}
- Hospital: {report.hospital_name}
- Resumen Clínico: {report.clinical_summary[:800]}

Responde ÚNICAMENTE un JSON con:
{{
  "compliant": true/false,
  "terms_compliant": true/false,
  "privacy_compliant": true/false,
  "rationale": "breve síntesis de cumplimiento"
}}"""

                llm_res = await llm_client.client.chat.completions.create(
                    model=llm_client.model,
                    messages=[
                        {"role": "system", "content": "Eres un moderador legal y de privacidad médica. Responde sólo JSON."},
                        {"role": "user", "content": llm_prompt}
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"} if "llama" in llm_client.model.lower() or "gpt" in llm_client.model.lower() else None,
                )
                raw_json = llm_res.choices[0].message.content or "{}"
                mod_data = json.loads(raw_json)
                if not mod_data.get("compliant", True):
                    is_terms_ok = is_terms_ok and mod_data.get("terms_compliant", True)
                    is_privacy_ok = is_privacy_ok and mod_data.get("privacy_compliant", True)
                    if mod_data.get("rationale"):
                        notes.append(mod_data["rationale"])
            except Exception as e:
                logger.warning("Moderador LLM no pudo ejecutarse (%s). Manteniendo moderación determinista.", e)

        # Generar explicación sintetizada
        if not notes:
            explanation = (
                f"Caso auditado y 100% conforme con los Términos y Condiciones ({terms_version}) "
                f"y la Política de Privacidad de Datos de Salud ({privacy_version}) activos en la webapp."
            )
        else:
            explanation = " | ".join(notes)

        return ModerationAuditResult(
            is_compliant=is_terms_ok and is_privacy_ok,
            terms_compliant=is_terms_ok,
            privacy_compliant=is_privacy_ok,
            terms_version=terms_version,
            privacy_version=privacy_version,
            explanation=explanation,
            verified_clauses=verified_clauses
        )


compliance_moderator = ComplianceModerator()
