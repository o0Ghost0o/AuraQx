<script setup lang="ts">
interface Props {
  variant?: 'default' | 'interactive' | 'glow-cyan' | 'glow-emerald' | 'glow-amber' | 'glow-rose'
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  class: '',
})

const variantClass = computed(() => {
  switch (props.variant) {
    case 'interactive':
      return 'glass-panel-interactive'
    case 'glow-cyan':
      return 'glass-panel glow-cyan'
    case 'glow-emerald':
      return 'glass-panel glow-emerald'
    case 'glow-amber':
      return 'glass-panel glow-amber'
    case 'glow-rose':
      return 'glass-panel glow-rose'
    default:
      return 'glass-panel'
  }
})
</script>

<template>
  <div :class="[variantClass, 'rounded-2xl p-6 transition-all duration-300 relative overflow-hidden', props.class]">
    <!-- Ambient subtle top light line -->
    <div class="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-white/20 to-transparent" />
    <slot />
  </div>
</template>
