import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
  compatibilityDate: '2025-09-01',
  future: {
    compatibilityVersion: 4,
  },
  ssr: false,
  devtools: { enabled: false },
  css: ['~/assets/css/main.css'],
  modules: ['@vite-pwa/nuxt'],
  vite: {
    plugins: [tailwindcss()],
  },
  pwa: {
    strategies: 'generateSW',
    registerType: 'autoUpdate',
    manifest: {
      name: 'AuraQx — Pre-Autorización Quirúrgica',
      short_name: 'AuraQx',
      lang: 'es',
      description: 'Agente de IA para Pre-Autorización Quirúrgica en Tiempo Real (HackIAthon)',
      display: 'standalone',
      orientation: 'portrait',
      theme_color: '#070b14',
      background_color: '#070b14',
      start_url: '/',
      scope: '/',
      id: '/',
      icons: [
        {
          src: '/icons/icon-192.png',
          sizes: '192x192',
          type: 'image/png',
          purpose: 'any',
        },
        {
          src: '/icons/icon-512.png',
          sizes: '512x512',
          type: 'image/png',
          purpose: 'any',
        },
        {
          src: '/icons/icon-512.png',
          sizes: '512x512',
          type: 'image/png',
          purpose: 'maskable',
        },
      ],
    },
    workbox: {
      navigateFallback: '/',
      globPatterns: ['**/*.{js,css,html,svg,png,ico}'],
      runtimeCaching: [
        {
          urlPattern: /^.*\/(api)\/.*/,
          handler: 'NetworkOnly',
        },
      ],
    },
    devOptions: {
      enabled: true,
      suppressWarnings: true,
    },
  },
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
    },
  },
  app: {
    head: {
      htmlAttrs: { lang: 'es' },
      title: 'AuraQx — Pre-Autorización Quirúrgica en Tiempo Real',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover' },
        { name: 'description', content: 'Agente de IA que evalúa informes médicos, pólizas en Notion y carencias para emitir pre-aprobaciones instantáneas.' },
        { name: 'theme-color', content: '#070b14' },
        { name: 'apple-mobile-web-app-capable', content: 'yes' },
        { name: 'apple-mobile-web-app-status-bar-style', content: 'black-translucent' },
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap',
        },
      ],
    },
  },
})
