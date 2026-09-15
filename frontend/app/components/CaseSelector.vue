<script setup lang="ts">
import { CheckCircle2, AlertTriangle, XCircle, Zap, Sparkles } from 'lucide-vue-next'

const emit = defineEmits<{
  (e: 'select', caseItem: any): void
}>()

const props = defineProps<{
  cases: any[]
  selectedCaseId: string | null
}>()

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
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center gap-2">
        <Sparkles class="w-4 h-4 text-cyan-400 animate-pulse" />
        <span class="text-xs font-semibold uppercase tracking-wider text-cyan-400">Casos Clínicos de Demostración (1-Click)</span>
      </div>
      <span class="text-xs text-slate-400">Selecciona un escenario para evaluar en tiempo real</span>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
      <div
        v-for="item in cases"
        :key="item.id"
        @click="emit('select', item)"
        :class="[
          'cursor-pointer rounded-xl p-3.5 transition-all duration-300 border text-left relative overflow-hidden',
          selectedCaseId === item.id
            ? 'bg-slate-800/80 border-cyan-400/80 shadow-[0_0_20px_-3px_rgba(56,189,248,0.3)] ring-1 ring-cyan-400/50'
            : 'bg-slate-900/40 border-white/10 hover:border-white/20 hover:bg-slate-800/50'
        ]"
      >
        <div class="flex items-start justify-between gap-2 mb-2">
          <span :class="['text-[11px] font-medium px-2 py-0.5 rounded-full border flex items-center gap-1', getBadgeClasses(item.badge)]">
            <component :is="getCaseIcon(item.badge)" class="w-3 h-3" />
            {{ item.badge }}
          </span>
          <span class="text-[10px] text-slate-500 font-mono">{{ item.report.procedure_cpt ? `CPT ${item.report.procedure_cpt}` : 'URGENTE' }}</span>
        </div>

        <h4 class="text-xs font-bold text-slate-100 line-clamp-1 mb-1">{{ item.report.procedure_name }}</h4>
        <p class="text-[11px] text-slate-400 line-clamp-2 leading-relaxed mb-2">
          {{ item.description }}
        </p>

        <div class="flex items-center justify-between pt-2 border-t border-white/5 text-[10px] text-slate-400">
          <span class="font-medium text-slate-300">{{ item.report.patient_name }}</span>
          <span class="font-mono text-cyan-300 font-semibold">${{ item.report.estimated_cost.toLocaleString() }} USD</span>
        </div>
      </div>
    </div>
  </div>
</template>
