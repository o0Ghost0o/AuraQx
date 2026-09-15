<script setup lang="ts">
import {
  Download,
  FolderArchive,
  FileText,
  FileCheck2,
  ExternalLink,
  Sparkles,
  Zap,
  Shield,
  Eye
} from 'lucide-vue-next'

const props = defineProps<{
  selectedCase: any | null
}>()

const emit = defineEmits<{
  (e: 'process-doc', docUrl: string, fileName: string): void
}>()

const { apiBase } = useAuth()

const getDocTypeBadge = (docType: string) => {
  switch (docType) {
    case 'informe_medico':
      return { label: 'INFORME MÉDICO', color: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30' }
    case 'poliza':
      return { label: 'PÓLIZA NOTION', color: 'bg-purple-500/15 text-purple-300 border-purple-500/30' }
    case 'ecografia':
      return { label: 'IMAGENOLOGÍA', color: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30' }
    case 'laboratorio':
      return { label: 'LABORATORIO', color: 'bg-blue-500/15 text-blue-300 border-blue-500/30' }
    case 'riesgo_quirurgico':
      return { label: 'RIESGO CARDIOLÓGICO', color: 'bg-rose-500/15 text-rose-300 border-rose-500/30' }
    case 'presupuesto':
      return { label: 'PRESUPUESTO', color: 'bg-amber-500/15 text-amber-300 border-amber-500/30' }
    default:
      return { label: 'DOCUMENTO', color: 'bg-slate-500/15 text-slate-300 border-slate-500/30' }
  }
}
</script>

<template>
  <div v-if="selectedCase && selectedCase.package" class="glass-panel rounded-2xl p-5 border border-white/10 relative overflow-hidden">
    <!-- Header del Paquete -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-white/10 mb-4">
      <div>
        <div class="flex items-center gap-2">
          <FolderArchive class="w-4 h-4 text-cyan-400" />
          <h3 class="text-xs font-bold uppercase tracking-wider text-slate-100">
            Expediente del Caso & Paquete Descargable (.ZIP)
          </h3>
        </div>
        <p class="text-[11px] text-slate-400 mt-0.5">
          {{ selectedCase.case_title }} • {{ selectedCase.package.documents?.length || 0 }} documentos clínicos
        </p>
      </div>

      <!-- Botón de Descarga ZIP del Caso -->
      <div class="flex items-center gap-2">
        <a
          :href="selectedCase.package.zip_url"
          :download="selectedCase.package.zip_filename"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-black text-xs shadow-[0_0_15px_rgba(56,189,248,0.25)] transition-all shrink-0"
        >
          <Download class="w-3.5 h-3.5" />
          <span>Descargar Paquete ZIP</span>
        </a>
      </div>
    </div>

    <!-- Lista de Documentos del Paquete -->
    <div class="space-y-2">
      <div
        v-for="doc in selectedCase.package.documents"
        :key="doc.filename"
        class="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 p-2.5 rounded-xl bg-slate-950/50 border border-white/5 hover:border-white/15 transition-all text-xs"
      >
        <div class="flex items-center gap-2.5 min-w-0">
          <div class="w-8 h-8 rounded-lg bg-slate-800 border border-white/10 flex items-center justify-center text-cyan-400 shrink-0">
            <FileText class="w-4 h-4" />
          </div>
          <div class="min-w-0">
            <div class="flex items-center gap-2">
              <span class="font-bold text-slate-200 truncate">{{ doc.title }}</span>
              <span :class="['text-[9px] font-mono px-1.5 py-0.5 rounded border', getDocTypeBadge(doc.doc_type).color]">
                {{ getDocTypeBadge(doc.doc_type).label }}
              </span>
            </div>
            <span class="text-[10px] text-slate-500 font-mono block truncate">{{ doc.filename }}</span>
          </div>
        </div>

        <div class="flex items-center gap-2 self-end sm:self-center shrink-0">
          <!-- Botón de procesar con Docling si es el informe primario -->
          <button
            v-if="doc.is_primary"
            @click="emit('process-doc', doc.url, doc.filename)"
            class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[10px] font-semibold bg-cyan-500/15 hover:bg-cyan-500/25 text-cyan-300 border border-cyan-500/30 transition-all"
            title="Procesar directamente con Docling y Dramatiq"
          >
            <Zap class="w-3 h-3 text-cyan-400" />
            <span>Procesar PDF</span>
          </button>

          <!-- Botón Descarga Individual -->
          <a
            :href="doc.url"
            :download="doc.filename"
            class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[10px] font-medium bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white border border-white/10 transition-all"
            title="Descargar PDF"
          >
            <Download class="w-3 h-3 text-slate-400" />
            <span>PDF</span>
          </a>

          <!-- Botón Visualizar en nueva pestaña -->
          <a
            :href="doc.url"
            target="_blank"
            class="p-1 rounded-lg hover:bg-white/10 text-slate-400 hover:text-cyan-300 transition-colors"
            title="Abrir en visor del navegador"
          >
            <Eye class="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </div>

    <!-- Muestra de Documento Faltante para Subsanar (Si aplica) -->
    <div
      v-if="selectedCase.package.missing_doc_sample"
      class="mt-3.5 p-3 rounded-xl bg-amber-500/10 border border-amber-500/25 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5 text-xs"
    >
      <div class="flex items-center gap-2">
        <Sparkles class="w-4 h-4 text-amber-400 shrink-0 animate-pulse" />
        <div>
          <span class="font-bold text-amber-200">Archivo de Prueba para Subsanación:</span>
          <p class="text-[11px] text-slate-400">
            Descarga este estudio cardiológico para probar el flujo de subsanación interactivo.
          </p>
        </div>
      </div>

      <a
        :href="selectedCase.package.missing_doc_sample.url"
        :download="selectedCase.package.missing_doc_sample.filename"
        class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 text-[11px] font-semibold transition-all shrink-0"
      >
        <Download class="w-3.5 h-3.5" />
        <span>Descargar Riesgo_Cardiologico.pdf</span>
      </a>
    </div>
  </div>
</template>
