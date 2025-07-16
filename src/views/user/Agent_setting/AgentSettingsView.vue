<template>
  <div class="settings-bg relative overflow-hidden p-6 md:p-10">
    <!-- 页面标题 -->
    <h1 class="text-3xl font-bold mb-8 text-gradient animate-gradient">Agent 功能开关</h1>

    <!-- 说明卡片 -->
    <div class="glass-panel p-6 mb-10">
      <p class="text-base-content/70">通过切换下列 Tool 的 ON / OFF，可精细控制各个 AI Agent 的能力，以满足不同攻防推演场景的需求。</p>
    </div>

    <!-- Agent 列表 -->
    <div class="space-y-4">
      <CollapsibleItem
        v-for="(agent,index) in agents"
        :key="index"
        :item="agent"
        level="agent"
        @toggle-tool="toggleTool"
      />
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import CollapsibleItem from './components/CollapsibleItem.vue'

// 初步数据结构（后续可从后端 / 配置加载）
const agents = reactive([
  {
    name: '场景生成 Agent',
    children: [
      {
        name: '场景服务',
        children: [
          { name: '列出现有场景模板工具', enabled: true },
          { name: '获取模板详情工具', enabled: true },
          { name: '根据模板创建场景工具', enabled: true },
          { name: '销毁场景实例工具', enabled: true },
          { name: '列出正在运行场景工具', enabled: true }
        ]
      },
      {
        name: '容器服务',
        children: [
          { name: '启动容器组工具', enabled: true },
          { name: '移除容器工具', enabled: true },
          { name: '创建虚拟网络工具', enabled: true },
          { name: '清理虚拟网络工具', enabled: true }
        ]
      }
    ]
  },
  {
    name: '攻击 Agent',
    children: [
      {
        name: '攻击服务',
        children: [
          { name: '端口扫描工具', enabled: true },
          { name: 'URL抓取工具', enabled: true },
          { name: '钓鱼邮件生成工具', enabled: false },
          { name: '邮箱泄露查询工具', enabled: true },
          { name: '凭据收集模拟工具', enabled: false },
          { name: '漏洞搜索工具', enabled: true },
          { name: '漏洞利用执行工具', enabled: true },
          { name: '远程命令执行工具', enabled: true },
          { name: '网络信息收集工具', enabled: true },
          { name: '恶意文档生成工具', enabled: false },
          { name: '性勒索邮件生成工具', enabled: false },
          { name: '亲和聊天脚本工具', enabled: false },
          { name: '虚假Offer邮件生成工具', enabled: false }
        ]
      }
    ]
  },
  {
    name: '防御 Agent',
    children: [
      {
        name: '漏洞修复 Agent',
        children: [
          {
            name: '修复服务',
            children: [
              { name: '漏洞扫描工具', enabled: true },
              { name: '自动打补丁工具', enabled: true },
              { name: '修改配置文件工具', enabled: true },
              { name: '重启服务工具', enabled: false }
            ]
          }
        ]
      },
      {
        name: '威胁阻断 Agent',
        children: [
          {
            name: '阻断服务',
            children: [
              { name: '防火墙阻断恶意流量工具', enabled: true },
              { name: '隔离受害主机工具', enabled: true },
              { name: '终止主机恶意进程工具', enabled: true },
              { name: '隔离恶意文件工具', enabled: false }
            ]
          }
        ]
      },
      {
        name: '攻击溯源 Agent',
        children: [
          {
            name: '溯源服务',
            children: [
              { name: 'ip威胁查询工具', enabled: true },
              { name: '哈希文件威胁查询工具', enabled: true },
              { name: '检测恶意通信和数据外传工具', enabled: true },
              { name: '检测恶意进程工具', enabled: true },
              { name: '检测恶意文件工具', enabled: true },
              { name: '检测恶意网络流量工具', enabled: true }
            ]
          }
        ]
      }
    ]
  },
  {
    name: '评估 Agent',
    children: [
      {
        name: '评估服务',
        children: [
              { name: '数据获取工具', enabled: true },
              { name: '场景拓扑获取工具', enabled: true },
              { name: '攻击量化指标计算工具', enabled: true },
              { name: '防御量化指标计算工具', enabled: true },
              { name: '报告生成工具', enabled: true },
              { name: '长期人员画像更新工具', enabled: true },
              { name: '长期攻击agent性能更新工具', enabled: true },
              { name: '长期防御agent性能更新工具', enabled: true }
        ]
      }
    ]
  }
])

// 切换 Tool 开关
function toggleTool (toolItem) {
  if (Object.prototype.hasOwnProperty.call(toolItem, 'enabled')) {
    toolItem.enabled = !toolItem.enabled
  }
}
</script>

<style scoped>
/* 背景星空特效 */
.settings-bg::before {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-radial-gradient(circle at 30% 40%, rgba(255,255,255,0.05) 0 1px, transparent 2px 100px),
              repeating-radial-gradient(circle at 70% 60%, rgba(255,255,255,0.04) 0 1px, transparent 2px 120px);
  animation: drift 60s linear infinite;
}
@keyframes drift {
  0% { transform: translateY(0); }
  100% { transform: translateY(-50%); }
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.animate-gradient {
  background-size: 200% 200%;
  animation: gradientShift 6s ease infinite;
}
</style> 