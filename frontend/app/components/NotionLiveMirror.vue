<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Database, RefreshCw, CheckCircle2, Shield, FileText, ExternalLink, Calendar, Layers } from 'lucide-vue-next'

const { fetchWithAuth } = useAuth()

const activeTab = ref<'cases' | 'policies'>('cases')
const isLoading = ref(false)
const notionStatus = ref<any>(null)
const policies = ref<any[]>([])
const cases = ref<any[]>([])

const loadNotionData = async () => {
  isLoading.value = true
  try {
    const [statusRes, policiesRes, casesRes] = await Promise.all([
      fetchWithAuth('/api/notion/status'),
      fetchWithAuth('/api/notion/policies'),
      fetchWithAuth('/api/notion/cases'),
    ])
    notionStatus.value = statusRes
    policies.value = policiesRes
    cases.value = casesRes
  } catch (err) {
    console.error('Error fetching Notion data:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadNotionData()
})

defineExpose({
  loadNotionData,
})
</script>

<template>
  <div class="glass-panel rounded-2xl p-6 border border-white/10 relative overflow-hidden">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-white/10">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
          <Database class="w-5 h-5" />
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h3 class="text-base font-bold text-white tracking-wide">Espejo en Vivo: Base de Datos de Notion</h3>
            <span
              :class="[
                'text-[10px] font-mono px-2 py-0.5 rounded-full border',
                notionStatus?.is_connected
                  ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                  : 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
              ]"
            >
              {{ notionStatus?.connection_mode || 'Conectando...' }}
            </span>
          </div>
          <p class="text-xs text-slate-400">Pólizas contractuales y pre-autorizaciones emitidas por el agente</p>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <div class="flex rounded-xl bg-slate-950/80 p-1 border border-white/10 text-xs">
          <button
            @click="activeTab = 'cases'"
            :class="[
              'px-3 py-1.5 rounded-lg font-medium transition-all',
              activeTab === 'cases' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' : 'text-slate-400 hover:text-white'
            ]"
          >
            Pre-Autorizaciones ({{ cases.length }})
          </button>
          <button
            @click="activeTab = 'policies'"
            :class="[
              'px-3 py-1.5 rounded-lg font-medium transition-all',
              activeTab === 'policies' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' : 'text-slate-400 hover:text-white'
            ]"
          >
            Pólizas de Seguros ({{ policies.length }})
          </button>
        </div>

        <button
          @click="loadNotionData"
          :disabled="isLoading"
          class="p-2 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-white/10 text-slate-300 hover:text-white transition-colors"
          title="Actualizar datos de Notion"
        >
          <RefreshCw class="w-4 h-4" :class="{ 'animate-spin': isLoading }" />
        </button>
      </div>
    </div>

    <!-- Table Content -->
    <div class="overflow-x-auto">
      <!-- Tab 1: Pre-Autorizaciones -->
      <table v-if="activeTab === 'cases'" class="w-full text-left text-xs font-mono">
        <thead>
          <tr class="border-b border-white/10 text-slate-400 uppercase text-[10px]">
            <th class="py-2.5 px-3">ID Solicitud</th>
            <th class="py-2.5 px-3">Asegurado</th>
            <th class="py-2.5 px-3">Procedimiento</th>
            <th class="py-2.5 px-3">Hospital</th>
            <th class="py-2.5 px-3">Estado</th>
            <th class="py-2.5 px-3">Monto Cubierto</th>
            <th class="py-2.5 px-3">Carencia</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-white/5">
          <tr v-if="cases.length === 0">
            <td colspan="7" class="py-8 text-center text-slate-500 font-sans">
              No hay solicitudes registradas aún. Evalúa un caso arriba para ver la sincronización en vivo.
            </td>
          </tr>
          <tr v-for="c in cases" :key="c.case_id" class="hover:bg-slate-800/30 transition-colors">
            <td class="py-3 px-3 font-bold text-cyan-300">{{ c.case_id }}</td>
            <td class="py-3 px-3 text-slate-200">
              <div class="font-bold">{{ c.patient_name }}</div>
              <div class="text-[10px] text-slate-400">C.I. {{ c.patient_id }}</div>
            </td>
            <td class="py-3 px-3 text-slate-300 max-w-[200px] truncate" :title="c.procedure_name">
              {{ c.procedure_name }}
            </td>
            <td class="py-3 px-3 text-slate-400">{{ c.hospital_name }}</td>
            <td class="py-3 px-3">
              <span
                :class="[
                  'px-2 py-0.5 rounded-full text-[10px] font-bold',
                  c.status === 'PRE_APROBADO' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                  c.status === 'DOCUMENTOS_FALTANTES' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                  'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                ]"
              >
                {{ c.status }}
              </span>
            </td>
            <td class="py-3 px-3 font-bold text-emerald-400">
              ${{ c.financials?.insurer_pays ? c.financials.insurer_pays.toLocaleString() : '0' }} USD
            </td>
            <td class="py-3 px-3">
              <span v-if="c.carencia_audit?.is_satisfied" class="text-emerald-400 flex items-center gap-1">
                <CheckCircle2 class="w-3.5 h-3.5" /> Cumplida
              </span>
              <span v-else class="text-rose-400">
                Faltan {{ c.carencia_audit?.required_months ? (c.carencia_audit.required_months - c.carencia_audit.elapsed_months).toFixed(1) : '' }}m
              </span>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Tab 2: Pólizas -->
      <table v-else class="w-full text-left text-xs font-mono">
        <thead>
          <tr class="border-b border-white/10 text-slate-400 uppercase text-[10px]">
            <th class="py-2.5 px-3">Póliza</th>
            <th class="py-2.5 px-3">Asegurado</th>
            <th class="py-2.5 px-3">Plan</th>
            <th class="py-2.5 px-3">Inicio Vigencia</th>
            <th class="py-2.5 px-3">Estado</th>
            <th class="py-2.5 px-3">Cobertura Red</th>
            <th class="py-2.5 px-3">Deducible</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-white/5">
          <tr v-for="p in policies" :key="p.policy_number" class="hover:bg-slate-800/30 transition-colors">
            <td class="py-3 px-3 font-bold text-cyan-300">{{ p.policy_number }}</td>
            <td class="py-3 px-3 text-slate-200">
              <div class="font-bold">{{ p.patient_name }}</div>
              <div class="text-[10px] text-slate-400">C.I. {{ p.patient_id }}</div>
            </td>
            <td class="py-3 px-3 text-slate-300">
              <span class="px-2 py-0.5 rounded-md bg-white/5 border border-white/10">{{ p.plan_tier }}</span>
            </td>
            <td class="py-3 px-3 text-slate-400">{{ p.start_date }}</td>
            <td class="py-3 px-3">
              <span class="text-emerald-400 font-bold">{{ p.status }}</span>
            </td>
            <td class="py-3 px-3 font-bold text-slate-200">{{ p.coverage_percent_in_network }}%</td>
            <td class="py-3 px-3 text-slate-400">${{ p.annual_deductible }} USD</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
