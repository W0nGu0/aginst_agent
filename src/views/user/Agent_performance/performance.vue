<template>
  <div class="min-h-screen bg-base-200 text-base-content">
    <!-- 页面标题 -->
    <header class="py-6 px-4 sm:px-6 lg:px-8 bg-base-100 shadow-md">
      <div class="container mx-auto">
        <h1
          class="text-3xl md:text-4xl font-bold text-left bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent text-gradient animate-gradient leading-snug"
        >
          Agent 性能概览
        </h1>
        <p class="text-left text-base-content/70 mt-2">
          实时监控攻击与防御Agent的决策有效性及系统稳定性指标
        </p>
      </div>
    </header>

    <main class="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 攻击与防御Agent指标区域 -->
      <section class="mb-12">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- 攻击Agent指标 -->
          <div
            class="bg-base-100 rounded-xl shadow-lg p-6 transform transition-all hover:shadow-xl"
          >
            <div class="flex items-center mb-6">
              <div
                class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center mr-3"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-6 w-6 text-primary"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 19l-7-7 7-7"
                  />
                </svg>
              </div>
              <h2 class="text-2xl font-bold text-base-content">
                攻击Agent性能指标
              </h2>
            </div>

            <!-- 决策成功率 -->
            <div class="mb-8">
              <h3 class="text-lg font-semibold mb-3 text-base-content/80">
                决策成功率
              </h3>
              <div class="h-64">
                <canvas id="attackSuccessRateChart"></canvas>
              </div>
            </div>

            <!-- 攻击类型分布 -->
            <div>
              <h3 class="text-lg font-semibold mb-3 text-base-content/80">
                攻击类型分布
              </h3>
              <div class="h-64">
                <canvas id="attackTypeChart"></canvas>
              </div>
            </div>
          </div>

          <!-- 防御Agent指标 -->
          <div
            class="bg-base-100 rounded-xl shadow-lg p-6 transform transition-all hover:shadow-xl"
          >
            <div class="flex items-center mb-6">
              <div
                class="w-10 h-10 rounded-full bg-secondary/10 flex items-center justify-center mr-3"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-6 w-6 text-secondary"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <h2 class="text-2xl font-bold text-base-content">
                防御Agent性能指标
              </h2>
            </div>

            <!-- 防御成功率 -->
            <div class="mb-8">
              <h3 class="text-lg font-semibold mb-3 text-base-content/80">
                防御成功率
              </h3>
              <div class="h-64">
                <canvas id="defenseSuccessRateChart"></canvas>
              </div>
            </div>

            <!-- 威胁检测时间 -->
            <div>
              <h3 class="text-lg font-semibold mb-3 text-base-content/80">
                威胁检测响应时间 (ms)
              </h3>
              <div class="h-64">
                <canvas id="detectionTimeChart"></canvas>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 系统稳定性指标区域 -->
      <section class="bg-base-100 rounded-xl shadow-lg p-6">
        <h2 class="text-2xl font-bold mb-6 flex items-center text-base-content">
          <div
            class="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center mr-3"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6 text-accent"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
              />
            </svg>
          </div>
          系统稳定性指标
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <!-- CPU使用率 -->
          <div class="bg-base-300/50 rounded-lg p-4">
            <h3 class="text-lg font-semibold mb-2 text-base-content/80">
              CPU使用率
            </h3>
            <div class="h-48">
              <canvas id="cpuUsageChart"></canvas>
            </div>
          </div>

          <!-- 内存使用率 -->
          <div class="bg-base-300/50 rounded-lg p-4">
            <h3 class="text-lg font-semibold mb-2 text-base-content/80">
              内存使用率
            </h3>
            <div class="h-48">
              <canvas id="memoryUsageChart"></canvas>
            </div>
          </div>

          <!-- 系统负载 -->
          <div class="bg-base-300/50 rounded-lg p-4">
            <h3 class="text-lg font-semibold mb-2 text-base-content/80">
              系统负载
            </h3>
            <div class="h-48">
              <canvas id="systemLoadChart"></canvas>
            </div>
          </div>
        </div>

        <!-- 系统状态卡片 -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="bg-primary/10 border border-primary/20 rounded-lg p-4">
            <h4 class="text-sm font-medium text-base-content/60">
              系统正常运行时间
            </h4>
            <p class="text-2xl font-bold mt-1 text-primary">24.5 小时</p>
            <p class="text-xs text-base-content/60 mt-1">↑ 2.3% 较昨日</p>
          </div>

          <div
            class="bg-secondary/10 border border-secondary/20 rounded-lg p-4"
          >
            <h4 class="text-sm font-medium text-base-content/60">
              活跃Agent数量
            </h4>
            <p class="text-2xl font-bold mt-1 text-secondary">7 个</p>
            <p class="text-xs text-base-content/60 mt-1">所有Agent正常运行</p>
          </div>

          <div class="bg-accent/10 border border-accent/20 rounded-lg p-4">
            <h4 class="text-sm font-medium text-base-content/60">
              平均响应时间
            </h4>
            <p class="text-2xl font-bold mt-1 text-accent">187 ms</p>
            <p class="text-xs text-base-content/60 mt-1">↑ 5.2% 较昨日</p>
          </div>

          <div class="bg-primary/10 border border-primary/20 rounded-lg p-4">
            <h4 class="text-sm font-medium text-base-content/60">任务完成率</h4>
            <p class="text-2xl font-bold mt-1 text-primary">98.7%</p>
            <p class="text-xs text-base-content/60 mt-1">↑ 1.2% 较昨日</p>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { onMounted } from "vue";
