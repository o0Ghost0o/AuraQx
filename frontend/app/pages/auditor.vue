<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  ShieldCheck,
  TrendingUp,
  Clock,
  AlertTriangle,
  DollarSign,
  Activity,
  FileCheck2,
  PieChart
} from 'lucide-vue-next'

const { fetchWithAuth } = useAuth()
const cases = ref<any[]>([])
const isLoading = ref(false)

onMounted(async () => {
  isLoading.value = true
  try {
    const res = await fetchWithAuth<any[]>('/api/notion/cases')
    cases.value = res
  } catch (err) {
    console.error('Error fetching auditor cases:', err)
  } finally {
    isLoading.value = false
  }
})

const approvedCount = computed(() => cases.value.filter(c => c.status === 'PRE_APROBADO').length)
const missingCount = computed(() => cases.value.filter(c => c.status === 'DOCUMENTOS_FALTANTES').length)
const rejectedCount = computed(() => cases.value.filter(c => c.status === 'RECHAZADO').length)
const totalAmountAuthorized = computed(() =>
  cases.value.filter(c => c.status === 'PRE_APROBADO').reduce((acc, c) => acc + (c.financials?.insurer_pays || 0), 0)
)
</script>

<template>
  <div class="space-y-6 animate-fadeIn">
    <!-- Header -->
    <div class="glass-panel rounded-3xl p-6 sm:p-8 border border-white/10 relative overflow-hidden">
      <div class="max-w-3xl">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-mono mb-3">
          <ShieldCheck class="w-3.5 h-3.5" />
          <span>Supervisión Médica & Analytics</span>
        </div>
        <h1 class="text-2xl sm:text-3xl font-black text-white tracking-tight mb-2">
          Panel de Control del <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">Auditor Clínico</span>
        </h1>
        <p class="text-xs sm:text-sm text-slate-400 leading-relaxed">
          Métricas de impacto operativo, mitigación de riesgo de carencias no cumplidas y consolidado de autorizaciones emitidas.
        </p>
      </div>
    </div>

    <!-- KPIs Metrics Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <GlassCard variant="glow-emerald">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs font-mono text-slate-400 uppercase">Pre-Aprobadas</span>
          <FileCheck2 class="w-5 h-5 text-emerald-400" />
        </div>
        <div class="text-3xl font-black text-white font-mono">{{ approvedCount }}</div>
        <p class="text-[11px] text-emerald-400 mt-1 font-mono">Carencias y pruebas validadas</p>
      </GlassCard>

      <GlassCard variant="glow-amber">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs font-mono text-slate-400 uppercase">Docs Faltantes</span>
          <AlertTriangle class="w-5 h-5 text-amber-400" />
        </div>
        <div class="text-3xl font-black text-white font-mono">{{ missingCount }}</div>
        <p class="text-[11px] text-amber-400 mt-1 font-mono">En espera de subsanación</p>
      </GlassCard>

      <GlassCard variant="glow-rose">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs font-mono text-slate-400 uppercase">No Autorizadas</span>
          <ShieldCheck class="w-5 h-5 text-rose-400" />
        </div>
        <div class="text-3xl font-black text-white font-mono">{{ rejectedCount }}</div>
        <p class="text-[11px] text-rose-400 mt-1 font-mono">Carencias insuficientes bloqueadas</p>
      </GlassCard>

      <GlassCard variant="glow-cyan">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs font-mono text-slate-400 uppercase">Total Autorizado</span>
          <DollarSign class="w-5 h-5 text-cyan-400" />
        </div>
        <div class="text-2xl font-black text-white font-mono">
          ${{ totalAmountAuthorized.toLocaleString() }} <span class="text-xs text-slate-400">USD</span>
        </div>
        <p class="text-[11px] text-cyan-400 mt-1 font-mono">Monto asegurado en red</p>
      </GlassCard>
    </div>

    <!-- Efficiency Comparison Card -->
    <GlassCard>
      <div class="flex items-center gap-3 mb-4 pb-3 border-b border-white/10">
        <Clock class="w-5 h-5 text-cyan-400" />
        <div>
          <h3 class="text-sm font-bold text-white">Impacto Operativo: Tiempos de Respuesta</h3>
          <p class="text-xs text-slate-400">Comparativa de flujo manual tradicional vs SurgiAuth AI</p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
        <div class="p-4 rounded-xl bg-slate-950/60 border border-rose-500/20 space-y-2">
          <span class="text-rose-400 font-bold block">PROCESO MANUAL TRADICIONAL</span>
          <div class="text-2xl font-black text-slate-300">24 a 72 Horas</div>
          <p class="text-slate-400 font-sans text-[11px] leading-relaxed">
            Revisión manual de pólizas en PDFs, intercambio de correos entre hospital y aseguradora, demoras en programaciones quirúrgicas y quejas de pacientes.
          </p>
        </div>

        <div class="p-4 rounded-xl bg-slate-950/60 border border-emerald-500/30 space-y-2 glow-emerald">
          <span class="text-emerald-400 font-bold block flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            SURGIAUTH AI EN TIEMPO REAL
          </span>
          <div class="text-2xl font-black text-emerald-300">&lt; 3 Segundos</div>
          <p class="text-slate-300 font-sans text-[11px] leading-relaxed">
            Ingestión multimodal automática, cálculo cronológico de carencias con base en Notion y emisión instantánea de voucher con QR y código de autorización.
          </p>
        </div>
      </div>
    </GlassCard>
  </div>
</template>
