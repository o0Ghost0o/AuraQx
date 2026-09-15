<script setup lang="ts">
import { ref } from 'vue'
import { Shield, KeyRound, User, Lock, LogIn, Sparkles, CheckCircle2, AlertCircle } from 'lucide-vue-next'

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'logged-in'): void
}>()

const { login, demoLogin, isAuthenticated, user, logout } = useAuth()

const username = ref('auditor_clinico')
const password = ref('hackiathon2026')
const isLoading = ref(false)
const errorMsg = ref<string | null>(null)

const handleLogin = async () => {
  isLoading.value = true
  errorMsg.value = null
  const res = await login(username.value, password.value)
  isLoading.value = false

  if (res.success) {
    emit('logged-in')
    emit('close')
  } else {
    errorMsg.value = res.error || 'Credenciales inválidas'
  }
}

const handleDemoLogin = async () => {
  isLoading.value = true
  errorMsg.value = null
  const res = await demoLogin()
  isLoading.value = false

  if (res.success) {
    emit('logged-in')
    emit('close')
  } else {
    errorMsg.value = res.error || 'Error al conectar con credenciales demo'
  }
}
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md animate-fadeIn">
    <div class="glass-panel glow-cyan rounded-2xl w-full max-w-md p-6 border border-cyan-500/30 relative">
      <button
        @click="emit('close')"
        class="absolute top-4 right-4 text-slate-400 hover:text-white text-xs font-mono px-2 py-1 rounded-lg bg-white/5"
      >
        ESC
      </button>

      <!-- Header -->
      <div class="flex items-center gap-3 mb-6 pb-4 border-b border-white/10">
        <div class="w-10 h-10 rounded-xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
          <Shield class="w-5 h-5" />
        </div>
        <div>
          <h3 class="text-base font-bold text-white">Seguridad y Autenticación</h3>
          <p class="text-xs text-slate-400 font-mono">Tokens JWT: 15 min acceso / 7 días refresh</p>
        </div>
      </div>

      <!-- Logged In State -->
      <div v-if="isAuthenticated && user" class="space-y-4">
        <div class="p-4 rounded-xl bg-slate-900/60 border border-emerald-500/30 text-xs">
          <div class="flex items-center gap-2 text-emerald-400 font-bold mb-2">
            <CheckCircle2 class="w-4 h-4" />
            <span>Sesión Activa</span>
          </div>
          <div class="space-y-1 text-slate-300">
            <div><strong>Usuario:</strong> {{ user.username }}</div>
            <div><strong>Rol:</strong> {{ user.role }}</div>
            <div><strong>Organización:</strong> {{ user.organization }}</div>
          </div>
        </div>

        <button
          @click="logout"
          class="w-full py-2.5 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/30 text-rose-300 font-bold text-xs transition-colors"
        >
          Cerrar Sesión
        </button>
      </div>

      <!-- Login Form -->
      <form v-else @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-xs font-medium text-slate-300 mb-1.5 flex items-center gap-1.5">
            <User class="w-3.5 h-3.5 text-cyan-400" />
            Usuario (Auditor o Personal Hospitalario)
          </label>
          <input
            v-model="username"
            type="text"
            required
            class="w-full px-3.5 py-2.5 rounded-xl glass-input text-xs font-mono"
            placeholder="auditor_clinico"
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-slate-300 mb-1.5 flex items-center gap-1.5">
            <Lock class="w-3.5 h-3.5 text-cyan-400" />
            Contraseña
          </label>
          <input
            v-model="password"
            type="password"
            required
            class="w-full px-3.5 py-2.5 rounded-xl glass-input text-xs font-mono"
            placeholder="••••••••••••"
          />
        </div>

        <div v-if="errorMsg" class="p-2.5 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle class="w-4 h-4 shrink-0" />
          <span>{{ errorMsg }}</span>
        </div>

        <div class="flex flex-col gap-2 pt-2">
          <button
            type="submit"
            :disabled="isLoading"
            class="w-full py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(56,189,248,0.3)] transition-all disabled:opacity-50"
          >
            <LogIn class="w-4 h-4" />
            <span>{{ isLoading ? 'Autenticando...' : 'Iniciar Sesión' }}</span>
          </button>

          <button
            type="button"
            @click="handleDemoLogin"
            :disabled="isLoading"
            class="w-full py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-cyan-500/40 text-cyan-300 font-bold text-xs flex items-center justify-center gap-2 transition-colors"
          >
            <Sparkles class="w-4 h-4 text-cyan-400" />
            <span>1-Click Acceso Rápido Jurado</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
