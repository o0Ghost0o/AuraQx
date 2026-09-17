import { test, expect } from '@playwright/test'

test.describe('AuraQx - Caso Alfa (Colecistectomía Laparoscópica - Pre-Aprobado)', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('auraqx_tour_seen', 'true')
    })
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('Debe procesar el Caso Alfa y emitir la Pre-Aprobación con Voucher Holográfico y QR', async ({ page }) => {
    // 1. Asegurar que el Caso Alfa esté seleccionado
    const caseAlfaCard = page.locator('#case-selector').getByText('Colecistectomía').first()
    await expect(caseAlfaCard).toBeVisible()
    await caseAlfaCard.click()

    // 2. Verificar datos en el formulario clínico
    const patientInput = page.locator('#clinical-form input[type="text"]').first()
    await expect(patientInput).toHaveValue('María Carmen Mendoza')

    // 3. Iniciar la auditoría agéntica en tiempo real
    const runBtn = page.locator('#run-audit-btn')
    await expect(runBtn).toBeVisible()
    await runBtn.click()

    // 4. Esperar a que el radar de telemetría registre los eventos SSE
    const radar = page.locator('#telemetry-radar')
    await expect(radar).toBeVisible()
    await expect(radar).toContainText(/Paso [1-6] \/ 6/)

    // 5. Verificar que aparezca el Voucher Holográfico
    const voucher = page.locator('#voucher-section')
    await expect(voucher).toBeVisible({ timeout: 25000 })

    // Validar estado de resolución
    await expect(voucher).toContainText(/PRE-AUTORIZACIÓN APROBADA|PRE_APROBADO/)
    await expect(voucher).toContainText('María Carmen Mendoza')
    await expect(voucher).toContainText('Colecistectomía laparoscópica')

    // Validar desglose financiero
    await expect(voucher).toContainText('80%')

    // Validar código QR generado
    const qrCanvas = voucher.locator('canvas')
    await expect(qrCanvas).toBeVisible()
  })
})
