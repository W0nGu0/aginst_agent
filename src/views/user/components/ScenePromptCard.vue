<script setup>
const props = defineProps({
  prompt: {
    type: Object,
    required: true
  }
})

// 格式化标题，在冒号后添加HTML换行标签
function formatTitle(title) {
  return title.replace(/[：:]/g, '$&<br>');
}
</script>

<template>
  <div class="scene-prompt-card glass-panel w-80 p-4 cursor-pointer hover:shadow-xl transition-shadow" @click="$emit('click')">
    <p class="text-base-content/90 font-medium line-clamp-2 h-14" v-html="formatTitle(props.prompt.title)"></p>
  </div>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>