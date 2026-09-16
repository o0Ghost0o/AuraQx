<script setup lang="ts">
import { ref } from 'vue'
import { AlertTriangle, UploadCloud, FileUp, Sparkles, Download, CheckCircle2, Loader2 } from 'lucide-vue-next'

const props = defineProps<{
  missingDocs: any[]
  currentReport: any
}>()

const emit = defineEmits<{
  (e: 'resolve-doc', resolvedDocType: string, fileName: string): void
  (e: 'upload-file', docType: string, file: File): void
}>()

const uploadingDoc = ref<string | null>(null)
const uploadingType = ref<'quick' | 'custom' | null>(null)
const fileInputs = ref<Record<string, HTMLInputElement | null>>({})

const handleQuickResolve = (docType: string, title: string) => {
  uploadingDoc.value = docType
  uploadingType.value = 'quick'
  setTimeout(() => {
    emit('resolve-doc', docType, `${title.replace(/\s+/g, '_')}_Firmado.pdf`)
    uploadingDoc.value = null
    uploadingType.value = null
  }, 600)
}

const triggerFileInput = (docType: string) => {
  const input = fileInputs.value[docType]
  if (input) {
    input.click()
  }
}

const onFileSelected = (docType: string, event: Event) => {
  const target = event.target as HTMLInputElement
  if (target && target.files && target.files[0]) {
    const file = target.files[0]
    uploadingDoc.value = docType
    uploadingType.value = 'custom'
    emit('upload-file', docType, file)
    target.value = ''
    setTimeout(() => {
      uploadingDoc.value = null
      uploadingType.value = null
    }, 1500)
  }
}
</script>

<template>
  <div class="glass-panel glow-amber rounded-2xl p-6 border border-amber-500/40 relative overflow-hidden">
    <div class="flex items-center gap-3 mb-4 pb-3 border-b border-amber-500/20">
      <div class="w-9 h-9 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400">
        <AlertTriangle class="w-5 h-5 animate-pulse" />
      </div>
      <div>
        <h3 class="text-sm font-bold text-white tracking-wide flex items-center gap-2">
          Portal de Subsanación de Documentos Faltantes
          <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">
            ACCIÓN REQUERIDA
          </span>
        </h3>
        <p class="text-xs text-slate-400">
          La póliza tiene carencia cumplida, pero faltan {{ missingDocs.length }} estudio(s) obligatorio(s) para emitir el voucher definitivo.
        </p>
      </div>
    </div>

    <div class="space-y-3 mb-5">
      <div
        v-for="doc in missingDocs"
        :key="doc.doc_type"
        class="p-4 rounded-xl bg-slate-950/70 border border-amber-500/20 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 transition-all hover:border-amber-500/40"
      >
        <div class="flex-1">
          <div class="flex items-center gap-2 mb-1">
            <span class="text-xs font-bold text-slate-200">{{ doc.title }}</span>
            <span class="text-[10px] font-mono px-1.5 py-0.2 rounded bg-rose-500/20 text-rose-300 font-bold">OBLIGATORIO</span>
          </div>
          <p class="text-[11px] text-slate-400 mb-1 leading-relaxed">
            <strong class="text-slate-300">Justificación Médica:</strong> {{ doc.medical_rationale }}
          </p>
          <span class="text-[10px] font-mono text-cyan-400">Acción requerida: {{ doc.suggested_action }}</span>
        </div>

        <div class="flex flex-wrap items-center gap-2 shrink-0">
          <!-- Input oculto para carga de archivo real -->
          <input
            type="file"
            :ref="(el) => { if (el) fileInputs[doc.doc_type] = el as HTMLInputElement }"
            class="hidden"
            accept=".pdf,.png,.jpg,.jpeg,.doc,.docx"
            @change="onFileSelected(doc.doc_type, $event)"
          />

          <!-- Botón de subir archivo propio -->
          <button
            @click="triggerFileInput(doc.doc_type)"
            :disabled="uploadingDoc === doc.doc_type"
            class="px-3 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-cyan-300 border border-cyan-500/40 hover:border-cyan-400 font-semibold text-xs flex items-center gap-1.5 shadow-sm transition-all disabled:opacity-50"
            title="Subir archivo propio (PDF o imagen escaneada)"
          >
            <Loader2 v-if="uploadingDoc === doc.doc_type && uploadingType === 'custom'" class="w-3.5 h-3.5 animate-spin text-cyan-400" />
            <FileUp v-else class="w-3.5 h-3.5 text-cyan-400" />
            <span>{{ uploadingDoc === doc.doc_type && uploadingType === 'custom' ? 'Analizando Archivo...' : 'Subir Archivo Propio' }}</span>
          </button>

          <!-- Botón de subsanación rápida 1-click -->
          <button
            @click="handleQuickResolve(doc.doc_type, doc.title)"
            :disabled="uploadingDoc === doc.doc_type"
            class="px-3.5 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-400 hover:to-yellow-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 shadow-[0_0_15px_rgba(245,158,11,0.3)] transition-all disabled:opacity-50"
          >
            <Loader2 v-if="uploadingDoc === doc.doc_type && uploadingType === 'quick'" class="w-3.5 h-3.5 animate-spin text-slate-950" />
            <UploadCloud v-else class="w-3.5 h-3.5" />
            <span>{{ uploadingDoc === doc.doc_type && uploadingType === 'quick' ? 'Auditando...' : 'Subsanar Rápido' }}</span>
          </button>
        </div>
      </div>
    </div>

    <div class="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-[11px] text-amber-300 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
      <div class="flex items-center gap-2">
        <Sparkles class="w-4 h-4 shrink-0 text-amber-400" />
        <span>Al adjuntar todos los documentos faltantes, el agente recalculará la resolución de inmediato a <strong>PRE-APROBADO</strong>.</span>
      </div>
      <a
        href="/case_packages/case-beta/05_FALTANTE_A_SUBIR_Riesgo_Cardiologico_Silva.pdf"
        download="05_FALTANTE_A_SUBIR_Riesgo_Cardiologico_Silva.pdf"
        class="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/30 text-[10px] font-mono shrink-0 transition-all font-semibold"
        title="Descargar documento faltante de prueba del Caso Beta"
      >
        <Download class="w-3.5 h-3.5" />
        <span>Descargar PDF de Prueba</span>
      </a>
    </div>
  </div>
</template>
