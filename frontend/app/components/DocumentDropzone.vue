<script setup lang="ts">
import { ref } from 'vue'
import { UploadCloud, FileText, Loader2, Sparkles, CheckCircle } from 'lucide-vue-next'

const emit = defineEmits<{
  (e: 'file-uploaded', resolution: any): void
}>()

const isDragging = ref(false)
const isUploading = ref(false)
const fileName = ref<string | null>(null)
const uploadProgress = ref<string | null>(null)
const errorMsg = ref<string | null>(null)

const { fetchWithAuth, apiBase } = useAuth()

const handleFileUpload = async (file: File) => {
  if (!file) return
  fileName.value = file.name
  isUploading.value = true
  uploadProgress.value = 'IBM Docling analizando layout, tablas y OCR multimodal...'
  errorMsg.value = null

  try {
    const formData = new FormData()
    formData.append('file', file)

    const res = await fetchWithAuth('/api/preauth/analyze-upload', {
      method: 'POST',
      body: formData,
    })

    uploadProgress.value = '¡Extracción y resolución emitida con éxito!'
    setTimeout(() => {
      emit('file-uploaded', res)
      isUploading.value = false
    }, 400)
  } catch (err: any) {
    console.error('Error uploading file:', err)
    errorMsg.value = err.data?.detail || 'Error procesando documento con Docling'
    isUploading.value = false
  }
}

const onDrop = (e: DragEvent) => {
  isDragging.value = false
  if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
    handleFileUpload(e.dataTransfer.files[0])
  }
}

const onFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    handleFileUpload(target.files[0])
  }
}
</script>

<template>
  <div class="w-full">
    <div
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="onDrop"
      :class="[
        'rounded-2xl border-2 border-dashed p-6 text-center transition-all cursor-pointer relative overflow-hidden',
        isDragging
          ? 'border-cyan-400 bg-cyan-500/10 shadow-[0_0_25px_rgba(56,189,248,0.25)]'
          : 'border-white/15 bg-slate-900/30 hover:border-cyan-500/40 hover:bg-slate-900/50'
      ]"
    >
      <input
        type="file"
        accept=".pdf,.png,.jpg,.jpeg"
        class="absolute inset-0 opacity-0 cursor-pointer w-full h-full z-10"
        @change="onFileChange"
        :disabled="isUploading"
      />

      <div class="flex flex-col items-center justify-center gap-2.5 pointer-events-none">
        <div class="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-inner">
          <Loader2 v-if="isUploading" class="w-6 h-6 animate-spin text-cyan-400" />
          <UploadCloud v-else class="w-6 h-6" />
        </div>

        <div v-if="isUploading" class="space-y-1">
          <p class="text-sm font-bold text-white">{{ fileName }}</p>
          <p class="text-xs text-cyan-400 font-mono flex items-center justify-center gap-1.5 animate-pulse">
            <Sparkles class="w-3.5 h-3.5" />
            {{ uploadProgress }}
          </p>
        </div>

        <div v-else class="space-y-1">
          <p class="text-sm font-bold text-slate-100">
            Arrastra el Informe Médico Quirúrgico (PDF o Imagen)
          </p>
          <p class="text-xs text-slate-400">
            Procesado con <strong class="text-cyan-400">IBM Docling</strong> + <strong class="text-emerald-400">Dramatiq Worker</strong> para extracción off-thread sin latencia
          </p>
        </div>

        <div class="flex items-center gap-2 mt-1 text-[11px] text-slate-500 font-mono">
          <span>Formatos: PDF, PNG, JPG</span>
          <span>•</span>
          <span>Cola Asíncrona Dramatiq</span>
          <span>•</span>
          <span>Auditoría Instantánea</span>
        </div>
      </div>
    </div>

    <div v-if="errorMsg" class="mt-2 text-xs text-rose-400 font-mono text-center">
      {{ errorMsg }}
    </div>
  </div>
</template>
