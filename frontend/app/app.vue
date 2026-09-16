<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  ShieldCheck,
  Activity,
  Database,
  Sparkles,
  Lock,
  User,
  Download,
  Github,
  CheckCircle2,
  Stethoscope,
  Compass
} from 'lucide-vue-next'

const { isAuthenticated, user, demoLogin, initUser } = useAuth()
const { startTour } = useTour()
const isAuthModalOpen = ref(false)
const pwaInstallPrompt = ref<any>(null)
const isInstalled = ref(false)

onMounted(async () => {
  // Inicializar usuario si hay cookie existente
  await initUser()

  // Si no está autenticado, hacer auto demoLogin para comodidad de jurados
  if (!isAuthenticated.value) {
    await demoLogin()
  }

  // Detectar PWA install prompt
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault()
    pwaInstallPrompt.value = e
  })

  window.addEventListener('appinstalled', () => {
    isInstalled.value = true
    pwaInstallPrompt.value = null
  })
})

const installPWA = async () => {
  if (pwaInstallPrompt.value) {
    pwaInstallPrompt.value.prompt()
    const { outcome } = await pwaInstallPrompt.value.userChoice
    if (outcome === 'accepted') {
      pwaInstallPrompt.value = null
    }
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#070b14] text-slate-100 relative selection:bg-cyan-500 selection:text-black">
    <!-- Ambient mesh lighting -->
    <div class="fixed inset-0 pointer-events-none z-0">
      <div class="absolute -top-40 left-1/4 w-[600px] h-[600px] bg-cyan-500/10 rounded-full blur-[140px]" />
      <div class="absolute top-1/3 -right-40 w-[500px] h-[500px] bg-emerald-500/10 rounded-full blur-[140px]" />
      <div class="absolute -bottom-40 left-1/3 w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-[140px]" />
      <div class="absolute inset-0 bg-grid-cyber opacity-30" />
    </div>

    <!-- Navigation Bar -->
    <header class="sticky top-0 z-40 backdrop-blur-xl bg-[#070b14]/75 border-b border-white/10 transition-all">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        <!-- Logo -->
        <NuxtLink to="/" class="flex items-center gap-3 group">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 via-blue-600 to-emerald-400 p-[1px] shadow-[0_0_20px_rgba(56,189,248,0.3)] transition-transform group-hover:scale-105">
            <div class="w-full h-full bg-[#070b14] rounded-[11px] flex items-center justify-center text-cyan-400">
              <Stethoscope class="w-5 h-5" />
            </div>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="text-base font-black tracking-tight text-white group-hover:text-cyan-300 transition-colors">
                Aura<span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-emerald-400">Qx</span>
              </span>
              <span class="text-[10px] font-mono px-1.5 py-0.2 rounded bg-cyan-500/15 border border-cyan-500/30 text-cyan-400">
                RETO 1
              </span>
            </div>
            <p class="text-[10px] text-slate-400 font-mono">Pre-Autorización Quirúrgica en Tiempo Real</p>
          </div>
        </NuxtLink>

        <!-- Nav Items -->
        <nav class="hidden md:flex items-center gap-1 font-mono text-xs">
          <NuxtLink
            to="/"
            class="px-3.5 py-2 rounded-xl text-slate-300 hover:text-white hover:bg-white/5 transition-all flex items-center gap-2"
            active-class="bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 font-bold"
          >
            <Activity class="w-3.5 h-3.5" />
            Triage Quirúrgico
          </NuxtLink>

          <NuxtLink
            to="/notion"
            class="px-3.5 py-2 rounded-xl text-slate-300 hover:text-white hover:bg-white/5 transition-all flex items-center gap-2"
            active-class="bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 font-bold"
          >
            <Database class="w-3.5 h-3.5" />
            Notion DB
          </NuxtLink>

          <NuxtLink
            to="/auditor"
            class="px-3.5 py-2 rounded-xl text-slate-300 hover:text-white hover:bg-white/5 transition-all flex items-center gap-2"
            active-class="bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 font-bold"
          >
            <ShieldCheck class="w-3.5 h-3.5" />
            Panel Auditor
          </NuxtLink>
        </nav>

        <!-- Right Controls -->
        <div class="flex items-center gap-2.5">
          <!-- Tour Guiado button -->
          <button
            @click="startTour"
            class="px-3 py-1.5 rounded-xl border border-cyan-500/40 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 text-xs font-mono font-medium flex items-center gap-1.5 transition-all cursor-pointer shadow-sm hover:shadow-[0_0_12px_rgba(56,189,248,0.25)]"
            title="Iniciar recorrido guiado interactivo de AuraQx"
          >
            <Compass class="w-3.5 h-3.5 text-cyan-400" />
            <span class="hidden sm:inline">Tour Guiado</span>
          </button>

          <!-- Install PWA button -->
          <button
            v-if="pwaInstallPrompt"
            @click="installPWA"
            class="hidden sm:flex px-3 py-1.5 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/40 text-emerald-300 text-xs font-mono font-medium items-center gap-1.5 transition-all"
          >
            <Download class="w-3.5 h-3.5 animate-bounce" />
            Instalar PWA
          </button>

          <!-- Auth Button -->
          <button
            @click="isAuthModalOpen = true"
            :class="[
              'px-3 py-1.5 rounded-xl border text-xs font-mono flex items-center gap-2 transition-all',
              isAuthenticated
                ? 'bg-slate-900/80 border-emerald-500/40 text-slate-200'
                : 'bg-slate-900/80 border-white/10 text-slate-400 hover:text-white'
            ]"
          >
            <span v-if="isAuthenticated" class="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
            <Lock v-else class="w-3.5 h-3.5 text-cyan-400" />
            <span class="hidden sm:inline">{{ isAuthenticated ? (user?.username || 'Auditor') : 'Iniciar Sesión' }}</span>
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <NuxtPage />
    </main>

    <!-- Footer -->
    <footer class="relative z-10 border-t border-white/10 bg-[#070b14]/80 py-6 mt-12 text-center text-xs text-slate-500 font-mono">
      <div class="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div>
          <span class="text-slate-400 font-bold">HackIAthon 2026</span> • Viamatica & ADEN University • Reto 1
        </div>
        <div class="flex items-center gap-4 text-slate-400">
          <span>FastAPI + uv</span>
          <span>•</span>
          <span>Nuxt 4 PWA + Bun</span>
          <span>•</span>
          <span>IBM Docling</span>
          <span>•</span>
          <span>Notion DB</span>
        </div>
      </div>
    </footer>

    <!-- Auth Modal -->
    <AuthModal
      v-if="isAuthModalOpen"
      @close="isAuthModalOpen = false"
      @logged-in="isAuthModalOpen = false"
    />
  </div>
</template>
