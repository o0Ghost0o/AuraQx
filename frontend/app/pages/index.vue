<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  Sparkles,
  Zap,
  Play,
  RotateCcw,
  FileCheck2,
  Stethoscope,
  Activity,
  AlertCircle,
  Building,
  DollarSign,
  User,
  Clock,
  Shield
} from 'lucide-vue-next'

const { fetchWithAuth, token, apiBase } = useAuth()

// Estado
const demoCases = ref<any[]>([])
const selectedCase = ref<any | null>(null)
const currentReport = ref<any>({
  patient_name: 'María Carmen Mendoza',
  patient_id: '0928374102',
  patient_age: 45,
  patient_gender: 'F',
  hospital_name: 'Hospital Metropolitano',
  treating_physician: 'Dr. Fernando Morales',
  diagnosis_icd10: 'K80.2 - Calculosis de la vesícula biliar sin colecistitis',
  procedure_name: 'Colecistectomía laparoscópica',
  procedure_cpt: '47562',
  urgency: 'ELECTIVA',
  request_date: new Date().toISOString().split('T')[0],
  estimated_cost: 2800.0,
  clinical_summary: 'Paciente con dolor cólico en hipocondrio derecho postprandial. Ecografía confirma litos vesiculares.',
  attachments: [
    { name: 'Ecografía Abdomen', doc_type: 'ecografia', is_present: true },
    { name: 'Laboratorio y Coagulación', doc_type: 'laboratorio', is_present: true },
    { name: 'Riesgo Cardiológico', doc_type: 'riesgo_quirurgico', is_present: true },
    { name: 'Presupuesto Quirúrgico', doc_type: 'presupuesto', is_present: true },
  ],
})

// Telemetría SSE
const isAnalyzing = ref(false)
const currentStep = ref(0)
const telemetryEvents = ref<any[]>([])
const resolution = ref<any | null>(null)
const errorAlert = ref<string | null>(null)
const incompleteTableRef = ref<any | null>(null)

// Cargar casos de demo
onMounted(async () => {
  try {
    const cases = await fetchWithAuth<any[]>('/api/demo/cases')
    demoCases.value = cases
    if (cases.length > 0) {
      selectCase(cases[0])
    }
  } catch (err) {
    console.error('Error fetching demo cases:', err)
  }
})

const selectCase = (caseItem: any) => {
  selectedCase.value = caseItem
  currentReport.value = JSON.parse(JSON.stringify(caseItem.report))
  resolution.value = null
  telemetryEvents.value = []
  currentStep.value = 0
  errorAlert.value = null
}

const handleDoclingUpload = (res: any) => {
  resolution.value = res
  currentStep.value = 6
  telemetryEvents.value = [
    {
      step: 1,
      title: 'Extracción Multimodal IBM Docling',
      status: 'success',
      detail: `Documento procesado. Paciente: ${res.patient_name} (${res.patient_id})`,
      timestamp: new Date().toLocaleTimeString(),
    },
    {
      step: 6,
      title: `Resolución Emitida: ${res.status}`,
      status: res.status === 'PRE_APROBADO' ? 'success' : 'warning',
      detail: `Caso ${res.case_id} emitido. Cobertura: ${res.financials.coverage_percent}%`,
      timestamp: new Date().toLocaleTimeString(),
    },
  ]
}

// Procesar documento directamente desde el paquete descargable
const handleProcessDocFromPackage = async (docUrl: string, fileName: string) => {
  try {
    isAnalyzing.value = true
    errorAlert.value = null
    const fileRes = await fetch(docUrl)
    const blob = await fileRes.blob()
    const file = new File([blob], fileName, { type: 'application/pdf' })

    const formData = new FormData()
    formData.append('file', file)
    formData.append('patient_id', currentReport.value.patient_id)

    const res = await fetchWithAuth<any>('/api/preauth/analyze-upload', {
      method: 'POST',
      body: formData,
    })

    handleDoclingUpload(res)
  } catch (err: any) {
    console.error('Error processing document from package:', err)
    errorAlert.value = err.data?.detail || 'Error procesando documento del paquete'
  } finally {
    isAnalyzing.value = false
  }
}

