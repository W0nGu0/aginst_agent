<template>
  <div class="tool-item glass-panel p-4 hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
    <div class="flex items-center justify-between">
      <!-- 工具信息 -->
      <div class="flex items-center flex-1">
        <!-- 工具图标 -->
        <div class="w-10 h-10 rounded-lg flex items-center justify-center mr-4 shadow-sm"
             :class="tool.enabled ? 'bg-gradient-to-br from-success/80 to-success' : 'bg-gradient-to-br from-base-300 to-base-200'">
          <svg xmlns="http://www.w3.org/2000/svg" 
               class="h-5 w-5" 
               :class="tool.enabled ? 'text-white' : 'text-base-content/60'"
               fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="toolIcon" />
          </svg>
        </div>
        
        <!-- 工具详情 -->
        <div class="flex-1">
          <div class="flex items-center mb-1">
            <h3 class="font-semibold text-base-content mr-3">{{ tool.name }}</h3>
            <span class="badge badge-sm" :class="tool.enabled ? 'badge-success' : 'badge-ghost'">
              {{ tool.enabled ? '已启用' : '已禁用' }}
            </span>
          </div>
          <p class="text-sm text-base-content/60">{{ toolDescription }}</p>
          
          <!-- 工具标签 -->
          <div class="flex flex-wrap gap-1 mt-2">
            <span v-for="tag in toolTags" :key="tag" 
                  class="badge badge-xs badge-outline">
              {{ tag }}
            </span>
          </div>
        </div>
      </div>
      
      <!-- 开关控制 -->
      <div class="ml-4">
        <label class="inline-flex items-center cursor-pointer">
          <span class="relative">
            <input 
              type="checkbox" 
              class="sr-only" 
              :checked="tool.enabled" 
              @change="$emit('toggle', tool)"
            />
            <div class="w-12 h-6 rounded-full shadow-inner transition-all duration-300"
                 :class="tool.enabled ? 'bg-success' : 'bg-base-300'">
            </div>
            <div class="dot absolute left-1 top-1 bg-white w-4 h-4 rounded-full transition-transform duration-300 shadow-sm"
                 :class="tool.enabled ? 'translate-x-6' : 'translate-x-0'">
            </div>
          </span>
        </label>
      </div>
    </div>
    
    <!-- 工具详细信息（可展开） -->
    <div v-if="showDetails" class="mt-4 pt-4 border-t border-white/10">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
        <div>
          <span class="text-base-content/60">类型：</span>
          <span class="font-medium">{{ toolType }}</span>
        </div>
        <div>
          <span class="text-base-content/60">风险等级：</span>
          <span class="font-medium" :class="riskLevelClass">{{ riskLevel }}</span>
        </div>
        <div>
          <span class="text-base-content/60">执行时间：</span>
          <span class="font-medium">{{ executionTime }}</span>
        </div>
      </div>
    </div>
    
    <!-- 展开/收起按钮 -->
    <div class="flex justify-center mt-3">
      <button 
        class="btn btn-ghost btn-xs"
        @click="showDetails = !showDetails"
      >
        <svg xmlns="http://www.w3.org/2000/svg" 
             class="h-4 w-4 transition-transform duration-200"
             :class="showDetails ? 'rotate-180' : ''"
             fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
        {{ showDetails ? '收起' : '详情' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  tool: Object,
  index: Number
})

defineEmits(['toggle'])

const showDetails = ref(false)

// 工具图标映射
const toolIcon = computed(() => {
  const iconMap = {
    '扫描': 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z',
    '抓取': 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253',
    '生成': 'M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z',
    '查询': 'M9 5H7a2 2 0 00-2 2v6a2 2 0 002 2h2m5 0h2a2 2 0 002-2V7a2 2 0 00-2-2h-2m-5 4h5',
    '收集': 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10',
    '搜索': 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z',
    '执行': 'M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M15 14h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
    '命令': 'M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
    '修复': 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z',
    '阻断': 'M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L12 21l-6.364-6.364M5.636 5.636L12 3l6.364 6.364',
    '隔离': 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z',
    '检测': 'M15 12a3 3 0 11-6 0 3 3 0 016 0z',
    '获取': 'M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10',
    '计算': 'M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z',
    '报告': 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    '更新': 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15'
  }
  
  // 根据工具名称匹配图标
  for (const [key, icon] of Object.entries(iconMap)) {
    if (props.tool.name.includes(key)) {
      return icon
    }
  }
  
  return 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z'
})

