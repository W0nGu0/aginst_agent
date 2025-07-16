<template>
  <div class="p-6 md:p-10 history-bg overflow-auto">
    <h1 class="text-3xl font-bold mb-8 text-gradient animate-gradient">推演记录</h1>

    <div class="w-full overflow-x-auto glass-panel">
      <table class="min-w-full text-left">
        <thead>
          <tr class="border-b border-base-300 text-base-content/80">
            <th class="px-6 py-3"><span class="flex items-center gap-2"><img src="/演练记录ico/date.svg" class="w-4 h-4" /> 日期</span></th>
            <th class="px-6 py-3"><span class="flex items-center gap-2"><img src="/演练记录ico/scene.svg" class="w-4 h-4" /> 场景</span></th>
            <th class="px-6 py-3"><span class="flex items-center gap-2"><img src="/演练记录ico/group.svg" class="w-4 h-4" /> 参与者组成</span></th>
            <th class="px-6 py-3 text-right"><span class="flex items-center gap-2 justify-end"><img src="/演练记录ico/view.svg" class="w-4 h-4" /> 查看详情</span></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.id" class="border-b border-base-300 hover:bg-base-100/40 transition-colors">
            <td class="px-6 py-3 whitespace-nowrap">{{ row.date }}</td>
            <td class="px-6 py-3">{{ row.scene }}</td>
            <td class="px-6 py-3">{{ row.group }}</td>
            <td class="px-6 py-3 text-right">
              <button class="btn btn-primary btn-sm transition-transform hover:-translate-y-0.5" @click="viewDetail(row.id)">点击详情</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 生成示例数据
function randomGroup() {
  const list = ['智能对抗', '攻击参与', '防御参与']
  return list[Math.floor(Math.random()*list.length)]
}
const scenes = ['金融', '培训', '医疗', '能源', '政务']
function randomScene() { return scenes[Math.floor(Math.random()*scenes.length)] }

const rows = ref(Array.from({ length: 15 }, (_, i) => ({
  id: i+1,
  date: new Date(Date.now() - i*86400000).toISOString().slice(0,16).replace('T',' '),
  scene: randomScene(),
  group: randomGroup()
})))

function viewDetail(id) {
  window.location.hash = `#/history/${id}`
}
</script>

<style scoped>
.history-bg::before {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(45deg, rgba(var(--primary-rgb),0.03) 0 10px, transparent 10px 20px);
  pointer-events: none;
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
.animate-gradient {
  background-size: 200% 200%;
  animation: gradientShift 8s ease infinite;
}
</style> 