// Ejecutar pipeline agéntico con streaming SSE
const runPreauthAnalysis = async () => {
  isAnalyzing.value = true
  resolution.value = null
  telemetryEvents.value = []
  currentStep.value = 1
  errorAlert.value = null

  try {
    const response = await fetch(`${apiBase}/api/preauth/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: token.value ? `Bearer ${token.value}` : '',
      },
      body: JSON.stringify(currentReport.value),
    })

    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status}`)
    }

    const reader = response.body?.getReader()
    if (!reader) throw new Error('No readable stream')

    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.replace('data: ', ''))
            if (data.telemetry) {
              telemetryEvents.value.push(data.telemetry)
              currentStep.value = data.telemetry.step
            }
            if (data.payload) {
              resolution.value = data.payload
            }
          } catch (e) {
            console.error('Error parsing SSE line:', e)
          }
        }
      }
    }
  } catch (err: any) {
    console.error('Error in agent streaming:', err)
    errorAlert.value = err.message || 'Error en el pipeline agéntico'
  } finally {
    isAnalyzing.value = false
    incompleteTableRef.value?.fetchIncompleteCases()
  }
}

// Subsanar documento faltante en vivo (1-Click)
const handleResolveMissingDoc = async (docType: string, fileName: string) => {
  try {
    const payload = {
      ...currentReport.value,
      case_id: resolution.value?.case_id,
      resolved_doc_type: docType,
      uploaded_file_name: fileName,
    }

    const updatedRes = await fetchWithAuth<any>('/api/preauth/submit-missing-doc', {
      method: 'POST',
      body: payload,
    })

    resolution.value = updatedRes

    // Actualizar y acumular en el reporte actual para evitar pérdida en subsanaciones posteriores
    let found = false
    for (const att of currentReport.value.attachments) {
      if (att.doc_type.toLowerCase() === docType.toLowerCase()) {
        att.is_present = true
        att.name = fileName
        found = true
      }
    }
    if (!found) {
      currentReport.value.attachments.push({
        name: fileName,
        doc_type: docType,
        is_present: true,
      })
    }

    telemetryEvents.value.push({
      step: 6,
      title: 'Documento Subsanado en Tiempo Real',
      status: updatedRes.status === 'PRE_APROBADO' ? 'success' : 'warning',
      detail: `Se adjuntó ${fileName}. Nueva resolución: ${updatedRes.status}`,
      timestamp: new Date().toLocaleTimeString(),
    })

    incompleteTableRef.value?.fetchIncompleteCases()
  } catch (err: any) {
    console.error('Error resolving missing document:', err)
  }
}

// Subsanar subiendo un archivo propio (PDF o Imagen)
const handleUploadRealMissingFile = async (docType: string, file: File) => {
  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('case_id', resolution.value?.case_id || '')
    formData.append('patient_id', currentReport.value.patient_id)
    formData.append('doc_type', docType)
    formData.append('report_json', JSON.stringify(currentReport.value))

    const updatedRes = await fetchWithAuth<any>('/api/preauth/upload-missing-file', {
      method: 'POST',
      body: formData,
    })

    resolution.value = updatedRes

    // Acumular en el reporte actual
    let found = false
    for (const att of currentReport.value.attachments) {
      if (att.doc_type.toLowerCase() === docType.toLowerCase()) {
        att.is_present = true
        att.name = file.name
        found = true
      }
    }
    if (!found) {
      currentReport.value.attachments.push({
        name: file.name,
        doc_type: docType,
        is_present: true,
      })
    }

    telemetryEvents.value.push({
      step: 6,
      title: 'Archivo Propio Auditado por Docling',
      status: updatedRes.status === 'PRE_APROBADO' ? 'success' : 'warning',
      detail: `Se procesó ${file.name}. Nueva resolución: ${updatedRes.status}`,
      timestamp: new Date().toLocaleTimeString(),
    })

    incompleteTableRef.value?.fetchIncompleteCases()
  } catch (err: any) {
    console.error('Error uploading missing file:', err)
  }
}

// Seleccionar un caso incompleto de la bandeja asíncrona
const handleSelectIncompleteCase = (caseItem: any) => {
  resolution.value = caseItem
  const matched = demoCases.value.find((c: any) => c.report?.patient_id === caseItem.patient_id)
  if (matched) {
    selectedCase.value = matched
    currentReport.value = JSON.parse(JSON.stringify(matched.report))
  } else {
    currentReport.value = {
      patient_name: caseItem.patient_name,
      patient_id: caseItem.patient_id,
      patient_age: 48,
      patient_gender: 'M',
      hospital_name: caseItem.hospital_name,
      treating_physician: 'Dr. Médico Tratante',
      diagnosis_icd10: 'Diagnóstico Quirúrgico',
      procedure_name: caseItem.procedure_name,
      procedure_cpt: '49505',
      urgency: 'ELECTIVA',
      request_date: caseItem.request_date || new Date().toISOString().split('T')[0],
      estimated_cost: caseItem.financials?.estimated_total || 2100.0,
      clinical_summary: caseItem.clinical_justification || '',
      attachments: [],
    }
  }

  window.scrollTo({ top: 350, behavior: 'smooth' })
}
</script>