import Chart from "chart.js/auto";

// 模拟数据 - 攻击Agent
const attackSuccessRateData = {
  labels: [
    "SQL注入",
    "XSS攻击",
    "DDoS攻击",
    "社会工程学",
    "零日漏洞",
    "APT攻击",
  ],
  datasets: [
    {
      label: "攻击成功率",
      data: [85, 78, 92, 65, 88, 45],
      backgroundColor: "rgba(192, 38, 211, 0.6)",
      borderColor: "rgb(192, 38, 211)",
      borderWidth: 1,
    },
  ],
};

const attackTypeData = {
  labels: ["SQL注入", "XSS攻击", "DDoS攻击", "社会工程攻击", "APT攻击", "其他"],
  datasets: [
    {
      label: "攻击次数分布",
      data: [35, 25, 20, 10, 7, 3],
      backgroundColor: [
        "rgba(239, 68, 68, 0.7)",
        "rgba(249, 115, 22, 0.7)",
        "rgba(234, 179, 8, 0.7)",
        "rgba(52, 211, 153, 0.7)",
        "rgba(16, 185, 129, 0.7)",
        "rgba(107, 114, 128, 0.7)",
      ],
      borderWidth: 1,
    },
  ],
};

// 模拟数据 - 防御Agent
const defenseSuccessRateData = {
  labels: [
    "SQL注入",
    "XSS攻击",
    "DDoS攻击",
    "社会工程学",
    "零日漏洞",
    "APT攻击",
  ],
  datasets: [
    {
      label: "防御成功率",
      data: [92, 88, 75, 82, 95, 60],
      backgroundColor: "rgba(59, 130, 246, 0.6)",
      borderColor: "rgb(59, 130, 246)",
      borderWidth: 1,
    },
  ],
};

const detectionTimeData = {
  labels: ["0-50ms", "51-100ms", "101-200ms", "201-500ms", "501ms以上"],
  datasets: [
    {
      label: "威胁检测响应时间分布",
      data: [30, 45, 15, 8, 2],
      backgroundColor: [
        "rgba(16, 185, 129, 0.7)",
        "rgba(52, 211, 153, 0.7)",
        "rgba(234, 179, 8, 0.7)",
        "rgba(249, 115, 22, 0.7)",
        "rgba(239, 68, 68, 0.7)",
      ],
      borderWidth: 1,
    },
  ],
};

// 模拟数据 - 系统稳定性
const cpuUsageData = {
  labels: Array.from({ length: 24 }, (_, i) => `${i}:00`),
  datasets: [
    {
      label: "CPU使用率 (%)",
      data: Array.from(
        { length: 24 },
        () => Math.floor(Math.random() * 40) + 20
      ),
      borderColor: "rgb(59, 130, 246)",
      backgroundColor: "rgba(59, 130, 246, 0.1)",
      tension: 0.4,
      fill: true,
    },
  ],
};

const memoryUsageData = {
  labels: Array.from({ length: 24 }, (_, i) => `${i}:00`),
  datasets: [
    {
      label: "内存使用率 (%)",
      data: Array.from(
        { length: 24 },
        () => Math.floor(Math.random() * 30) + 40
      ),
      borderColor: "rgb(139, 92, 246)",
      backgroundColor: "rgba(139, 92, 246, 0.1)",
      tension: 0.4,
      fill: true,
    },
  ],
};

const systemLoadData = {
  labels: ["低", "中", "高", "极高"],
  datasets: [
    {
      label: "系统负载分布",
      data: [65, 25, 8, 2],
      backgroundColor: [
        "rgba(16, 185, 129, 0.7)",
        "rgba(52, 211, 153, 0.7)",
        "rgba(234, 179, 8, 0.7)",
        "rgba(239, 68, 68, 0.7)",
      ],
      borderWidth: 1,
    },
  ],
};

// 初始化图表
onMounted(() => {
  // 攻击Agent图表
  new Chart(document.getElementById("attackSuccessRateChart"), {
    type: "bar",
    data: attackSuccessRateData,
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: {
            callback: function (value) {
              return value + "%";
            },
          },
        },
      },
    },
  });

  new Chart(document.getElementById("attackTypeChart"), {
    type: "doughnut",
    data: attackTypeData,
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "right",
        },
      },
    },
  });

  // 防御Agent图表
  new Chart(document.getElementById("defenseSuccessRateChart"), {
    type: "bar",
    data: defenseSuccessRateData,
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: {
            callback: function (value) {
              return value + "%";
            },
          },
        },
      },
    },
  });

  new Chart(document.getElementById("detectionTimeChart"), {
    type: "doughnut",
    data: detectionTimeData,
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "right",
        },
      },
    },
  });

  // 系统稳定性图表
  new Chart(document.getElementById("cpuUsageChart"), {
    type: "line",
    data: cpuUsageData,
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: {
            callback: function (value) {
              return value + "%";
            },
          },
        },
      },
    },
  });

  new Chart(document.getElementById("memoryUsageChart"), {
    type: "line",
    data: memoryUsageData,
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: {
            callback: function (value) {
              return value + "%";
            },
          },
        },
      },
    },
  });

  new Chart(document.getElementById("systemLoadChart"), {
    type: "pie",
    data: systemLoadData,
    options: {
      responsive: true,
    },
  });
});
</script>
<style scoped>
@keyframes gradientShift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.animate-gradient {
  background-size: 200% 200%;
  animation: gradientShift 8s ease infinite;
}

.text-gradient {
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
}
</style>
