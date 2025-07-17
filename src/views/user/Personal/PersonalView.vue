<template>
  <div class="personal-view p-6 md:p-10 space-y-8">
    <!-- 个人信息卡片 -->
    <div class="bg-base-100 rounded-xl shadow-lg p-6">
      <div class="flex flex-col md:flex-row items-center md:items-start gap-6">
        <!-- 头像 -->
        <div class="avatar">
          <div
            class="w-24 h-24 rounded-full bg-gradient-to-r from-primary to-secondary flex items-center justify-center shadow-glow-sm">
            <span class="text-base-100 font-bold text-3xl">Z</span>
          </div>
        </div>

        <!-- 个人信息 -->
        <div class="flex-1 text-center md:text-left">
          <h1 class="text-2xl font-bold">张安全</h1>
          <p class="text-base-content/70 mt-1">安全工程师 | 中级认证</p>

          <div class="stats stats-vertical md:stats-horizontal shadow mt-4">
            <div class="stat">
              <div class="stat-title">参与演练</div>
              <div class="stat-value text-primary">28</div>
              <div class="stat-desc">次</div>
            </div>

            <div class="stat">
              <div class="stat-title">累计时长</div>
              <div class="stat-value text-secondary">156</div>
              <div class="stat-desc">小时</div>
            </div>

            <div class="stat">
              <div class="stat-title">技能评级</div>
              <div class="stat-value text-accent">B+</div>
              <div class="stat-desc">中高级</div>
            </div>
          </div>
        </div>

        <!-- 编辑按钮 -->
        <button class="btn btn-outline btn-sm">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24"
            stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
          </svg>
          编辑资料
        </button>
      </div>

      <!-- 技能标签 -->
      <div class="mt-6">
        <h3 class="text-sm font-medium text-base-content/70 mb-2">技能标签</h3>
        <div class="flex flex-wrap gap-2">
          <span class="badge badge-primary">Web安全</span>
          <span class="badge badge-secondary">网络安全</span>
          <span class="badge badge-accent">应急响应</span>
          <span class="badge">漏洞挖掘</span>
          <span class="badge">安全开发</span>
          <span class="badge">渗透测试</span>
          <span class="badge">安全运营</span>
        </div>
      </div>
    </div>

    <!-- 能力雷达图 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 红队能力雷达图 -->
      <div class="bg-base-100 rounded-xl shadow-lg p-6">
        <h2 class="text-xl font-bold mb-4 text-primary">红队能力画像</h2>
        <div class="h-80">
          <canvas id="redTeamRadarChart"></canvas>
        </div>
      </div>

      <!-- 蓝队能力雷达图 -->
      <div class="bg-base-100 rounded-xl shadow-lg p-6">
        <h2 class="text-xl font-bold mb-4 text-secondary">蓝队能力画像</h2>
        <div class="h-80">
          <canvas id="blueTeamRadarChart"></canvas>
        </div>
      </div>
    </div>

    <!-- 详细能力指标 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 蓝队详细指标 -->
      <div class="bg-base-100 rounded-xl shadow-lg p-6">
        <h2 class="text-xl font-bold mb-4 text-secondary">蓝队能力详情</h2>
        <div class="space-y-4">
          <div v-for="(item, index) in blueTeamMetrics" :key="index">
            <div class="flex justify-between items-center mb-1">
              <span class="text-sm">{{ item.label }}</span>
              <span class="text-sm font-medium">{{ item.value }}%</span>
            </div>
            <div class="w-full bg-base-300 rounded-full h-2">
              <div class="bg-secondary h-2 rounded-full" :style="`width: ${item.value}%`"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 红队详细指标 -->
      <div class="bg-base-100 rounded-xl shadow-lg p-6">
        <h2 class="text-xl font-bold mb-4 text-primary">红队能力详情</h2>
        <div class="space-y-4">
          <div v-for="(item, index) in redTeamMetrics" :key="index">
            <div class="flex justify-between items-center mb-1">
              <span class="text-sm">{{ item.label }}</span>
              <span class="text-sm font-medium">{{ item.value }}%</span>
            </div>
            <div class="w-full bg-base-300 rounded-full h-2">
              <div class="bg-primary h-2 rounded-full" :style="`width: ${item.value}%`"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 能力提升建议 -->
    <div class="bg-base-100 rounded-xl shadow-lg p-6">
      <h2 class="text-xl font-bold mb-4">能力提升建议</h2>

      <div class="tabs tabs-boxed mb-4">
        <a class="tab" :class="{ 'tab-active': activeTab === 'blue' }" @click="activeTab = 'blue'">蓝队能力提升</a>
        <a class="tab" :class="{ 'tab-active': activeTab === 'red' }" @click="activeTab = 'red'">红队能力提升</a>
      </div>

      <!-- 蓝队提升建议 -->
      <div v-if="activeTab === 'blue'" class="space-y-4">
        <div class="alert alert-info">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
            class="stroke-current shrink-0 w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <span>根据您的蓝队能力画像，我们为您提供以下提升建议</span>
        </div>

        <div class="card bg-base-200">
          <div class="card-body">
            <h3 class="card-title text-secondary">优势能力</h3>
            <p>您在<span class="font-medium">事件检测能力</span>和<span
                class="font-medium">防御知识覆盖能力</span>方面表现出色，建议继续保持并深入学习高级检测技术。</p>
          </div>
        </div>

        <div class="card bg-base-200">
          <div class="card-body">
            <h3 class="card-title text-warning">待提升能力</h3>
            <p>您的<span class="font-medium">反制能力</span>和<span class="font-medium">防御工具使用熟练度</span>相对较弱，建议：</p>
            <ul class="list-disc list-inside space-y-1 text-base-content/80">
              <li>参加更多反制技术的实战演练，提升对攻击者的主动防御能力</li>
              <li>系统学习SIEM、EDR等防御工具的高级功能，提高工具使用效率</li>
              <li>尝试构建自动化防御流程，减少手动操作带来的延迟</li>
            </ul>
          </div>
        </div>

        <div class="card bg-base-200">
          <div class="card-body">
            <h3 class="card-title text-info">推荐学习路径</h3>
            <div class="overflow-x-auto">
              <table class="table table-zebra w-full">
                <thead>
                  <tr>
                    <th>课程/实验</th>
                    <th>难度</th>
                    <th>预计提升</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>高级蜜罐部署与攻击者行为分析</td>
                    <td>中级</td>
                    <td>反制能力 +15%</td>
                  </tr>
                  <tr>
                    <td>SIEM系统高级配置与告警优化</td>
                    <td>中高级</td>
                    <td>工具使用熟练度 +20%</td>
                  </tr>
                  <tr>
                    <td>自动化响应流程构建实战</td>
                    <td>高级</td>
                    <td>事件响应能力 +12%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- 红队提升建议 -->
      <div v-if="activeTab === 'red'" class="space-y-4">
        <div class="alert alert-info">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
            class="stroke-current shrink-0 w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <span>根据您的红队能力画像，我们为您提供以下提升建议</span>
        </div>

        <div class="card bg-base-200">
          <div class="card-body">
            <h3 class="card-title text-primary">优势能力</h3>
            <p>您在<span class="font-medium">漏洞利用与攻击执行能力</span>和<span
                class="font-medium">攻击知识覆盖能力</span>方面表现出色，这为您的红队工作奠定了良好基础。</p>
          </div>
        </div>

        <div class="card bg-base-200">
          <div class="card-body">
            <h3 class="card-title text-warning">待提升能力</h3>
            <p>您的<span class="font-medium">隐蔽性与对抗规避能力</span>和<span class="font-medium">攻击链完整性</span>相对较弱，建议：</p>
            <ul class="list-disc list-inside space-y-1 text-base-content/80">
              <li>学习更多反检测和反取证技术，提高攻击隐蔽性</li>
              <li>系统学习完整的ATT&CK攻击链模型，提升攻击的系统性和完整性</li>
              <li>参加更多实战红队演练，锻炼在真实环境中的攻击能力</li>
            </ul>
          </div>
        </div>

        <div class="card bg-base-200">
          <div class="card-body">
            <h3 class="card-title text-info">推荐学习路径</h3>
            <div class="overflow-x-auto">
              <table class="table table-zebra w-full">
                <thead>
                  <tr>
                    <th>课程/实验</th>
                    <th>难度</th>
                    <th>预计提升</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>高级内存规避技术与反检测方法</td>
                    <td>高级</td>
                    <td>隐蔽性与对抗规避能力 +18%</td>
                  </tr>
                  <tr>
                    <td>ATT&CK框架实战应用</td>
                    <td>中高级</td>
                    <td>攻击链完整性 +15%</td>
                  </tr>
                  <tr>
                    <td>红队自动化工具开发</td>
                    <td>高级</td>
                    <td>攻击工具使用熟练度 +20%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 最近参与的演练 -->
    <div class="bg-base-100 rounded-xl shadow-lg p-6">
      <h2 class="text-xl font-bold mb-4">最近参与的演练</h2>
      <div class="overflow-x-auto">
        <table class="table w-full">
          <thead>
            <tr>
              <th>演练名称</th>
              <th>角色</th>
              <th>日期</th>
              <th>表现评级</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(exercise, index) in recentExercises" :key="index">
              <td>{{ exercise.name }}</td>
              <td>
                <span :class="exercise.role === '红队' ? 'text-primary' : 'text-secondary'">{{ exercise.role }}</span>
              </td>
              <td>{{ exercise.date }}</td>
              <td>
                <div class="rating rating-sm">
                  <input type="radio" name="rating-1" class="mask mask-star-2 bg-orange-400"
                    :checked="exercise.rating >= 1" disabled />
                  <input type="radio" name="rating-1" class="mask mask-star-2 bg-orange-400"
                    :checked="exercise.rating >= 2" disabled />
                  <input type="radio" name="rating-1" class="mask mask-star-2 bg-orange-400"
                    :checked="exercise.rating >= 3" disabled />
                  <input type="radio" name="rating-1" class="mask mask-star-2 bg-orange-400"
                    :checked="exercise.rating >= 4" disabled />
                  <input type="radio" name="rating-1" class="mask mask-star-2 bg-orange-400"
                    :checked="exercise.rating >= 5" disabled />
                </div>
              </td>
              <td>
                <button class="btn btn-xs btn-outline">查看详情</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Chart from 'chart.js/auto';

