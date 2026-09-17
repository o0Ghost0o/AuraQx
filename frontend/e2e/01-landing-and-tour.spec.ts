import { test, expect } from '@playwright/test'

test.describe('AuraQx - Landing Page y Tour Guiado (driver.js)', () => {
  test.beforeEach(async ({ page }) => {
    // Evitar que el tour se auto-abra si ya se vio para controlar su activación explícita
    await page.addInitScript(() => {
      localStorage.setItem('auraqx_tour_seen', 'true')
    })
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('Debe renderizar correctamente el encabezado, hero y componentes principales', async ({ page }) => {
    // 1. Validar título y logo
    await expect(page).toHaveTitle(/AuraQx/i)
    await expect(page.locator('header')).toContainText('AuraQx')
    await expect(page.locator('header')).toContainText('RETO 1')

    // 2. Validar Hero Header
    const hero = page.locator('#hero-header')
    await expect(hero).toBeVisible()
    await expect(hero).toContainText('Agente de Pre-Autorización Quirúrgica')

    // 3. Validar Selector de Casos y Formulario
    await expect(page.locator('#case-selector')).toBeVisible()
    await expect(page.locator('#docling-dropzone')).toBeVisible()
    await expect(page.locator('#clinical-form')).toBeVisible()
    await expect(page.locator('#run-audit-btn')).toBeVisible()

    // 4. Validar Radar de Telemetría
    await expect(page.locator('#telemetry-radar')).toBeVisible()

    // 5. Validar Bandeja Asíncrona
    await expect(page.locator('#incomplete-cases-tray')).toBeVisible()

    // 6. Validar Sección de Documentación Técnica
    await expect(page.locator('#system-documentation')).toBeVisible()
  })

  test('Debe iniciar y navegar por el Tour Guiado interactivo de driver.js', async ({ page }) => {
    // Buscar y hacer clic en el botón de Tour Guiado en el Hero
    const tourBtn = page.locator('#hero-header button:has-text("Tour Guiado")')
    await expect(tourBtn).toBeVisible()
    await tourBtn.click()

    // Comprobar que el popover de driver.js aparezca en el DOM
    const popover = page.locator('.driver-popover')
    await expect(popover).toBeVisible()
    await expect(popover.locator('.driver-popover-title')).toContainText('AuraQx')

    // Avanzar al siguiente paso del tour
    const nextBtn = popover.locator('.driver-popover-next-btn')
    await expect(nextBtn).toBeVisible()
    await nextBtn.click()

    // Verificar que el paso 2 muestre el Selector de Casos
    await expect(popover.locator('.driver-popover-title')).toContainText('Selector de Casos')

    // Cerrar el tour
    const closeBtn = popover.locator('.driver-popover-close-btn')
    await closeBtn.click()
    await expect(popover).not.toBeVisible()
  })

  test('Debe alternar entre las pestañas de la Documentación Técnica', async ({ page }) => {
    const docs = page.locator('#system-documentation')
    await docs.scrollIntoViewIfNeeded()

    // Pestaña por defecto: Visión & Reto 1
    await expect(docs).toContainText('El Problema Actual (Status Quo)')
    await expect(docs).toContainText('La Solución AuraQx (Reto 1)')

    // Cambiar a pestaña: Pipeline Agéntico & Carencias
    const pipelineTab = docs.locator('button:has-text("Pipeline Agéntico")')
    await pipelineTab.click()
    await expect(docs).toContainText('Pipeline Agéntico en 6 Fases')
    await expect(docs).toContainText('Fórmulas Matemáticas de Liquidación')

    // Cambiar a pestaña: Integración Notion DB
    const notionTab = docs.locator('button:has-text("Integración Notion DB")')
    await notionTab.click()
    await expect(docs).toContainText('Arquitectura de Integración Dual con Notion')
    await expect(docs).toContainText('DB 1: Pólizas de Asegurados')

    // Cambiar a pestaña: Seguridad & Credenciales
    const securityTab = docs.locator('button:has-text("Seguridad & Credenciales")')
    await securityTab.click()
    await expect(docs).toContainText('Credenciales de Prueba para Evaluadores')
    await expect(docs).toContainText('auditor_clinico')
  })
})
