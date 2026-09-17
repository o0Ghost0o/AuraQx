import { test, expect } from '@playwright/test'

test.describe('AuraQx - Casos Gamma (Rechazo por Carencia) y Delta (Excepción de Emergencia)', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('auraqx_tour_seen', 'true')
    })
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('Caso Gamma (Cesárea): Debe rechazar la pre-autorización por período de carencia no cumplido', async ({ page }) => {
    // 1. Seleccionar Caso Gamma (Cesárea)
    const caseGammaCard = page.locator('#case-selector').getByText('Cesárea').first()
    await expect(caseGammaCard).toBeVisible()
    await caseGammaCard.click()

    // 2. Verificar datos de Valeria Ramos
    const patientInput = page.locator('#clinical-form input[type="text"]').first()
    await expect(patientInput).toHaveValue('Valeria Sofía Ramos')

    // 3. Ejecutar auditoría
    await page.locator('#run-audit-btn').click()

    // 4. Validar resultado RECHAZADO en el voucher
    const voucher = page.locator('#voucher-section')
    await expect(voucher).toBeVisible({ timeout: 25000 })
    await expect(voucher).toContainText(/RECHAZADO|SOLICITUD NO AUTORIZADA/)

    // Validar explicación de carencia en la justificación
    await expect(voucher).toContainText(/carencia/i)
  })

  test('Caso Delta (Apendicectomía): Debe pre-aprobar de inmediato aplicando la excepción de emergencia vital (0 carencia)', async ({ page }) => {
    // 1. Seleccionar Caso Delta (Apendicectomía)
    const caseDeltaCard = page.locator('#case-selector').getByText('Apendicectomía').first()
    await expect(caseDeltaCard).toBeVisible()
    await caseDeltaCard.click()

    // 2. Verificar datos de Juan Diego Morales
    const patientInput = page.locator('#clinical-form input[type="text"]').first()
    await expect(patientInput).toHaveValue('Juan Diego Morales')

    // 3. Ejecutar auditoría
    await page.locator('#run-audit-btn').click()

    // 4. Validar resultado PRE_APROBADO
    const voucher = page.locator('#voucher-section')
    await expect(voucher).toBeVisible({ timeout: 25000 })
    await expect(voucher).toContainText(/PRE-AUTORIZACIÓN APROBADA|PRE_APROBADO/)

    // Validar que se mencione la emergencia quirúrgica vital
    await expect(voucher).toContainText('Emergencia')
  })
})