// 选项卡状态
const activeTab = ref('blue');

// 蓝队能力指标
const blueTeamMetrics = [
  { label: '攻击预防能力', value: 78 },
  { label: '防御加固能力', value: 82 },
  { label: '反制能力', value: 65 },
  { label: '事件检测能力', value: 88 },
  { label: '事件响应能力', value: 75 },
  { label: '防御知识覆盖能力', value: 85 },
  { label: '防御工具使用熟练度', value: 68 },
  { label: '防御成功率', value: 80 }
];

// 红队能力指标
const redTeamMetrics = [
  { label: '漏洞利用与攻击执行能力', value: 86 },
  { label: '横向移动与权限提升能力', value: 75 },
  { label: '隐蔽性与对抗规避能力', value: 62 },
  { label: '攻击链完整性与任务完成度', value: 68 },
  { label: '攻击知识覆盖能力', value: 84 },
  { label: '攻击工具使用熟练度', value: 79 },
  { label: '攻击成功率', value: 72 }
];

// 最近参与的演练
const recentExercises = [
  { name: '企业内网渗透与防御演练', role: '蓝队', date: '2025-07-10', rating: 4 },
  { name: 'Web应用安全攻防实战', role: '红队', date: '2025-06-28', rating: 5 },
  { name: '勒索软件攻击应急响应', role: '蓝队', date: '2025-06-15', rating: 3 },
  { name: '供应链攻击渗透测试', role: '红队', date: '2025-05-22', rating: 4 }
];

