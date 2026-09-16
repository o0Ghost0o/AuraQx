# 📜 Aviso de Política de Tratamiento de Datos Personales — VIAMATICA S.A.
## Aplicación y Cumplimiento Normativo en AuraQx

> **Fuente Oficial:** [https://hackiathon.dev/aviso-de-la-politica-de-tratamiento-de-datos-personales/](https://hackiathon.dev/aviso-de-la-politica-de-tratamiento-de-datos-personales/)  
> **Marco Legal:** Ley Orgánica de Protección de Datos Personales (LOPDP Ecuador) & Art. 66 Numeral 19 de la Constitución de la República del Ecuador.

---

## 1. Identificación del Responsable del Tratamiento
* **Razón Social:** VIAMATICA S.A.
* **RUC:** 0992446501001
* **Domicilio Social:** Nueve de Octubre y Córdova esquina, Edificio San Francisco 300, piso 16, oficina 1, Guayaquil, Ecuador.
* **Delegado de Protección de Datos (DPD):** `datoseguro@viamatica.com` | Teléfono: +593 (04) 2565634.

---

## 2. Declaración de Cumplimiento de AuraQx con la LOPDP y Políticas de Viamatica

AuraQx fue diseñado desde su concepción bajo los principios de **Privacidad desde el Diseño (Privacy by Design)** y **Privacidad por Defecto (Privacy by Default)**, alineándose estrictamente con los 13 principios de la LOPDP reconocidos por Viamatica S.A.:

| Principio LOPDP | Exigencia de Viamatica | Implementación Técnica en AuraQx |
| :--- | :--- | :--- |
| **Juridicidad y Lealtad** | Tratamiento bajo consentimiento y base contractual de seguros. | El procesamiento se activa únicamente ante la solicitud formal del asegurado/hospital para la gestión de pre-autorización de su póliza contratada. |
| **Transparencia** | Información clara al titular sobre el uso de sus datos. | Cada pre-autorización emitida detalla el desglose médico, financiero y el razonamiento clínico de aprobación o solicitud de faltantes. |
| **Pertinencia y Minimización** | Tratar únicamente datos estrictamente necesarios. | El extractor multimodal procesa únicamente los campos indispensables para la auditoría quirúrgica (identificación, CIE-10, CPT, hospital y vigencia), descartando datos no relacionados. |
| **Confidencialidad y Seguridad** | Custodia con altos estándares de seguridad y cifrado. | Autenticación robusta JWT (Access Token de 15 minutos, Refresh Token de 7 días con rotación), comunicación HTTPS forzada y almacenamiento seguro en Notion con permisos restringidos. |
| **Decisiones Automatizadas (Art. 8)** | **Garantizar el derecho del titular a objetar decisiones automatizadas y solicitar intervención humana.** | **AuraQx incorpora soporte nativo para "Human-in-the-Loop":** estado `EN_AUDITORIA_MANUAL`, explicabilidad clínica exhaustiva de cada rechazo o requerimiento, y canal de revisión por auditor médico. |
| **Conservación y Supresión** | Conservación solo durante el tiempo necesario para la finalidad. | Archivos temporales de procesamiento PDF son purgados tras la extracción; las resoluciones solo persisten metadatos anonimizables requeridos para la liquidación. |

---

## 3. Cláusula de Decisiones Automatizadas y Explicabilidad (IA)

En concordancia con el **Numeral 8 del Aviso de Viamatica S.A.** y el derecho del titular a **objetar decisiones automatizadas**:

1. **Razonabilidad Explicable:** El motor agéntico de AuraQx no opera como una caja negra. Cada evaluación contiene:
   * Detalle matemático del cálculo de carencias (días transcurridos vs meses contractuales exigidos).
   * Justificación clínica del checklist de protocolos quirúrgicos.
   * Reglas de cobertura arancelaria y deducibles contractuales.
2. **Derecho a Revisión Humana:** Si una solicitud recibe el estado `RECHAZADO` o `DOCUMENTOS_FALTANTES`, el sistema permite:
   * Subsanar interactivamente estudios pendientes con re-evaluación inmediata.
   * Solicitar la intervención directa de un médico auditor del seguro mediante el botón de derivación a auditoría manual.
   * Notificar formalmente al DPD a través de `datoseguro@viamatica.com`.

---

## 4. Texto Íntegro de la Política de Tratamiento de Datos de Viamatica S.A.

*(Reproducido de la publicación oficial para archivo y auditoría del HackIAthon)*

### 1. Responsable del Tratamiento
VIAMATICA S.A. con RUC 0992446501001 y domicilio social en Nueve de Octubre y Córdova esquina, Edificio San Francisco 300 piso 16 oficina 1, Guayaquil, Ecuador.

### 2. Delegado de Protección de Datos Personales
Canal de contacto: `datoseguro@viamatica.com` / +593 (04) 2565634.

### 3. Finalidades del Tratamiento
* **Clientes:** Gestión contractual de productos/servicios, cumplimiento normativo, prevención de fraudes, ofertas comerciales y comunicación con empresas del grupo.
* **Proveedores:** Calificación, instrumentación contractual, continuidad operativa y prevención de lavado de activos.
* **Colaboradores:** Selección, nómina, capacitación y salud ocupacional.

### 4. Base Legal
Constitución de la República del Ecuador (Art. 66 num. 19) y LOPDP (Art. 7 num. 1, 2, 3, 5, 7 y 8).

### 5. Consentimiento e Interés Legítimo
Otorgado mediante aceptación digital o inequívoca para finalidades legítimas y soluciones informáticas.

### 6. Conservación
Almacenamiento temporal limitado a la vigencia contractual y plazos de prescripción legal, procediendo luego a su eliminación o anonimización.

### 7. Derechos del Titular
Acceso, Rectificación/Actualización, Eliminación, Oposición, Suspensión, Portabilidad y **Objetar Decisiones Automatizadas**.

### 8. Decisiones Automatizadas
Tratamiento y perfilamiento automatizado con fines de mantenimiento, gestión, mejora de servicios e información técnica/comercial. El titular tiene derecho a solicitar intervención de un operador para explicar o impugnar decisiones.
