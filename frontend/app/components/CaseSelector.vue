<script setup lang="ts">
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Zap,
  Sparkles,
  Download,
  FolderArchive,
  FileText
} from 'lucide-vue-next'

const emit = defineEmits<{
  (e: 'select', caseItem: any): void
}>()

const props = defineProps<{
  cases: any[]
  selectedCaseId: string | null
}>()

const { apiBase } = useAuth()

const getCaseIcon = (badge: string) => {
  if (badge.includes('Exitosa')) return CheckCircle2
  if (badge.includes('Faltantes')) return AlertTriangle
  if (badge.includes('Carencia')) return XCircle
  return Zap
}

const getBadgeClasses = (badge: string) => {
  if (badge.includes('Exitosa')) return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
  if (badge.includes('Faltantes')) return 'bg-amber-500/15 text-amber-400 border-amber-500/30'
  if (badge.includes('Carencia')) return 'bg-rose-500/15 text-rose-400 border-rose-500/30'
  return 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30'
}
</script>

<template>
  <div class="w-full">
    <!-- Encabezado con selector y botón master bundle -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 mb-3">
      <div>
        <div class="flex items-center gap-2">
          <Sparkles class="w-4 h-4 text-cyan-400 animate-pulse" />
          <span class="text-xs font-semibold uppercase tracking-wider text-cyan-400">
            Casos Clínicos de Demostración & Expedientes Digitales
          </span>
        </div>
        <p class="text-xs text-slate-400 mt-0.5">
          Selecciona un escenario de prueba o descarga los paquetes de documentos para evaluar
        </p>
      </div>

      <!-- Botón de Descarga Master Bundle -->
      <a
        :href="`${apiBase}/api/demo/packages/all`"
        download="AuraQx_Todos_Los_Casos_Clinicos.zip"
        class="inline-flex items-center justify-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold bg-cyan-500/15 hover:bg-cyan-500/25 text-cyan-300 border border-cyan-500/40 transition-all shadow-[0_0_15px_rgba(56,189,248,0.2)] hover:shadow-[0_0_20px_rgba(56,189,248,0.4)] group shrink-0"
        title="Descargar archivo ZIP con todos los casos clínicos, pólizas e informes"
      >
        <FolderArchive class="w-4 h-4 text-cyan-400 group-hover:scale-110 transition-transform" />
        <span>Descargar Todos los Casos (.ZIP)</span>
      </a>
    </div>

    <!-- Grid de Casos -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
      <div
        v-for="item in cases"
        :key="item.id"
        @click="emit('select', item)"
        :class="[
          'cursor-pointer rounded-xl p-3.5 transition-all duration-300 border text-left relative overflow-hidden flex flex-col justify-between group',
          selectedCaseId === item.id
            ? 'bg-slate-800/80 border-cyan-400/80 shadow-[0_0_20px_-3px_rgba(56,189,248,0.3)] ring-1 ring-cyan-400/50'
            : 'bg-slate-900/40 border-white/10 hover:border-white/20 hover:bg-slate-800/50'
        ]"
      >
        <div>
          <!-- Badge y CPT -->
          <div class="flex items-start justify-between gap-2 mb-2">
            <span :class="['text-[11px] font-medium px-2 py-0.5 rounded-full border flex items-center gap-1', getBadgeClasses(item.badge)]">
              <component :is="getCaseIcon(item.badge)" class="w-3 h-3" />
              {{ item.badge }}
            </span>
            <span class="text-[10px] text-slate-500 font-mono">
              {{ item.report.procedure_cpt ? `CPT ${item.report.procedure_cpt}` : 'URGENTE' }}
            </span>
          </div>

          <!-- Título y Descripción -->
          <h4 class="text-xs font-bold text-slate-100 line-clamp-1 mb-1 group-hover:text-cyan-300 transition-colors">
            {{ item.report.procedure_name }}
          </h4>
          <p class="text-[11px] text-slate-400 line-clamp-2 leading-relaxed mb-3">
            {{ item.description }}
          </p>
        </div>

        <!-- Footer del Card con Paciente, Costo y Botón de Descarga del Paquete -->
        <div class="pt-2 border-t border-white/5 space-y-2">
          <div class="flex items-center justify-between text-[10px] text-slate-400">
            <span class="font-medium text-slate-300 truncate max-w-[130px]">{{ item.report.patient_name }}</span>
            <span class="font-mono text-cyan-300 font-semibold">${{ item.report.estimated_cost.toLocaleString() }} USD</span>
          </div>

          <!-- Acciones de paquete descargable -->
          <div class="flex items-center justify-between gap-1.5 pt-1">
            <span class="text-[10px] text-slate-400 flex items-center gap-1">
              <FileText class="w-3 h-3 text-slate-500" />
              {{ item.package?.documents?.length || 4 }} documentos
            </span>

            <a
              v-if="item.package?.zip_url"
              :href="item.package.zip_url"
              :download="item.package.zip_filename || 'expediente.zip'"
              @click.stop
              class="inline-flex items-center gap-1 px-2 py-1 rounded-md text-[10px] font-medium bg-slate-800 hover:bg-cyan-500/20 text-slate-300 hover:text-cyan-200 border border-white/10 hover:border-cyan-500/30 transition-all"
              title="Descargar paquete ZIP de este caso"
            >
              <Download class="w-3 h-3 text-cyan-400" />
              <span>Pack .ZIP</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
