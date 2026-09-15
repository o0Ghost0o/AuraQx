<script setup lang="ts">
import { ref } from 'vue'
import { Database, Sparkles, ExternalLink, Key, Layers, CheckCircle2 } from 'lucide-vue-next'

const notionMirrorRef = ref<any>(null)
</script>

<template>
  <div class="space-y-6 animate-fadeIn">
    <!-- Header -->
    <div class="glass-panel rounded-3xl p-6 sm:p-8 border border-white/10 relative overflow-hidden">
      <div class="max-w-3xl">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/15 border border-cyan-500/30 text-cyan-300 text-xs font-mono mb-3">
          <Database class="w-3.5 h-3.5" />
          <span>Base de Datos del Reto 1 (Notion Integration)</span>
        </div>
        <h1 class="text-2xl sm:text-3xl font-black text-white tracking-tight mb-2">
          Monitor de Pólizas y Pre-Autorizaciones en <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-emerald-400">Notion DB</span>
        </h1>
        <p class="text-xs sm:text-sm text-slate-400 leading-relaxed">
          SurgiAuth AI opera de forma bidireccional: consulta las pólizas y reglas de carencia contractuales directamente desde Notion y escribe al instante las resoluciones, códigos de pre-aprobación y montos cubiertos.
        </p>
      </div>
    </div>

    <!-- Guía de Configuración para Evaluadores -->
    <GlassCard>
      <div class="flex items-start gap-4">
        <div class="w-10 h-10 rounded-xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shrink-0">
          <Key class="w-5 h-5" />
        </div>
        <div class="space-y-2 text-xs">
          <h3 class="font-bold text-slate-100 text-sm">Modo Híbrido Garantizado (Zero-Friction Hackathon)</h3>
          <p class="text-slate-400 leading-relaxed">
            El sistema incluye un almacén reactivo dual. Por defecto, funciona 100% de manera autónoma con las pólizas y resoluciones sincronizadas localmente. Para conectar tu propio espacio de Notion, simplemente define en <code class="px-1.5 py-0.5 rounded bg-slate-800 text-cyan-300 font-mono">backend/.env</code>:
          </p>
          <div class="p-3 rounded-xl bg-slate-950/80 border border-white/10 font-mono text-[11px] text-cyan-300 space-y-1">
            <div>NOTION_API_KEY=secret_tu_token_aqui</div>
            <div>NOTION_POLICIES_DB_ID=tu_database_id_de_polizas</div>
            <div>NOTION_PREAUTHS_DB_ID=tu_database_id_de_preautorizaciones</div>
          </div>
        </div>
      </div>
    </GlassCard>

    <!-- Componente Espejo en Vivo -->
    <NotionLiveMirror ref="notionMirrorRef" />
  </div>
</template>
