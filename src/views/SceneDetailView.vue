<template>
  <div class="scene-detail-view">
    <div class="glass-panel p-8 mb-8">
      <div class="flex flex-col md:flex-row items-start justify-between gap-6 mb-6">
        <h1 class="text-3xl font-bold text-base-content flex items-center">
          <span class="inline-block w-3 h-8 bg-gradient-to-b from-primary to-secondary rounded mr-4"></span>
          场景详情
        </h1>
        <button
          @click="$router.push('/topology')"
          class="btn btn-primary">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2" />
          </svg>
          进入拓扑设计
        </button>
      </div>
      
      <div class="divider-gradient"></div>
      
      <!-- 场景信息 -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-10">
        <div class="col-span-1 lg:col-span-2">
          <h2 class="text-2xl font-semibold mb-6 text-gradient">
            {{ currentScene?.title || '企业内网渗透场景：多层防御网络架构下的横向移动与权限提升' }}
          </h2>
          <div class="prose prose-invert max-w-none">
            <p class="text-base-content/80 text-lg leading-relaxed mb-6">本场景模拟一个企业内网环境，包含多层网络防御架构，设计真实的攻防体验。</p>
            
            <div class="bg-base-300/30 p-6 rounded-lg border-l-4 border-primary mb-6">
              <h3 class="text-lg font-medium mb-3 flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                关键组件
              </h3>
              <ul class="space-y-2 ml-6">
                <li class="flex items-start">
                  <span class="text-primary mr-2">•</span>
                  <span>外围防火墙与DMZ区</span>
                </li>
                <li class="flex items-start">
                  <span class="text-primary mr-2">•</span>
                  <span>内网安全域划分</span>
                </li>
                <li class="flex items-start">
                  <span class="text-primary mr-2">•</span>
                  <span>核心业务系统区域</span>
                </li>
                <li class="flex items-start">
                  <span class="text-primary mr-2">•</span>
                  <span>管理网络区域</span>
                </li>
                <li class="flex items-start">
                  <span class="text-primary mr-2">•</span>
                  <span>各类安全设备（IDS/IPS/WAF等）</span>
                </li>
              </ul>
            </div>
            <p class="text-base-content/80">参与者需要识别网络架构中的弱点，执行渗透测试流程，尝试从外部网络突破至内部核心系统。</p>
          </div>
        </div>
        
        <div class="glass-panel p-6 h-fit">
          <h3 class="text-lg font-medium mb-4 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            场景信息
          </h3>
          <div class="space-y-4">
            <div class="flex justify-between items-center pb-2 border-b border-base-300/30">
              <span class="text-base-content/70">场景类型</span>
              <span class="badge badge-primary">网络渗透</span>
            </div>
            <div class="flex justify-between items-center pb-2 border-b border-base-300/30">
              <span class="text-base-content/70">难度等级</span>
              <div class="rating rating-sm">
                <input type="radio" name="rating-2" class="mask mask-star-2 bg-orange-400" checked />
                <input type="radio" name="rating-2" class="mask mask-star-2 bg-orange-400" checked />
                <input type="radio" name="rating-2" class="mask mask-star-2 bg-orange-400" checked />
                <input type="radio" name="rating-2" class="mask mask-star-2 bg-orange-400" />
                <input type="radio" name="rating-2" class="mask mask-star-2 bg-orange-400" />
              </div>
            </div>
            <div class="flex justify-between items-center pb-2 border-b border-base-300/30">
              <span class="text-base-content/70">预计时间</span>
              <span>45-60分钟</span>
            </div>
            <div class="flex justify-between items-center pb-2 border-b border-base-300/30">
              <span class="text-base-content/70">生成时间</span>
              <span>{{ new Date().toLocaleDateString() }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-base-content/70">适用对象</span>
              <span class="badge badge-secondary">安全工程师</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 场景目标 -->
      <div class="mb-10">
        <h2 class="text-xl font-semibold mb-6 flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
          场景目标
        </h2>
        <div class="bg-gradient-to-r from-base-300/50 to-base-300/10 rounded-lg p-6">
          <ul class="space-y-4">
            <li class="flex items-start">
              <div class="inline-flex items-center justify-center bg-primary/20 text-primary rounded-full w-8 h-8 mr-4 flex-shrink-0 shadow-glow-sm">1</div>
              <div>
                <h4 class="font-medium">通过外网扫描发现可能的入口点</h4>
                <p class="text-base-content/70 text-sm mt-1">识别暴露的服务和可能的漏洞，突破外围防御</p>
              </div>
            </li>
            <li class="flex items-start">
              <div class="inline-flex items-center justify-center bg-primary/20 text-primary rounded-full w-8 h-8 mr-4 flex-shrink-0 shadow-glow-sm">2</div>
              <div>
                <h4 class="font-medium">在内网中进行横向移动</h4>
                <p class="text-base-content/70 text-sm mt-1">利用内网漏洞和配置错误，绕过分段防御机制</p>
              </div>
            </li>
            <li class="flex items-start">
              <div class="inline-flex items-center justify-center bg-primary/20 text-primary rounded-full w-8 h-8 mr-4 flex-shrink-0 shadow-glow-sm">3</div>
              <div>
                <h4 class="font-medium">获取核心业务系统的访问权限</h4>
                <p class="text-base-content/70 text-sm mt-1">突破内部防御，获得数据库和应用系统访问</p>
              </div>
            </li>
            <li class="flex items-start">
              <div class="inline-flex items-center justify-center bg-primary/20 text-primary rounded-full w-8 h-8 mr-4 flex-shrink-0 shadow-glow-sm">4</div>
              <div>
                <h4 class="font-medium">提取敏感信息并实现数据外传</h4>
                <p class="text-base-content/70 text-sm mt-1">找到并获取核心数据，建立秘密通信通道</p>
              </div>
            </li>
            <li class="flex items-start">
              <div class="inline-flex items-center justify-center bg-primary/20 text-primary rounded-full w-8 h-8 mr-4 flex-shrink-0 shadow-glow-sm">5</div>
              <div>
                <h4 class="font-medium">清理痕迹，维持后门访问</h4>
                <p class="text-base-content/70 text-sm mt-1">移除攻击痕迹，建立隐蔽的持久访问机制</p>
              </div>
            </li>
          </ul>
        </div>
      </div>
      
      <!-- 网络架构预览 -->
      <div>
        <h2 class="text-xl font-semibold mb-6 flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
          </svg>
          网络架构预览
        </h2>
        <div class="cyber-bg rounded-lg h-80 flex items-center justify-center border border-white/5">
          <div class="text-center">
            <div class="text-6xl mb-4 opacity-30">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-20 w-20 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
            </div>
            <p class="text-base-content/50 text-lg">点击"进入拓扑设计"开始构建网络拓扑图</p>
            <button 
              @click="$router.push('/topology')" 
              class="btn btn-outline btn-sm mt-4">
              进入设计
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 按钮组 -->
    <div class="flex justify-end space-x-4">
      <button @click="$router.push('/')" class="btn btn-outline">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        返回首页
      </button>
      <button @click="$router.push('/topology')" class="btn btn-primary">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5" />
        </svg>
        进入拓扑设计
      </button>
    </div>
  </div>
</template>

<script setup>
import { useAppStore } from '../stores/app'

const appStore = useAppStore()
const currentScene = appStore.currentScene
</script>

<style scoped>
.divider {
  height: 1px;
  background: linear-gradient(to right, transparent, rgba(var(--primary-rgb), 0.2), transparent);
  margin: 1.5rem 0;
}

:deep(.btn) {
  @apply rounded-lg;
}

:deep(.btn-primary) {
  @apply bg-gradient-to-r from-primary to-secondary border-0;
}

:deep(.badge-primary) {
  @apply bg-primary/20 text-primary border-primary/30;
}
</style> 