export interface UserProfile {
  username: string
  role: string
  full_name: string
  organization: string
}

/**
 * Resuelve la URL base de la API de forma dinámica:
 * - En el navegador (client-side), si la configuración apunta al hostname interno de Docker ('backend:8000')
 *   o si el usuario está accediendo desde un dominio público (*.vertexdc.com o HTTPS),
 *   se redirige automáticamente a la API pública externa 'https://api-auraqx.vertexdc.com'.
 * - En localhost/127.0.0.1, mantiene 'http://localhost:8000'.
 */
export const resolveApiBase = (configuredBase?: string): string => {
  let base = (configuredBase || '').trim()

  if (import.meta.client && typeof window !== 'undefined') {
    const { hostname, protocol } = window.location

    // En entorno local de desarrollo
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return base.includes('backend:8000') ? 'http://localhost:8000' : (base || 'http://localhost:8000')
    }

    // En el navegador en producción / dominios externos:
    // 'backend:8000' es inaccesible fuera de la red interna de Docker.
    if (!base || base.includes('backend:8000') || base.includes('backend') || hostname.includes('vertexdc.com')) {
      return 'https://api-auraqx.vertexdc.com'
    }

    // Si la web carga por HTTPS, forzar HTTPS en la API para evitar bloqueo de Mixed Content
    if (protocol === 'https:' && base.startsWith('http://')) {
      if (base.includes('vertexdc.com')) {
        return base.replace('http://', 'https://')
      }
      return 'https://api-auraqx.vertexdc.com'
    }
  }

  return base || 'https://api-auraqx.vertexdc.com'
}

export const useAuth = () => {
  const config = useRuntimeConfig()
  const apiBase = resolveApiBase(config.public.apiBase)

  const token = useCookie<string | null>('auraqx_access_token', {
    maxAge: 60 * 15, // 15 minutos
    sameSite: 'lax',
  })

  const refreshToken = useCookie<string | null>('auraqx_refresh_token', {
    maxAge: 60 * 60 * 24 * 7, // 7 días
    sameSite: 'lax',
  })

  const user = useState<UserProfile | null>('auraqx_user', () => null)
  const isRefreshing = useState<boolean>('auraqx_is_refreshing', () => false)

  const isAuthenticated = computed(() => !!token.value)

  // Login formal
  const login = async (username: string, password: string) => {
    try {
      const res = await $fetch<{
        access_token: string
        refresh_token: string
        user: UserProfile
      }>(`${apiBase}/api/auth/login`, {
        method: 'POST',
        body: { username, password },
      })

      token.value = res.access_token
      refreshToken.value = res.refresh_token
      user.value = res.user
      return { success: true }
    } catch (err: any) {
      const msg = err.data?.detail || 'Error al iniciar sesión'
      return { success: false, error: msg }
    }
  }

  // 1-Click Demo Login para jurados y evaluadores
  const demoLogin = async () => {
    return await login('auditor_clinico', 'hackiathon2026')
  }

  // Renovación transparente de token (15m con refresh token de 7d)
  const refresh = async (): Promise<boolean> => {
    if (!refreshToken.value || isRefreshing.value) return false

    isRefreshing.value = true
    try {
      const res = await $fetch<{ access_token: string }>(`${apiBase}/api/auth/refresh`, {
        method: 'POST',
        body: { refresh_token: refreshToken.value },
      })

      token.value = res.access_token
      return true
    } catch (err) {
      logout()
      return false
    } finally {
      isRefreshing.value = false
    }
  }

  // Wrapper seguro con auto-refresh en 401
  const fetchWithAuth = async <T = any>(url: string, opts: any = {}): Promise<T> => {
    const fullUrl = url.startsWith('http') ? url : `${apiBase}${url}`
    opts.headers = opts.headers || {}

    if (token.value) {
      opts.headers.Authorization = `Bearer ${token.value}`
    }

    try {
      return await $fetch<T>(fullUrl, opts)
    } catch (err: any) {
      // Si recibimos 401 Unauthorized, intentamos renovar con el refresh token de 7 días
      if (err.statusCode === 401 && refreshToken.value) {
        const refreshed = await refresh()
        if (refreshed && token.value) {
          opts.headers.Authorization = `Bearer ${token.value}`
          return await $fetch<T>(fullUrl, opts)
        }
      }
      throw err
    }
  }

  const logout = () => {
    token.value = null
    refreshToken.value = null
    user.value = null
  }

  // Restaurar usuario al cargar si hay token
  const initUser = async () => {
    if (token.value && !user.value) {
      try {
        const res = await fetchWithAuth<UserProfile>('/api/auth/me')
        user.value = res
      } catch {
        // Ignorar o expirar
      }
    }
  }

  return {
    token,
    refreshToken,
    user,
    isAuthenticated,
    login,
    demoLogin,
    refresh,
    fetchWithAuth,
    logout,
    initUser,
    apiBase,
  }
}
