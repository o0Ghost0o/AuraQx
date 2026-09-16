<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  FileWarning,
  RefreshCw,
  ArrowRight,
  Clock,
  User,
  Building2,
  FileCheck2,
  AlertCircle
} from 'lucide-vue-next'

const emit = defineEmits<{
  (e: 'select-case', caseItem: any): void
}>()

const { fetchWithAuth } = useAuth()

const incompleteCases = ref<any[]>([])
const isLoading = ref(false)
const errorMsg = ref<string | null>(null)

const fetchIncompleteCases = async () => {
  isLoading.value = true
  errorMsg.value = null
  try {
    const data = await fetchWithAuth<any[]>('/api/preauth/cases/incomplete')
    incompleteCases.value = data || []
  } catch (err: any) {
    console.error('Error fetching incomplete cases:', err)
    errorMsg.value = err.data?.detail || 'Error al cargar casos con documentos pendientes'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchIncompleteCases()
})

defineExpose({
  fetchIncompleteCases,
})
</script>

<template>
  <div class="glass-panel glow-amber rounded-3xl p-6 sm:p-7 border border-amber-500/30 relative overflow-hidden">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-amber-500/20">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-2xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400 shrink-0">
          <FileWarning class="w-5 h-5 animate-pulse" />
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h3 class="text-base font-bold text-white tracking-wide">
              Bandeja de Subsanación Asíncrona
            </h3>
            <span class="px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 text-[10px] font-mono border border-amber-500/30 font-bold">
              {{ incompleteCases.length }} {{ incompleteCases.length === 1 ? 'CASO PENDIENTE' : 'CASOS PENDIENTES' }}
            </span>
          </div>
          <p class="text-xs text-slate-400 mt-0.5">
            Solicitudes quirúrgicas con carencia cumplida a la espera de estudios prequirúrgicos para emitir el voucher definitivo.
          </p>
        </div>
      </div>

      <button
        @click="fetchIncompleteCases"
        :disabled="isLoading"
        class="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-slate-300 hover:text-white border border-white/10 hover:border-white/20 text-xs font-semibold transition-all disabled:opacity-50 shrink-0"
        title="Actualizar lista de casos incompletos"
      >
        <RefreshCw class="w-3.5 h-3.5 text-cyan-400" :class="{ 'animate-spin': isLoading }" />
        <span>Actualizar Bandeja</span>
      </button>
    </div>

    <!-- Error State -->
    <div v-if="errorMsg" class="p-4 rounded-xl bg-rose-500/20 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-2.5 mb-4">
      <AlertCircle class="w-4 h-4 shrink-0" />
      <span>{{ errorMsg }}</span>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading && incompleteCases.length === 0" class="py-12 text-center text-slate-400 text-xs space-y-2">
      <RefreshCw class="w-6 h-6 animate-spin text-amber-400 mx-auto" />
      <p>Consultando base de expedientes pendientes...</p>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="incompleteCases.length === 0"
      class="py-10 text-center rounded-2xl bg-slate-950/40 border border-white/5 p-6 space-y-2"
    >
      <FileCheck2 class="w-8 h-8 text-emerald-400 mx-auto" />
      <p class="text-sm font-semibold text-slate-200">¡Bandeja al día!</p>
      <p class="text-xs text-slate-400 max-w-md mx-auto">
        No existen casos pendientes de documentación complementaria. Todos los expedientes evaluados han sido resueltos.
      </p>
    </div>

    <!-- Table of Incomplete Cases -->
    <div v-else class="overflow-x-auto -mx-6 sm:mx-0 px-6 sm:px-0">
      <table class="w-full text-left text-xs">
        <thead>
          <tr class="border-b border-white/10 text-slate-400 font-mono text-[11px] uppercase tracking-wider">
            <th class="pb-3 font-semibold">ID Solicitud</th>
            <th class="pb-3 font-semibold">Paciente</th>
            <th class="pb-3 font-semibold">Procedimiento</th>
            <th class="pb-3 font-semibold">Documentos Faltantes</th>
            <th class="pb-3 font-semibold">Presupuesto</th>
            <th class="pb-3 font-semibold text-right">Acción</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-white/5">
          <tr
            v-for="item in incompleteCases"
            :key="item.case_id"
            class="hover:bg-slate-900/40 transition-colors group"
          >
            <!-- ID Caso -->
            <td class="py-3.5 pr-3 font-mono font-bold text-cyan-400">
              {{ item.case_id }}
            </td>

            <!-- Paciente -->
            <td class="py-3.5 pr-3">
              <div class="font-medium text-slate-100 flex items-center gap-1.5">
                <User class="w-3.5 h-3.5 text-slate-400 shrink-0" />
                <span>{{ item.patient_name }}</span>
              </div>
              <div class="text-[11px] font-mono text-slate-400 mt-0.5">
                CI: {{ item.patient_id }} • {{ item.policy_number }}
              </div>
            </td>

            <!-- Procedimiento -->
            <td class="py-3.5 pr-3">
              <div class="font-semibold text-slate-200">
                {{ item.procedure_name }}
              </div>
              <div class="text-[11px] text-slate-400 flex items-center gap-1 mt-0.5">
                <Building2 class="w-3 h-3 text-slate-500 shrink-0" />
                <span>{{ item.hospital_name }}</span>
              </div>
            </td>

            <!-- Badges de Documentos Faltantes -->
            <td class="py-3.5 pr-3">
              <div class="flex flex-wrap gap-1.5 max-w-xs">
                <span
                  v-for="doc in item.missing_documents"
                  :key="doc.doc_type"
                  class="inline-flex items-center px-2 py-0.5 rounded-md bg-amber-500/15 border border-amber-500/30 text-amber-300 text-[10px] font-mono font-semibold"
                  :title="doc.medical_rationale"
                >
                  {{ doc.title }}
                </span>
              </div>
            </td>

            <!-- Presupuesto -->
            <td class="py-3.5 pr-3 font-mono font-bold text-emerald-400">
              ${{ (item.financials?.estimated_total || 0).toLocaleString('en-US', { minimumFractionDigits: 2 }) }}
            </td>

            <!-- Botón Subsanar Caso -->
            <td class="py-3.5 text-right">
              <button
                @click="emit('select-case', item)"
                class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-400 hover:to-yellow-400 text-slate-950 font-bold text-xs shadow-sm hover:shadow-[0_0_12px_rgba(245,158,11,0.3)] transition-all"
              >
                <span>Subsanar Caso</span>
                <ArrowRight class="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
