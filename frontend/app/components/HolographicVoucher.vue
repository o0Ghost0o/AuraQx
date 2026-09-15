<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import QRCode from 'qrcode'
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ShieldAlert,
  Printer,
  Sparkles,
  ExternalLink,
  Calendar,
  Building2,
  FileCheck,
  Percent,
  DollarSign
} from 'lucide-vue-next'

const props = defineProps<{
  resolution: any
}>()

const qrCanvas = ref<HTMLCanvasElement | null>(null)

const renderQR = async () => {
  if (qrCanvas.value && props.resolution?.qr_data) {
    try {
      await QRCode.toCanvas(qrCanvas.value, props.resolution.qr_data, {
        width: 110,
        margin: 1,
        color: {
          dark: '#070b14',
          light: '#38bdf8',
        },
      })
    } catch (e) {
      console.error('Error generating QR:', e)
    }
  }
}

onMounted(() => {
  renderQR()
})

watch(() => props.resolution, () => {
  setTimeout(renderQR, 50)
}, { deep: true })

const printVoucher = () => {
  window.print()
}
</script>

<template>
  <div
    v-if="resolution"
    :class="[
      'glass-panel rounded-2xl p-6 border relative overflow-hidden transition-all duration-500',
      resolution.status === 'PRE_APROBADO' ? 'border-emerald-500/40 glow-emerald' :
      resolution.status === 'DOCUMENTOS_FALTANTES' ? 'border-amber-500/40 glow-amber' :
      'border-rose-500/40 glow-rose'
    ]"
  >
    <!-- Top holographic glow strip -->
    <div
      :class="[
        'absolute top-0 left-0 right-0 h-1.5',
        resolution.status === 'PRE_APROBADO' ? 'bg-gradient-to-r from-emerald-500 via-teal-300 to-cyan-400' :
        resolution.status === 'DOCUMENTOS_FALTANTES' ? 'bg-gradient-to-r from-amber-500 via-orange-400 to-yellow-300' :
        'bg-gradient-to-r from-rose-600 via-red-500 to-pink-500'
      ]"
    />

    <!-- Header Section -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6 pb-5 border-b border-white/10">
      <div>
        <div class="flex items-center gap-2 mb-1.5">
          <span class="text-[10px] font-mono tracking-widest uppercase text-slate-400">RESOLUCIÓN QUIRÚRGICA OFICIAL</span>
          <span v-if="resolution.notion_synced" class="px-2 py-0.5 rounded-full text-[10px] font-mono bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 flex items-center gap-1">
            <span class="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
            Notion DB Sincronizado
          </span>
        </div>
        <h2 class="text-xl sm:text-2xl font-black text-white tracking-tight flex items-center gap-3">
          <component
            :is="resolution.status === 'PRE_APROBADO' ? CheckCircle2 : (resolution.status === 'DOCUMENTOS_FALTANTES' ? AlertTriangle : XCircle)"
            :class="[
              'w-7 h-7',
              resolution.status === 'PRE_APROBADO' ? 'text-emerald-400' :
              resolution.status === 'DOCUMENTOS_FALTANTES' ? 'text-amber-400' :
              'text-rose-400'
            ]"
          />
          {{ resolution.status === 'PRE_APROBADO' ? 'PRE-AUTORIZACIÓN APROBADA' : (resolution.status === 'DOCUMENTOS_FALTANTES' ? 'DOCUMENTOS FALTANTES REQUERIDOS' : 'SOLICITUD NO AUTORIZADA') }}
        </h2>
        <div class="text-xs font-mono text-slate-400 mt-1">
          Código de Voucher: <span class="text-white font-bold">{{ resolution.case_id }}</span> | Emisión: {{ resolution.created_at }}
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center gap-2">
        <button
          @click="printVoucher"
          class="px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-white/10 text-xs font-medium text-slate-200 flex items-center gap-1.5 transition-colors"
        >
          <Printer class="w-3.5 h-3.5" />
          Imprimir Certificado
        </button>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-6">
      <!-- Columna 1 y 2: Detalles Clínicos y Financieros -->
      <div class="lg:col-span-2 space-y-4">
        <!-- Patient and Surgery Summary -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 p-4 rounded-xl bg-slate-950/60 border border-white/5 text-xs">
          <div>
            <span class="text-[10px] text-slate-500 uppercase font-mono block">Paciente Asegurado</span>
            <span class="font-bold text-slate-200 text-sm">{{ resolution.patient_name }}</span>
            <span class="text-slate-400 block font-mono">C.I. {{ resolution.patient_id }}</span>
          </div>
          <div>
            <span class="text-[10px] text-slate-500 uppercase font-mono block">Póliza y Hospital</span>
            <span class="font-bold text-cyan-300">{{ resolution.policy_number }}</span>
            <span class="text-slate-300 block">{{ resolution.hospital_name }}</span>
          </div>
          <div class="sm:col-span-2 pt-2 border-t border-white/5">
            <span class="text-[10px] text-slate-500 uppercase font-mono block">Procedimiento Solicitado</span>
            <span class="font-bold text-slate-100 text-sm">{{ resolution.procedure_name }}</span>
          </div>
        </div>

        <!-- Carencia Audit Box -->
        <div class="p-4 rounded-xl bg-slate-950/60 border border-white/5">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-2">
              <Calendar class="w-4 h-4 text-cyan-400" />
              <span class="text-xs font-bold text-slate-200">Auditoría de Período de Carencia</span>
            </div>
            <span
              :class="[
                'text-[10px] font-mono px-2 py-0.5 rounded-full font-bold',
                resolution.carencia_audit.is_satisfied
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
              ]"
            >
              {{ resolution.carencia_audit.is_satisfied ? 'CARENCIA CUMPLIDA' : 'CARENCIA INSUFICIENTE' }}
            </span>
          </div>
          <p class="text-xs text-slate-300 leading-relaxed">
            {{ resolution.carencia_audit.explanation }}
          </p>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-2 mt-3 pt-3 border-t border-white/5 text-[11px] font-mono">
            <div>
              <span class="text-slate-500 block">Antigüedad activa:</span>
              <span class="font-bold text-white">{{ resolution.carencia_audit.elapsed_months }} meses</span> ({{ resolution.carencia_audit.elapsed_days }} días)
            </div>
            <div>
              <span class="text-slate-500 block">Carencia requerida:</span>
              <span class="font-bold text-white">{{ resolution.carencia_audit.required_months }} meses</span>
            </div>
            <div>
              <span class="text-slate-500 block">Excepción aplicada:</span>
              <span class="text-cyan-300 font-bold">{{ resolution.carencia_audit.exception_applied || 'Ninguna (Electiva)' }}</span>
            </div>
          </div>
        </div>

        <!-- Financial Breakdown Cards -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
          <div class="p-3 rounded-xl bg-slate-900/60 border border-white/5">
            <span class="text-[10px] text-slate-500 font-mono uppercase block">Presupuesto</span>
            <span class="text-sm font-bold text-white font-mono">${{ resolution.financials.estimated_total.toLocaleString() }} USD</span>
          </div>
          <div class="p-3 rounded-xl bg-slate-900/60 border border-white/5">
            <span class="text-[10px] text-slate-500 font-mono uppercase block">Cobertura Plan</span>
            <span class="text-sm font-bold text-cyan-300 font-mono">{{ resolution.financials.coverage_percent }}%</span>
          </div>
          <div class="p-3 rounded-xl bg-slate-900/60 border border-white/5">
            <span class="text-[10px] text-slate-500 font-mono uppercase block">Aseguradora Asume</span>
            <span class="text-sm font-bold text-emerald-400 font-mono">${{ resolution.financials.insurer_pays.toLocaleString() }} USD</span>
          </div>
          <div class="p-3 rounded-xl bg-slate-900/60 border border-white/5">
            <span class="text-[10px] text-slate-500 font-mono uppercase block">Copago Paciente</span>
            <span class="text-sm font-bold text-amber-400 font-mono">${{ resolution.financials.patient_copay.toLocaleString() }} USD</span>
          </div>
        </div>
      </div>

      <!-- Columna 3: Código QR Criptográfico y Sello Digital -->
      <div class="flex flex-col items-center justify-between p-4 rounded-xl bg-slate-950/80 border border-white/10 text-center">
        <div class="w-full">
          <span class="text-[10px] font-mono tracking-wider text-slate-400 uppercase block mb-2">VERIFICACIÓN DIGITAL QR</span>
          <div class="p-2 rounded-xl bg-cyan-950/40 border border-cyan-500/30 inline-block mb-3 shadow-[0_0_20px_rgba(56,189,248,0.2)]">
            <canvas ref="qrCanvas" class="rounded-lg"></canvas>
          </div>
          <div class="text-[10px] font-mono text-slate-400 break-all px-2 line-clamp-2">
            {{ resolution.qr_data }}
          </div>
        </div>

        <div class="w-full pt-3 mt-3 border-t border-white/10 text-[10px] text-slate-400 font-mono">
          <div>Validador: <span class="text-slate-200">SurgiAuth Core AI</span></div>
          <div>Red Hospitalaria: <span class="text-emerald-400 font-bold">{{ resolution.financials.in_network ? 'CONVENIO EN RED' : 'FUERA DE RED' }}</span></div>
        </div>
      </div>
    </div>

    <!-- Clinical Justification Text -->
    <div class="p-4 rounded-xl bg-slate-950/50 border border-white/5">
      <span class="text-[10px] font-mono uppercase tracking-wider text-cyan-400 block mb-1">FUNDAMENTACIÓN MÉDICA Y NORMATIVA DE LA RESOLUCIÓN</span>
      <p class="text-xs text-slate-300 leading-relaxed font-sans">
        {{ resolution.clinical_justification }}
      </p>
    </div>
  </div>
</template>