<template>
  <div class="space-y-6 animate-fadeIn">
    <!-- Hero Header -->
    <div class="glass-panel rounded-3xl p-6 sm:p-8 border border-white/10 relative overflow-hidden">
      <div class="absolute -right-16 -top-16 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
      
      <div class="max-w-3xl">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/15 border border-cyan-500/30 text-cyan-300 text-xs font-mono mb-3">
          <Zap class="w-3.5 h-3.5 animate-pulse" />
          <span>Viamatica & ADEN HackIAthon 2026 • Reto 1</span>
        </div>
        <h1 class="text-2xl sm:text-4xl font-black text-white tracking-tight leading-tight mb-2">
          Agente de Pre-Autorización Quirúrgica en <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-400 to-emerald-400">Tiempo Real</span>
        </h1>
        <p class="text-xs sm:text-sm text-slate-400 leading-relaxed">
          De días de espera a segundos de certeza. Ingesta el informe médico con <strong>IBM Docling</strong>, consulta la póliza en <strong>Notion DB</strong>, audita períodos de carencia y emite la pre-aprobación o checklist de faltantes de forma instantánea.
        </p>
      </div>
    </div>

    <!-- 1-Click Demo Selector Bar -->
    <GlassCard>
      <CaseSelector
        :cases="demoCases"
        :selected-case-id="selectedCase?.id || null"
        @select="selectCase"
      />
    </GlassCard>

    <!-- Main Working Grid: Clinical Form & Ingestion vs Telemetry & Voucher -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      <!-- Columna Izquierda: Formulario Quirúrgico & Docling Uploader (5 cols) -->
      <div class="lg:col-span-5 space-y-5">
        <!-- Subida Multimodal con IBM Docling -->
        <GlassCard>
          <div class="flex items-center gap-2 mb-3">
            <Stethoscope class="w-4 h-4 text-cyan-400" />
            <h3 class="text-xs font-bold uppercase tracking-wider text-slate-200">Ingestión de Documento Clínico</h3>
          </div>
          <DocumentDropzone @file-uploaded="handleDoclingUpload" />
        </GlassCard>

        <!-- Expediente del Caso & Paquete Descargable (.ZIP) -->
        <CasePackageViewer
          :selected-case="selectedCase"
          @process-doc="handleProcessDocFromPackage"
        />

        <!-- Formulario Clínico Parametrizable -->
        <GlassCard>
          <div class="flex items-center justify-between mb-4 pb-3 border-b border-white/10">
            <div class="flex items-center gap-2">
              <Activity class="w-4 h-4 text-cyan-400" />
              <h3 class="text-xs font-bold uppercase tracking-wider text-slate-200">Datos del Informe Médico</h3>
            </div>
            <span class="text-[10px] font-mono text-cyan-400">{{ currentReport.urgency }}</span>
          </div>

          <div class="space-y-3.5 text-xs">
            <!-- Paciente y Cédula -->
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-slate-400 text-[11px] mb-1 font-mono">Nombre Paciente</label>
                <input
                  v-model="currentReport.patient_name"
                  type="text"
                  class="w-full px-3 py-2 rounded-xl glass-input text-xs"
                />
              </div>
              <div>
                <label class="block text-slate-400 text-[11px] mb-1 font-mono">Cédula / ID Notion</label>
                <input
                  v-model="currentReport.patient_id"
                  type="text"
                  class="w-full px-3 py-2 rounded-xl glass-input text-xs font-mono text-cyan-300 font-bold"
                />
              </div>
            </div>

            <!-- Edad y Género -->
            <div class="grid grid-cols-3 gap-3">
              <div>
                <label class="block text-slate-400 text-[11px] mb-1 font-mono">Edad</label>
                <input
                  v-model.number="currentReport.patient_age"
                  type="number"
                  class="w-full px-3 py-2 rounded-xl glass-input text-xs"
                />
              </div>
              <div>
                <label class="block text-slate-400 text-[11px] mb-1 font-mono">Género</label>
                <select
                  v-model="currentReport.patient_gender"
                  class="w-full px-3 py-2 rounded-xl glass-input text-xs bg-slate-900"
                >
                  <option value="F">Femenino</option>
                  <option value="M">Masculino</option>
                </select>
              </div>
              <div>
                <label class="block text-slate-400 text-[11px] mb-1 font-mono">Urgencia</label>
                <select
                  v-model="currentReport.urgency"
                  class="w-full px-3 py-2 rounded-xl glass-input text-xs bg-slate-900"
                >
                  <option value="ELECTIVA">ELECTIVA</option>
                  <option value="URGENCIA">URGENCIA</option>
                  <option value="EMERGENCIA_VITAL">EMERGENCIA</option>
                </select>
              </div>
            </div>

            <!-- Diagnóstico CIE-10 -->
            <div>
              <label class="block text-slate-400 text-[11px] mb-1 font-mono">Diagnóstico CIE-10</label>
              <input
                v-model="currentReport.diagnosis_icd10"
                type="text"
                class="w-full px-3 py-2 rounded-xl glass-input text-xs"
              />
            </div>

            <!-- Procedimiento Quirúrgico Propuesto -->
            <div>
              <label class="block text-slate-400 text-[11px] mb-1 font-mono">Cirugía Solicitada</label>
              <input
                v-model="currentReport.procedure_name"
                type="text"
                class="w-full px-3 py-2 rounded-xl glass-input text-xs font-semibold text-slate-100"
              />
            </div>

            <!-- Hospital y Presupuesto -->
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-slate-400 text-[11px] mb-1 font-mono">Hospital Solicitante</label>
                <input
                  v-model="currentReport.hospital_name"
                  type="text"
                  class="w-full px-3 py-2 rounded-xl glass-input text-xs"
                />
              </div>
              <div>
                <label class="block text-slate-400 text-[11px] mb-1 font-mono">Presupuesto (USD)</label>
                <input
                  v-model.number="currentReport.estimated_cost"
                  type="number"
                  class="w-full px-3 py-2 rounded-xl glass-input text-xs font-mono text-emerald-300 font-bold"
                />
              </div>
            </div>

            <!-- Estudios Adjuntos Checklist -->
            <div>
              <label class="block text-slate-400 text-[11px] mb-1.5 font-mono">Estudios Prequirúrgicos Adjuntos</label>
              <div class="grid grid-cols-2 gap-2">
                <label
                  v-for="att in currentReport.attachments"
                  :key="att.doc_type"
                  class="flex items-center gap-2 p-2 rounded-lg bg-slate-950/60 border border-white/5 cursor-pointer hover:border-white/20 transition-all text-[11px]"
                >
                  <input
                    type="checkbox"
                    v-model="att.is_present"
                    class="rounded bg-slate-800 border-white/20 text-cyan-500 focus:ring-0"
                  />
                  <span :class="att.is_present ? 'text-slate-200 font-medium' : 'text-slate-500 line-through'">
                    {{ att.name }}
                  </span>
                </label>
              </div>
            </div>

            <!-- Botón de Ejecución Principal -->
            <button
              @click="runPreauthAnalysis"
              :disabled="isAnalyzing"
              class="w-full mt-2 py-3 rounded-xl bg-gradient-to-r from-cyan-500 via-blue-600 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-slate-950 font-black text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-[0_0_25px_rgba(56,189,248,0.35)] transition-all disabled:opacity-50"
            >
              <Sparkles class="w-4 h-4" :class="{ 'animate-spin': isAnalyzing }" />
              <span>{{ isAnalyzing ? 'Auditando Carencias y Póliza...' : 'Iniciar Pre-Autorización Quirúrgica' }}</span>
            </button>
          </div>
        </GlassCard>
      </div>

      <!-- Columna Derecha: Telemetría Radar, Voucher Holográfico y Portal de Faltantes (7 cols) -->
      <div class="lg:col-span-7 space-y-6">
        <!-- Error Alert -->
        <div v-if="errorAlert" class="p-4 rounded-xl bg-rose-500/20 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-2.5">
          <AlertCircle class="w-5 h-5 shrink-0" />
          <span>{{ errorAlert }}</span>
        </div>

        <!-- Radar de Telemetría Agéntica SSE -->
        <AgentTelemetryRadar
          :events="telemetryEvents"
          :current-step="currentStep"
          :is-running="isAnalyzing"
        />

        <!-- Voucher Holográfico de Resolución -->
        <HolographicVoucher
          v-if="resolution"
          :resolution="resolution"
        />

        <!-- Portal de Documentos Faltantes (Si aplica) -->
        <MissingDocsPortal
          v-if="resolution && resolution.status === 'DOCUMENTOS_FALTANTES'"
          :missing-docs="resolution.missing_documents"
          :current-report="currentReport"
          @resolve-doc="handleResolveMissingDoc"
          @upload-file="handleUploadRealMissingFile"
        />
      </div>
    </div>

    <!-- Bandeja de Casos Quirúrgicos Incompletos / Por Subsanar (Asíncrono) -->
    <IncompleteCasesTable
      ref="incompleteTableRef"
      @select-case="handleSelectIncompleteCase"
      class="mt-8"
    />
  </div>
</template>
