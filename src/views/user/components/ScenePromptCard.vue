<script setup>
const props = defineProps({
  prompt: {
    type: Object,
    required: true
  }
})
</script>

<template>
  <div class="scene-prompt-card glass-panel w-64 p-4 cursor-pointer hover:shadow-xl transition-shadow" @click="$emit('click')">
    <p class="text-base-content/90 font-medium">{{ props.prompt.title }}</p>
  </div>
</template> 