// 工具描述
const toolDescription = computed(() => {
  const descriptions = {
    '列出现有场景模板工具': '获取系统中所有可用的攻防场景模板',
    '获取模板详情工具': '查看特定场景模板的详细配置信息',
    '根据模板创建场景工具': '基于选定模板快速创建攻防场景实例',
    '销毁场景实例工具': '安全清理和销毁不再需要的场景实例',
    '列出正在运行场景工具': '监控当前活跃的攻防场景状态',
    '启动容器组工具': '批量启动场景所需的容器服务',
    '移除容器工具': '清理和移除指定的容器实例',
    '创建虚拟网络工具': '构建隔离的虚拟网络环境',
    '清理虚拟网络工具': '清理不再使用的网络资源',
    '端口扫描工具': '探测目标主机的开放端口和服务',
    'URL抓取工具': '自动化网页内容抓取和分析',
    '钓鱼邮件生成工具': '生成用于社工测试的钓鱼邮件',
    '邮箱泄露查询工具': '查询邮箱是否存在数据泄露记录',
    '凭据收集模拟工具': '模拟凭据窃取攻击行为',
    '漏洞搜索工具': '搜索已知的安全漏洞信息',
    '漏洞利用执行工具': '执行特定漏洞的利用代码',
    '远程命令执行工具': '在目标系统上执行远程命令',
    '网络信息收集工具': '收集目标网络的详细信息',
    '恶意文档生成工具': '生成包含恶意代码的文档文件',
    '性勒索邮件生成工具': '生成勒索软件相关的邮件内容',
    '亲和聊天脚本工具': '生成社交工程攻击的聊天脚本',
    '虚假Offer邮件生成工具': '生成虚假工作机会的钓鱼邮件',
    '漏洞扫描工具': '自动扫描系统中的安全漏洞',
    '自动打补丁工具': '自动下载并安装安全补丁',
    '修改配置文件工具': '修改系统配置以提升安全性',
    '重启服务工具': '重启系统服务以应用安全配置',
    '防火墙阻断恶意流量工具': '配置防火墙规则阻断威胁',
    '隔离受害主机工具': '将受感染主机从网络中隔离',
    '终止主机恶意进程工具': '识别并终止恶意进程',
    '隔离恶意文件工具': '隔离检测到的恶意文件',
    'ip威胁查询工具': '查询IP地址的威胁情报信息',
    '哈希文件威胁查询工具': '通过文件哈希查询威胁信息',
    '检测恶意通信和数据外传工具': '监控异常的网络通信行为',
    '检测恶意进程工具': '识别系统中的恶意进程',
    '检测恶意文件工具': '扫描和识别恶意文件',
    '检测恶意网络流量工具': '分析网络流量中的威胁',
    '数据获取工具': '收集攻防演练过程中的各类数据',
    '场景拓扑获取工具': '获取当前场景的网络拓扑信息',
    '攻击量化指标计算工具': '计算攻击行为的量化指标',
    '防御量化指标计算工具': '评估防御措施的有效性',
    '报告生成工具': '自动生成攻防演练报告',
    '长期人员画像更新工具': '更新参与人员的能力画像',
    '长期攻击agent性能更新工具': '优化攻击代理的性能参数',
    '长期防御agent性能更新工具': '优化防御代理的性能参数'
  }
  
  return descriptions[props.tool.name] || '智能工具，提供专业的攻防能力支持'
})

// 工具标签
const toolTags = computed(() => {
  const tags = []
  
  if (props.tool.name.includes('扫描') || props.tool.name.includes('检测')) {
    tags.push('检测')
  }
  if (props.tool.name.includes('生成') || props.tool.name.includes('创建')) {
    tags.push('生成')
  }
  if (props.tool.name.includes('修复') || props.tool.name.includes('打补丁')) {
    tags.push('修复')
  }
  if (props.tool.name.includes('阻断') || props.tool.name.includes('隔离')) {
    tags.push('防护')
  }
  if (props.tool.name.includes('查询') || props.tool.name.includes('获取')) {
    tags.push('查询')
  }
  if (props.tool.name.includes('计算') || props.tool.name.includes('分析')) {
    tags.push('分析')
  }
  
  // 根据工具类型添加风险标签
  if (props.tool.name.includes('钓鱼') || props.tool.name.includes('恶意') || props.tool.name.includes('勒索')) {
    tags.push('高风险')
  } else if (props.tool.name.includes('扫描') || props.tool.name.includes('收集')) {
    tags.push('中风险')
  } else {
    tags.push('低风险')
  }
  
  return tags
})

// 工具类型
const toolType = computed(() => {
  if (props.tool.name.includes('扫描') || props.tool.name.includes('检测')) return '检测类'
  if (props.tool.name.includes('生成') || props.tool.name.includes('创建')) return '生成类'
  if (props.tool.name.includes('修复') || props.tool.name.includes('打补丁')) return '修复类'
  if (props.tool.name.includes('阻断') || props.tool.name.includes('隔离')) return '防护类'
  if (props.tool.name.includes('查询') || props.tool.name.includes('获取')) return '查询类'
  if (props.tool.name.includes('计算') || props.tool.name.includes('分析')) return '分析类'
  return '通用类'
})

// 风险等级
const riskLevel = computed(() => {
  if (props.tool.name.includes('钓鱼') || props.tool.name.includes('恶意') || props.tool.name.includes('勒索')) return '高'
  if (props.tool.name.includes('扫描') || props.tool.name.includes('收集') || props.tool.name.includes('执行')) return '中'
  return '低'
})

const riskLevelClass = computed(() => {
  switch (riskLevel.value) {
    case '高': return 'text-error'
    case '中': return 'text-warning'
    default: return 'text-success'
  }
})

// 执行时间
const executionTime = computed(() => {
  const times = ['1-5秒', '5-30秒', '30秒-2分钟', '2-10分钟', '10分钟以上']
  return times[props.index % times.length]
})
</script>

<style scoped>
.tool-item {
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.tool-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.dot {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}
</style>
