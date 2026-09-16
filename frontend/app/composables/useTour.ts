import { driver } from 'driver.js'
import 'driver.js/dist/driver.css'

export const useTour = () => {
  const startTour = () => {
    if (typeof window === 'undefined' || typeof document === 'undefined') return

    const rawSteps = [
      {
        element: '#hero-header',
        popover: {
          title: '🏥 AuraQx • Pre-Autorización Quirúrgica',
          description: '¡Bienvenido a AuraQx (Reto 1)! Esta plataforma reduce el tiempo de aprobación quirúrgica de días u horas a tan sólo segundos de certeza médica en tiempo real, integrando el informe hospitalario con la póliza en Notion DB.',
          side: 'bottom',
          align: 'start',
        },
      },
      {
        element: '#case-selector',
        popover: {
          title: '🎯 Selector de Casos Clínicos (1-Click)',
          description: 'Selecciona cualquiera de los 4 casos de prueba preparados: Colecistectomía aprobada, Hernioplastia con documentos faltantes, Cesárea rechazada por carencia insuficiente, o Apendicectomía con excepción inmediata de 0 días por emergencia vital.',
          side: 'bottom',
          align: 'start',
        },
      },
      {
        element: '#docling-dropzone',
        popover: {
          title: '📄 Ingestión Multimodal con IBM Docling',
          description: 'Arrastra y somete informes médicos hospitalarios en PDF o imágenes escaneadas. El pipeline ejecuta OCR, análisis de layout y tablas de alta fidelidad.',
          side: 'bottom',
          align: 'start',
        },
      },
      {
        element: '#case-package-viewer',
        popover: {
          title: '📦 Expediente Clínico y Descarga .ZIP',
          description: 'Explora y descarga los paquetes de admisión clínica oficiales (.ZIP) que contienen informes operatorios, notas de evolución, biometrías y presupuestos hospitalarios.',
          side: 'bottom',
          align: 'start',
        },
      },
      {
        element: '#clinical-form',
        popover: {
          title: '🩺 Formulario Quirúrgico Parametrizable',
          description: 'Visualiza y ajusta en vivo los parámetros clínicos: Paciente, Cédula Notion, Diagnóstico CIE-10, Procedimiento CPT, Hospital de la Red, Presupuesto USD y estudios prequirúrgicos adjuntos.',
          side: 'right',
          align: 'start',
        },
      },
      {
        element: '#run-audit-btn',
        popover: {
          title: '⚡ Iniciar Pre-Autorización Quirúrgica',
          description: 'Al pulsar este botón, el agente de IA consulta en vivo la base de datos de Notion, valida las cláusulas de carencia, audita los estudios indispensables y emite la resolución en tiempo real.',
          side: 'top',
          align: 'center',
        },
      },
      {
        element: '#telemetry-radar',
        popover: {
          title: '📡 Radar de Telemetría Agéntica SSE',
          description: 'Supervisa en vivo cada una de las 6 etapas del razonamiento clínico transmitidas vía Server-Sent Events (SSE) sin recargar la página.',
          side: 'left',
          align: 'start',
        },
      },
      {
        element: '#voucher-section',
        popover: {
          title: '🎫 Voucher Holográfico y QR Verificable',
          description: 'Certificado oficial con desglose financiero exacto (cobertura vs copago del paciente), código QR criptográfico para admisión hospitalaria y enlace directo a la fila en Notion DB.',
          side: 'left',
          align: 'start',
        },
      },
      {
        element: '#missing-docs-portal',
        popover: {
          title: '⚠️ Portal de Subsanación de Faltantes',
          description: 'En casos con documentos incompletos (como el Caso 2 de Hernioplastia), sube archivos propios con OCR o usa la subsanación en 1-click para recalcular el caso a PRE-APROBADO.',
          side: 'left',
          align: 'start',
        },
      },
      {
        element: '#incomplete-cases-tray',
        popover: {
          title: '📥 Bandeja de Subsanación Asíncrona',
          description: 'Bandeja persistente donde las clínicas y auditores pueden consultar y retomar casos con documentos incompletos de forma asíncrona cuando el paciente traiga los estudios pendientes.',
          side: 'top',
          align: 'start',
        },
      },
      {
        element: '#system-documentation',
        popover: {
          title: '📚 Documentación Técnica Integral',
          description: 'Especificación técnica completa del sistema: Fórmulas matemáticas de deducibles/copagos, reglas de carencia, arquitectura FastAPI + Nuxt 4, esquema de Notion DB y catálogo de APIs.',
          side: 'top',
          align: 'start',
        },
      },
    ]

    // Filtrar únicamente elementos presentes en el DOM para evitar fallos
    const activeSteps = rawSteps.filter((step) => {
      const el = document.querySelector(step.element)
      return el !== null
    })

    if (activeSteps.length === 0) return

    const driverObj = driver({
      showProgress: true,
      animate: true,
      allowClose: true,
      nextBtnText: 'Siguiente →',
      prevBtnText: '← Anterior',
      doneBtnText: '¡Finalizar Tour! 🚀',
      steps: activeSteps as any,
    })

    driverObj.drive()
  }

  return {
    startTour,
  }
}
