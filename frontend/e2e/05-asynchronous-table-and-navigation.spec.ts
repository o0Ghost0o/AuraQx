import { test, expect } from '@playwright/test'

test.describe('AuraQx - Bandeja Asíncrona y Navegación entre Vistas', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('auraqx_tour_seen', 'true')
    })
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('Debe visualizar la Bandeja de Subsanación Asíncrona y permitir retomar un caso incompleto', async ({ page }) => {
    const tray = page.locator('#incomplete-cases-tray')
    await tray.scrollIntoViewIfNeeded()
    await expect(tray).toBeVisible()

    // Comprobar título de la bandeja
    await expect(tray).toContainText('Bandeja de Subsanación Asíncrona')

    // Si existen casos en la tabla, verificar el botón "Subsanar Caso"
    const solveBtns = tray.locator('button:has-text("Subsanar Caso")')
    const count = await solveBtns.count()
    if (count > 0) {
      await solveBtns.first().click()
      // Verificar que se cargue la resolución o portal en pantalla
      const voucherOrPortal = page.locator('#voucher-section, #missing-docs-portal').first()
      await expect(voucherOrPortal).toBeVisible({ timeout: 5000 })
    }
  })

  test('Debe navegar a la vista de Notion DB y renderizar el Live Mirror', async ({ page }) => {
    // Clic en enlace de navegación Notion DB
    const notionNav = page.locator('header nav a:has-text("Notion DB")')
    await expect(notionNav).toBeVisible()
    await notionNav.click()

    await expect(page).toHaveURL(/.*\/notion/)
    await expect(page.locator('h1').first()).toContainText(/Notion/i)
  })

  test('Debe navegar al Panel Auditor', async ({ page }) => {
    const auditorNav = page.locator('header nav a:has-text("Panel Auditor")')
    await expect(auditorNav).toBeVisible()
    await auditorNav.click()

    await expect(page).toHaveURL(/.*\/auditor/)
    await expect(page.locator('h1').first()).toContainText(/Auditor|Auditoría/i)
  })
})