// 初始化图表
onMounted(() => {
  // 设置Chart.js全局配置
  Chart.defaults.font.family = "'Inter', 'Helvetica', 'Arial', sans-serif";
  Chart.defaults.color = '#a3a3a3';

  // 红队雷达图
  new Chart(document.getElementById('redTeamRadarChart'), {
    type: 'radar',
    data: {
      labels: redTeamMetrics.map(item => item.label),
      datasets: [{
        label: '能力水平',
        data: redTeamMetrics.map(item => item.value),
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        borderColor: 'rgba(255, 99, 132, 0.8)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(255, 99, 132, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(255, 99, 132, 1)',
        pointRadius: 4,
        pointHoverRadius: 6,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          beginAtZero: true,
          max: 100,
          ticks: {
            stepSize: 20,
            backdropColor: 'transparent',
            z: 100
          },
          grid: {
            color: 'rgba(255, 255, 255, 0.1)'
          },
          angleLines: {
            color: 'rgba(255, 255, 255, 0.1)'
          },
          pointLabels: {
            font: {
              size: 11
            },
            color: '#e2e8f0'
          }
        }
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          titleFont: {
            size: 13
          },
          bodyFont: {
            size: 12
          },
          callbacks: {
            label: function (context) {
              return `${context.label}: ${context.raw}%`;
            }
          }
        }
      }
    }
  });

  // 蓝队雷达图
  new Chart(document.getElementById('blueTeamRadarChart'), {
    type: 'radar',
    data: {
      labels: blueTeamMetrics.map(item => item.label),
      datasets: [{
        label: '能力水平',
        data: blueTeamMetrics.map(item => item.value),
        backgroundColor: 'rgba(99, 179, 237, 0.2)',
        borderColor: 'rgba(99, 179, 237, 0.8)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(99, 179, 237, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(99, 179, 237, 1)',
        pointRadius: 4,
        pointHoverRadius: 6,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          beginAtZero: true,
          max: 100,
          ticks: {
            stepSize: 20,
            backdropColor: 'transparent',
            z: 100
          },
          grid: {
            color: 'rgba(255, 255, 255, 0.1)'
          },
          angleLines: {
            color: 'rgba(255, 255, 255, 0.1)'
          },
          pointLabels: {
            font: {
              size: 11
            },
            color: '#e2e8f0'
          }
        }
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          titleFont: {
            size: 13
          },
          bodyFont: {
            size: 12
          },
          callbacks: {
            label: function (context) {
              return `${context.label}: ${context.raw}%`;
            }
          }
        }
      }
    }
  });
});
</script>

<style scoped>
.shadow-glow-sm {
  box-shadow: 0 0 10px rgba(var(--primary-rgb), 0.5);
}
</style>