<script setup lang="ts">
import { ref } from 'vue'
import {
  BookOpen,
  Cpu,
  Database,
  FileCheck2,
  ShieldCheck,
  Zap,
  Activity,
  Stethoscope,
  Code2,
  Layers,
  FileText,
  Lock,
  ExternalLink,
  ChevronRight,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Scale
} from 'lucide-vue-next'

const activeTab = ref<'overview' | 'agent' | 'curing' | 'notion' | 'tech' | 'security'>('overview')

const tabs = [
  { id: 'overview', label: 'Visión & Reto 1', icon: BookOpen },
  { id: 'agent', label: 'Pipeline Agéntico & Carencias', icon: Cpu },
  { id: 'curing', label: 'Subsanación Asíncrona & OCR', icon: FileCheck2 },
  { id: 'notion', label: 'Integración Notion DB', icon: Database },
  { id: 'tech', label: 'Arquitectura & APIs', icon: Code2 },
  { id: 'security', label: 'Seguridad & Credenciales', icon: ShieldCheck },
]
</script>

<template>
  <div id="system-documentation" class="glass-panel rounded-3xl p-6 sm:p-8 border border-white/10 relative overflow-hidden">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-white/10">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-2xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shrink-0">
          <BookOpen class="w-5 h-5" />
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h2 class="text-lg font-black text-white tracking-wide">
              Documentación Técnica del Sistema
            </h2>
            <span class="px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-300 text-[10px] font-mono border border-cyan-500/30">
              ESPECIFICACIÓN RETO 1
            </span>
          </div>
          <p class="text-xs text-slate-400 mt-0.5">
            Arquitectura de software, fórmulas matemáticas de liquidación, reglas de carencia y contratos de API.
          </p>
        </div>
      </div>

      <!-- Quick stats badge -->
      <div class="flex items-center gap-2 font-mono text-[11px] text-slate-400 bg-slate-950/60 px-3 py-1.5 rounded-xl border border-white/5">
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
        <span>Viamatica & ADEN HackIAthon 2026</span>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="flex flex-wrap items-center gap-2 mb-6 border-b border-white/10 pb-3">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id as any"
        :class="[
          'px-3.5 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all cursor-pointer',
          activeTab === tab.id
            ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/40 shadow-[0_0_15px_rgba(56,189,248,0.2)]'
            : 'text-slate-400 hover:text-slate-200 hover:bg-white/5 border border-transparent'
        ]"
      >
        <component :is="tab.icon" class="w-4 h-4" />
        <span>{{ tab.label }}</span>
      </button>
    </div>

    <!-- Tab 1: Visión & Reto 1 -->
    <div v-if="activeTab === 'overview'" class="space-y-6 text-xs text-slate-300 leading-relaxed animate-fadeIn">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="p-5 rounded-2xl bg-slate-950/60 border border-white/10 space-y-3">
          <div class="flex items-center gap-2 text-rose-400 font-bold text-sm">
            <AlertTriangle class="w-4 h-4" />
            <span>El Problema Actual (Status Quo)</span>
          </div>
          <p class="text-slate-400">
            En el sistema hospitalario y asegurador tradicional, autorizar una cirugía programada toma de <strong>24 a 72 horas</strong>. El paciente y los cirujanos esperan mientras auditores revisan manualmente contratos de pólizas de cientos de páginas, causales de carencia y estudios clínicos. Esto genera cuellos de botella, reprogramaciones quirúrgicas y quejas de afiliados.
          </p>
          <div class="space-y-1.5 font-mono text-[11px] text-slate-400">
            <div class="flex items-center gap-2">❌ Tiempo de espera: 1 a 3 días</div>
            <div class="flex items-center gap-2">❌ Proceso manual sujeto a error humano</div>
            <div class="flex items-center gap-2">❌ Desinformación en copagos y deducibles</div>
          </div>
        </div>

        <div class="p-5 rounded-2xl bg-cyan-950/30 border border-cyan-500/30 space-y-3">
          <div class="flex items-center gap-2 text-cyan-400 font-bold text-sm">
            <Sparkles class="w-4 h-4" />
            <span>La Solución AuraQx (Reto 1)</span>
          </div>
          <p class="text-slate-300">
            Un <strong>Agente Autónomo de Pre-Autorización Quirúrgica en Tiempo Real</strong> que ingesta el informe médico digital (vía IBM Docling con OCR de alta fidelidad), consulta la base de datos de pólizas en <strong>Notion DB</strong>, audita períodos de carencia y emite la resolución en <strong>menos de 5 segundos</strong> con voucher holográfico y código QR.
          </p>
          <div class="space-y-1.5 font-mono text-[11px] text-emerald-400 font-semibold">
            <div class="flex items-center gap-2">✔ Tiempo de resolución: &lt; 5 segundos</div>
            <div class="flex items-center gap-2">✔ Validación estricta de carencia y estudios</div>
            <div class="flex items-center gap-2">✔ Sincronización en vivo con Notion DB</div>
          </div>
        </div>
      </div>

      <!-- Casos Clínicos Evaluables -->
      <div class="p-5 rounded-2xl bg-slate-950/50 border border-white/10 space-y-3">
        <h4 class="text-xs font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
          <Scale class="w-4 h-4 text-cyan-400" />
          Matriz de Casos Clínicos Oficiales para Evaluación
        </h4>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div class="p-3.5 rounded-xl bg-slate-900/80 border border-emerald-500/30 space-y-1.5">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-mono font-bold text-emerald-400">CASO ALFA</span>
              <span class="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[9px] font-bold">PRE-APROBADO</span>
            </div>
            <div class="font-bold text-white text-xs">Colecistectomía Laparoscópica</div>
            <p class="text-[11px] text-slate-400">María Mendoza (45a). Póliza con 18.5 meses (carencia 10m cumplida). 4/4 estudios adjuntos. Cobertura al 80%.</p>
          </div>

          <div class="p-3.5 rounded-xl bg-slate-900/80 border border-amber-500/30 space-y-1.5">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-mono font-bold text-amber-400">CASO BETA</span>
              <span class="px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[9px] font-bold">DOCUMENTOS FALTANTES</span>
            </div>
            <div class="font-bold text-white text-xs">Hernioplastia Inguinal</div>
            <p class="text-[11px] text-slate-400">Carlos Silva (48a). Carencia 14m cumplida. Faltan ecografía y riesgo quirúrgico (>=40a). Subsanable en vivo.</p>
          </div>

          <div class="p-3.5 rounded-xl bg-slate-900/80 border border-rose-500/30 space-y-1.5">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-mono font-bold text-rose-400">CASO GAMMA</span>
              <span class="px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300 text-[9px] font-bold">RECHAZADO</span>
            </div>
            <div class="font-bold text-white text-xs">Cesárea Programada</div>
            <p class="text-[11px] text-slate-400">Valeria Ramos (29a). Póliza con 3.5 meses. Carencia exigida para maternidad: 10 meses. Rechazo fundamentado.</p>
          </div>

          <div class="p-3.5 rounded-xl bg-slate-900/80 border border-cyan-500/30 space-y-1.5">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-mono font-bold text-cyan-400">CASO DELTA</span>
              <span class="px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 text-[9px] font-bold">EMERGENCIA VITAL</span>
            </div>
            <div class="font-bold text-white text-xs">Apendicectomía Urgente</div>
            <p class="text-[11px] text-slate-400">Juan Morales (34a). Póliza con 2 meses. Aplica Excepción de Emergencia Quirúrgica Vital (Carencia 0 Días).</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab 2: Pipeline Agéntico & Carencias -->
    <div v-else-if="activeTab === 'agent'" class="space-y-6 text-xs text-slate-300 leading-relaxed animate-fadeIn">
      <!-- 6 Pasos Agénticos -->
      <div class="space-y-3">
        <h4 class="text-xs font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
          <Layers class="w-4 h-4 text-cyan-400" />
          Pipeline Agéntico en 6 Fases (Streaming SSE en Tiempo Real)
        </h4>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <div class="p-4 rounded-xl bg-slate-950/60 border border-white/10 space-y-1.5">
            <div class="text-[10px] font-mono text-cyan-400 font-bold">PASO 1</div>
            <div class="font-bold text-slate-100 text-xs">Ingestión Multimodal IBM Docling</div>
            <p class="text-[11px] text-slate-400">Extracción de texto, tablas y metadatos clínicos de PDFs o imágenes escaneadas mediante fast-path digital o OCR multimodal profundo.</p>
          </div>

          <div class="p-4 rounded-xl bg-slate-950/60 border border-white/10 space-y-1.5">
            <div class="text-[10px] font-mono text-cyan-400 font-bold">PASO 2</div>
            <div class="font-bold text-slate-100 text-xs">Consulta de Póliza en Notion DB</div>
            <p class="text-[11px] text-slate-400">Búsqueda bidireccional por cédula en la base de datos de Notion. Verificación de estatus activo, antigüedad y red de prestadores.</p>
          </div>

          <div class="p-4 rounded-xl bg-slate-950/60 border border-white/10 space-y-1.5">
            <div class="text-[10px] font-mono text-cyan-400 font-bold">PASO 3</div>
            <div class="font-bold text-slate-100 text-xs">Auditoría Normativa de Carencia</div>
            <p class="text-[11px] text-slate-400">Cálculo exacto de meses transcurridos vs meses requeridos según patología, reconociendo excepciones inmediatas (0 días) para emergencias vitales.</p>
          </div>

          <div class="p-4 rounded-xl bg-slate-950/60 border border-white/10 space-y-1.5">
            <div class="text-[10px] font-mono text-cyan-400 font-bold">PASO 4</div>
            <div class="font-bold text-slate-100 text-xs">Auditoría de Requisitos Quirúrgicos</div>
            <p class="text-[11px] text-slate-400">Verificación de estudios diagnósticos obligatorios (ecografía abdominal, riesgo cardiológico ECG en mayores de 40 años, biometría, etc.).</p>
          </div>

          <div class="p-4 rounded-xl bg-slate-950/60 border border-white/10 space-y-1.5">
            <div class="text-[10px] font-mono text-cyan-400 font-bold">PASO 5</div>
            <div class="font-bold text-slate-100 text-xs">Liquidación Financiera Dinámica</div>
            <p class="text-[11px] text-slate-400">Cálculo algorítmico de deducible anual remanente, porcentaje de cobertura hospitalaria en red vs fuera de red y copago final del paciente.</p>
          </div>

          <div class="p-4 rounded-xl bg-slate-950/60 border border-white/10 space-y-1.5">
            <div class="text-[10px] font-mono text-cyan-400 font-bold">PASO 6</div>
            <div class="font-bold text-slate-100 text-xs">Emisión y Sincronización en Notion</div>
            <p class="text-[11px] text-slate-400">Generación del voucher con código QR criptográfico y escritura automática del caso en la base de datos de Notion con URL permanente.</p>
          </div>
        </div>
      </div>

      <!-- Fórmulas Matemáticas de Liquidación -->
      <div class="p-5 rounded-2xl bg-slate-950/70 border border-cyan-500/20 space-y-3">
        <h4 class="text-xs font-bold text-cyan-400 uppercase tracking-wider font-mono">
          Fórmulas Matemáticas de Liquidación y Desglose Financiero
        </h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-[11px] font-mono">
          <div class="p-3 rounded-xl bg-slate-900 border border-white/5 space-y-1">
            <div class="text-slate-400">1. Deducible Aplicado (USD)</div>
            <div class="text-cyan-300 font-bold">Deducible_Aplicado = min(Presupuesto, max(0, Deducible_Anual - Deducible_Pagado))</div>
          </div>
          <div class="p-3 rounded-xl bg-slate-900 border border-white/5 space-y-1">
            <div class="text-slate-400">2. Base Indemnizable (USD)</div>
            <div class="text-cyan-300 font-bold">Base_Indemnizable = max(0, Presupuesto - Deducible_Aplicado)</div>
          </div>
          <div class="p-3 rounded-xl bg-slate-900 border border-white/5 space-y-1">
            <div class="text-slate-400">3. Cobertura de la Aseguradora (USD)</div>
            <div class="text-emerald-300 font-bold">Aseguradora_Paga = Base_Indemnizable × (Cobertura_% / 100)</div>
          </div>
          <div class="p-3 rounded-xl bg-slate-900 border border-white/5 space-y-1">
            <div class="text-slate-400">4. Copago Total del Paciente (USD)</div>
            <div class="text-amber-300 font-bold">Copago_Paciente = Presupuesto - Aseguradora_Paga</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab 3: Subsanación Asíncrona & OCR -->
    <div v-else-if="activeTab === 'curing'" class="space-y-6 text-xs text-slate-300 leading-relaxed animate-fadeIn">
      <div class="p-5 rounded-2xl bg-slate-950/60 border border-amber-500/30 space-y-3">
        <div class="flex items-center gap-2 text-amber-400 font-bold text-sm">
          <FileCheck2 class="w-4 h-4" />
          <span>Mecanismo de Subsanación Asíncrona de Expedientes</span>
        </div>
        <p class="text-slate-300">
          Cuando un paciente cumple con la carencia contractual de su póliza pero el hospital no adjuntó todos los estudios complementarios obligatorios (ej. valoración cardiológica o ecografía específica), el caso no se rechaza: se clasifica como <strong>DOCUMENTOS_FALTANTES</strong>.
        </p>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2">
          <div class="p-3.5 rounded-xl bg-slate-900 border border-white/10 space-y-1.5">
            <div class="font-bold text-white text-xs">1. Preservación del Caso ID</div>
            <p class="text-[11px] text-slate-400">El número de solicitud único (ej. <code class="text-cyan-400">AUTH-2026-647F5A</code>) se mantiene idéntico entre todas las iteraciones para trazabilidad hospitalaria.</p>
          </div>
          <div class="p-3.5 rounded-xl bg-slate-900 border border-white/10 space-y-1.5">
            <div class="font-bold text-white text-xs">2. Carga de Archivos Propios</div>
            <p class="text-[11px] text-slate-400">Soporta carga real de documentos (PDF, fotos de celular de ecografías o ECGs) procesados mediante el endpoint <code class="text-cyan-400">/upload-missing-file</code>.</p>
          </div>
          <div class="p-3.5 rounded-xl bg-slate-900 border border-white/10 space-y-1.5">
            <div class="font-bold text-white text-xs">3. Transición Automática</div>
            <p class="text-[11px] text-slate-400">Una vez satisfechos todos los estudios faltantes, el estado pasa automáticamente a <strong>PRE-APROBADO</strong> con emisión de voucher oficial.</p>
          </div>
        </div>
      </div>

      <!-- Bandeja Asíncrona -->
      <div class="p-5 rounded-2xl bg-slate-950/60 border border-white/10 space-y-3">
        <h4 class="text-xs font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
          <Activity class="w-4 h-4 text-cyan-400" />
          Bandeja de Casos Incompletos para Clínicas
        </h4>
        <p class="text-slate-400">
          La mesa de ayuda o el auditor hospitalario puede consultar la bandeja de expedientes pendientes mediante <code class="text-cyan-400">GET /api/preauth/cases/incomplete</code>. Al pulsar "Subsanar Caso", los parámetros del reporte se recargan instantáneamente en pantalla permitiendo anexar los documentos que acaban de llegar del laboratorio o del servicio de cardiología.
        </p>
      </div>
    </div>

    <!-- Tab 4: Integración Notion DB -->
    <div v-else-if="activeTab === 'notion'" class="space-y-6 text-xs text-slate-300 leading-relaxed animate-fadeIn">
      <div class="p-5 rounded-2xl bg-slate-950/60 border border-cyan-500/20 space-y-3">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2 text-cyan-400 font-bold text-sm">
            <Database class="w-4 h-4" />
            <span>Arquitectura de Integración Dual con Notion</span>
          </div>
          <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
            RESILIENCIA 100%
          </span>
        </div>
        <p class="text-slate-300">
          AuraQx se conecta con dos bases de datos principales en Notion mediante el SDK oficial <code class="text-cyan-400">notion-client</code>, con un sistema de respaldo local inteligente en caso de micro-cortes o límites de tasa de la API de Notion.
        </p>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          <div class="p-4 rounded-xl bg-slate-900 border border-white/10 space-y-2">
            <div class="font-bold text-white text-xs flex items-center gap-2">
              <span class="w-2 h-2 rounded-full bg-cyan-400" />
              DB 1: Pólizas de Asegurados (Notion)
            </div>
            <ul class="space-y-1 text-[11px] text-slate-400 list-disc list-inside">
              <li><strong>ID Paciente / Cédula:</strong> Clave única de búsqueda (ej. 0928374102).</li>
              <li><strong>Vigencia y Antigüedad:</strong> Fecha de contratación para cómputo de carencias.</li>
              <li><strong>Plan Tier:</strong> Plan Oro (80%), Plata (75%), Esmeralda (85%).</li>
              <li><strong>Deducibles y Copagos:</strong> Deducible anual ($200-$250 USD) y acumulado.</li>
              <li><strong>Red Hospitalaria:</strong> Clínicas en red autorizadas para cobertura preferente.</li>
            </ul>
          </div>

          <div class="p-4 rounded-xl bg-slate-900 border border-white/10 space-y-2">
            <div class="font-bold text-white text-xs flex items-center gap-2">
              <span class="w-2 h-2 rounded-full bg-emerald-400" />
              DB 2: Registro de Pre-Autorizaciones (Notion)
            </div>
            <ul class="space-y-1 text-[11px] text-slate-400 list-disc list-inside">
              <li><strong>ID Solicitud:</strong> Código de voucher correlativo (AUTH-2026-XXXXXX).</li>
              <li><strong>Estado:</strong> Select con estados PRE_APROBADO, DOCUMENTOS_FALTANTES o RECHAZADO.</li>
              <li><strong>Valores Financieros:</strong> Columnas numéricas de Monto Cubierto y Copago Paciente.</li>
              <li><strong>Auditoría Médica:</strong> Justificación clínica formal con normativa y fundamento.</li>
              <li><strong>Enlace Permanente:</strong> URL pública en Notion para consulta de la clínica.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab 5: Arquitectura & APIs -->
    <div v-else-if="activeTab === 'tech'" class="space-y-6 text-xs text-slate-300 leading-relaxed animate-fadeIn">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 font-mono text-[11px]">
        <div class="p-3.5 rounded-xl bg-slate-950/60 border border-white/10 space-y-1">
          <div class="text-cyan-400 font-bold">FastAPI + uv</div>
          <p class="text-slate-400 text-[10px]">Backend asíncrono en Python 3.12 con empaquetador ultrarrápido uv y tipado estricto Pydantic v2.</p>
        </div>
        <div class="p-3.5 rounded-xl bg-slate-950/60 border border-white/10 space-y-1">
          <div class="text-emerald-400 font-bold">Nuxt 4 + Vite 8</div>
          <p class="text-slate-400 text-[10px]">Frontend SSR/SPA reactivo con Bun, Tailwind CSS v4, Glassmorphism y soporte PWA offline.</p>
        </div>
        <div class="p-3.5 rounded-xl bg-slate-950/60 border border-white/10 space-y-1">
          <div class="text-amber-400 font-bold">IBM Docling + PyPDF</div>
          <p class="text-slate-400 text-[10px]">Extracción multimodal de layout, tablas y OCR para informes médicos hospitalarios.</p>
        </div>
        <div class="p-3.5 rounded-xl bg-slate-950/60 border border-white/10 space-y-1">
          <div class="text-purple-400 font-bold">Dramatiq + Redis</div>
          <p class="text-slate-400 text-[10px]">Cola de tareas en segundo plano para extracción pesada sin bloquear endpoints HTTP.</p>
        </div>
      </div>

      <!-- Catálogo de Endpoints REST -->
      <div class="p-5 rounded-2xl bg-slate-950/60 border border-white/10 space-y-3">
        <h4 class="text-xs font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
          <Code2 class="w-4 h-4 text-cyan-400" />
          Especificación de Endpoints de la API
        </h4>
        <div class="space-y-2 font-mono text-[11px]">
          <div class="p-2.5 rounded-lg bg-slate-900 border border-white/5 flex items-center justify-between">
            <div>
              <span class="text-emerald-400 font-bold mr-2">POST</span>
              <span class="text-slate-200">/api/preauth/stream</span>
            </div>
            <span class="text-slate-500 text-[10px]">Server-Sent Events (SSE) en vivo (6 pasos)</span>
          </div>

          <div class="p-2.5 rounded-lg bg-slate-900 border border-white/5 flex items-center justify-between">
            <div>
              <span class="text-emerald-400 font-bold mr-2">POST</span>
              <span class="text-slate-200">/api/preauth/analyze</span>
            </div>
            <span class="text-slate-500 text-[10px]">Auditoría síncrona JSON con resolución y voucher</span>
          </div>

          <div class="p-2.5 rounded-lg bg-slate-900 border border-white/5 flex items-center justify-between">
            <div>
              <span class="text-emerald-400 font-bold mr-2">POST</span>
              <span class="text-slate-200">/api/preauth/upload-missing-file</span>
            </div>
            <span class="text-slate-500 text-[10px]">Multipart/form-data: subida de archivos reales con OCR</span>
          </div>

          <div class="p-2.5 rounded-lg bg-slate-900 border border-white/5 flex items-center justify-between">
            <div>
              <span class="text-cyan-400 font-bold mr-2">GET</span>
              <span class="text-slate-200">/api/preauth/cases/incomplete</span>
            </div>
            <span class="text-slate-500 text-[10px]">Lista de casos con documentos pendientes para subsanación</span>
          </div>

          <div class="p-2.5 rounded-lg bg-slate-900 border border-white/5 flex items-center justify-between">
            <div>
              <span class="text-purple-400 font-bold mr-2">POST</span>
              <span class="text-slate-200">/api/auth/login</span>
            </div>
            <span class="text-slate-500 text-[10px]">Autenticación JWT con refresh token de 7 días</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab 6: Seguridad & Credenciales -->
    <div v-else-if="activeTab === 'security'" class="space-y-6 text-xs text-slate-300 leading-relaxed animate-fadeIn">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Credenciales de Evaluación -->
        <div class="p-5 rounded-2xl bg-slate-950/60 border border-emerald-500/30 space-y-3">
          <div class="flex items-center gap-2 text-emerald-400 font-bold text-sm">
            <ShieldCheck class="w-4 h-4" />
            <span>Credenciales de Prueba para Evaluadores</span>
          </div>
          <p class="text-slate-400 text-xs">
            Para comodidad del jurado, la plataforma inicia sesión automáticamente con credenciales de auditor clínico. Si desea iniciar sesión manualmente:
          </p>
          <div class="p-3 rounded-xl bg-slate-900 border border-white/10 font-mono text-[11px] space-y-1">
            <div class="flex justify-between">
              <span class="text-slate-400">Usuario:</span>
              <span class="text-cyan-300 font-bold">auditor_clinico</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">Contraseña:</span>
              <span class="text-cyan-300 font-bold">hackiathon2026</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">Rol:</span>
              <span class="text-emerald-300 font-bold">Auditor Médico y Quirúrgico</span>
            </div>
          </div>
        </div>

        <!-- Protección de Datos y Cumplimiento LOPDP -->
        <div class="p-5 rounded-2xl bg-slate-950/60 border border-cyan-500/30 space-y-3">
          <div class="flex items-center gap-2 text-cyan-400 font-bold text-sm">
            <Lock class="w-4 h-4" />
            <span>Privacidad y Cumplimiento Normativo (LOPDP)</span>
          </div>
          <p class="text-slate-400 text-xs">
            AuraQx incorpora salvaguardas de conformidad con la Ley Orgánica de Protección de Datos Personales (LOPDP) para el tratamiento de datos sensibles de salud:
          </p>
          <ul class="space-y-1 text-[11px] text-slate-300 list-disc list-inside">
            <li>Tokens Bearer JWT seguros con expiración corta (15 min) y renovación controlada.</li>
            <li>Anonimización de transcripciones OCR de historias clínicas.</li>
            <li>Trazabilidad inmutable de firmas y resoluciones emitidas.</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>
