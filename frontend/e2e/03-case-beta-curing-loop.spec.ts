import { test, expect } from '@playwright/test'

test.describe('AuraQx - Caso Beta (Hernioplastia - Documentos Faltantes y Subsanación sin Loops)', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('auraqx_tour_seen', 'true')
    })
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('Debe detectar documentos faltantes, permitir subsanación secuencial y aprobar sin bucles', async ({ page }) => {
    // 1. Seleccionar Caso Beta
    const caseBetaCard = page.locator('#case-selector').getByText('Hernioplastia').first()
    await expect(caseBetaCard).toBeVisible()
    await caseBetaCard.click()

    // 2. Verificar datos de Carlos Andrés Silva en el formulario
    const patientInput = page.locator('#clinical-form input[type="text"]').first()
    await expect(patientInput).toHaveValue('Carlos Andrés Silva')

    // 3. Iniciar la pre-autorización
    const runBtn = page.locator('#run-audit-btn')
    await runBtn.click()

    // 4. Esperar resolución y verificar estado DOCUMENTOS_FALTANTES
    const voucher = page.locator('#voucher-section')
    await expect(voucher).toBeVisible({ timeout: 40000 })
    await expect(voucher).toContainText(/DOCUMENTOS FALTANTES/)

    // 5. Verificar que el Portal de Documentos Faltantes esté visible
    const missingPortal = page.locator('#missing-docs-portal')
    await expect(missingPortal).toBeVisible()
    await expect(missingPortal).toContainText('Portal de Subsanación de Documentos Faltantes')

    // Debe mostrar dos requisitos faltantes (Ecografía y Riesgo Quirúrgico)
    const quickSolveButtons = missingPortal.locator('button:has-text("Subsanar Rápido")')
    await expect(quickSolveButtons).toHaveCount(2)

    // 6. Subsanar el primer documento (Ecografía)
    await quickSolveButtons.first().click()

    // Esperar a que se procese la subsanación (debe quedar solo 1 documento faltante, sin bucle)
    await expect(missingPortal.locator('button:has-text("Subsanar Rápido")')).toHaveCount(1, { timeout: 15000 })
    await expect(voucher).toContainText(/DOCUMENTOS FALTANTES/)
    await page.waitForTimeout(600)

    // 7. Subsanar el segundo documento (Riesgo Quirúrgico)
    const secondQuickBtn = missingPortal.locator('button:has-text("Subsanar Rápido")').first()
    await secondQuickBtn.click()

    // 8. Verificar que la resolución transicione automáticamente a PRE_APROBADO
    await expect(voucher).toContainText(/PRE-AUTORIZACIÓN APROBADA|PRE_APROBADO/, { timeout: 20000 })

    // Validar que el portal de faltantes desaparezca al estar aprobado
    await expect(missingPortal).not.toBeVisible()

    // Validar que el voucher muestre el porcentaje de cobertura
    await expect(voucher).toContainText(/80%|75%/)
  })
})
