<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  FileText,
  Database,
  Clock,
  ShieldCheck,
  CheckSquare,
  Sparkles,
  Loader2,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Terminal
} from 'lucide-vue-next'

export interface TelemetryEvent {
  step: number
  title: string
  status: 'running' | 'success' | 'warning' | 'error'
  detail: string
  timestamp: string
}

const props = defineProps<{
  events: TelemetryEvent[]
  currentStep: number
  isRunning: boolean
}>()

const stepsMeta = [
  { step: 1, label: 'Docling Multimodal', icon: FileText, desc: 'OCR, tablas y layout' },
  { step: 2, label: 'Notion DB', icon: Database, desc: 'Consulta de póliza' },
  { step: 3, label: 'Carencias', icon: Clock, desc: 'Cálculo de antigüedad' },
  { step: 4, label: 'Red & Exclusiones', icon: ShieldCheck, desc: 'Convenio hospitalario' },
  { step: 5, label: 'Auditoría Pruebas', icon: CheckSquare, desc: 'Checklist prequirúrgico' },
  { step: 6, label: 'Resolución & Sync', icon: Sparkles, desc: 'Voucher y Notion write' },
]

const getStepStatus = (stepNumber: number) => {
  const match = props.events.find(e => e.step === stepNumber)
  if (match) return match.status
  if (props.currentStep === stepNumber) return 'running'
  if (props.currentStep > stepNumber) return 'success'
  return 'pending'
}
</script>

<template>
  <div class="glass-panel rounded-2xl p-5 border border-white/10 relative overflow-hidden">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4 pb-3 border-b border-white/10">
      <div class="flex items-center gap-2.5">
        <div class="relative flex items-center justify-center w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30">
          <Sparkles class="w-4 h-4 text-cyan-400" :class="{ 'animate-spin': isRunning }" />
          <div v-if="isRunning" class="absolute -inset-1 rounded-lg bg-cyan-500/20 blur-sm animate-pulse" />
        </div>
        <div>
          <h3 class="text-sm font-bold text-white tracking-wide flex items-center gap-2">
            Telemetría Agéntica en Vivo (SSE)
            <span v-if="isRunning" class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 animate-pulse">
              PROCESANDO
            </span>
          </h3>
          <p class="text-[11px] text-slate-400 font-mono">Pipeline autónomo de decisión quirúrgica</p>
        </div>
      </div>
      <div class="flex items-center gap-1.5 text-[11px] text-slate-400 font-mono">
        <Terminal class="w-3.5 h-3.5 text-slate-500" />
        <span>Paso {{ Math.min(Math.max(currentStep, 1), 6) }} / 6</span>
      </div>
    </div>

    <!-- 6-Steps Visual Pipeline -->
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 mb-5">
      <div
        v-for="s in stepsMeta"
        :key="s.step"
        :class="[
          'rounded-xl p-3 border text-left transition-all duration-300 relative overflow-hidden',
          getStepStatus(s.step) === 'running'
            ? 'bg-cyan-500/15 border-cyan-400/80 shadow-[0_0_15px_rgba(56,189,248,0.25)] ring-1 ring-cyan-400/40'
            : getStepStatus(s.step) === 'success'
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
            : getStepStatus(s.step) === 'warning'
            ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
            : getStepStatus(s.step) === 'error'
            ? 'bg-rose-500/10 border-rose-500/30 text-rose-400'
            : 'bg-slate-900/40 border-white/5 opacity-50'
        ]"
      >
        <div class="flex items-center justify-between mb-1.5">
          <component :is="s.icon" class="w-4 h-4" />
          <span v-if="getStepStatus(s.step) === 'running'" class="flex h-2 w-2 relative">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
          </span>
          <CheckCircle2 v-else-if="getStepStatus(s.step) === 'success'" class="w-3.5 h-3.5 text-emerald-400" />
          <AlertTriangle v-else-if="getStepStatus(s.step) === 'warning'" class="w-3.5 h-3.5 text-amber-400" />
          <XCircle v-else-if="getStepStatus(s.step) === 'error'" class="w-3.5 h-3.5 text-rose-400" />
          <span v-else class="text-[10px] font-mono text-slate-500">#{{ s.step }}</span>
        </div>

        <div class="text-xs font-semibold text-slate-200 truncate">{{ s.label }}</div>
        <div class="text-[10px] text-slate-400 truncate">{{ s.desc }}</div>
      </div>
    </div>

    <!-- Live Event Stream Log -->
    <div class="rounded-xl bg-slate-950/80 border border-white/10 p-3.5 font-mono text-xs max-h-48 overflow-y-auto space-y-2">
      <div v-if="events.length === 0" class="text-slate-500 text-center py-4 flex flex-col items-center gap-1">
        <Terminal class="w-5 h-5 text-slate-600" />
        <span>Esperando solicitud para iniciar telemetría de eventos...</span>
      </div>

      <div
        v-for="(ev, idx) in events"
        :key="idx"
        class="flex items-start gap-2.5 leading-relaxed text-[11px] animate-fadeIn"
      >
        <span class="text-slate-500 shrink-0 select-none">[{{ ev.timestamp }}]</span>
        <span
          :class="[
            'px-1.5 py-0.2 rounded text-[10px] font-bold uppercase shrink-0',
            ev.status === 'success' ? 'bg-emerald-500/20 text-emerald-300' :
            ev.status === 'warning' ? 'bg-amber-500/20 text-amber-300' :
            ev.status === 'error' ? 'bg-rose-500/20 text-rose-300' :
            'bg-cyan-500/20 text-cyan-300 animate-pulse'
          ]"
        >
          PASO {{ ev.step }}
        </span>
        <div class="flex-1">
          <span class="font-semibold text-slate-200 mr-2">{{ ev.title }}:</span>
          <span class="text-slate-400">{{ ev.detail }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fadeIn {
  animation: fadeIn 0.25s ease-out forwards;
}
</style>
