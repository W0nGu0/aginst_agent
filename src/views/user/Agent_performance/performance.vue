<template>
  <div class="min-h-screen bg-base-200 text-base-content">
    <!-- 页面标题 -->
    <header class="py-6 px-4 sm:px-6 lg:px-8 bg-base-100 shadow-md">
      <div class="container mx-auto">
        <h1
          class="text-3xl md:text-4xl font-bold text-left bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent text-gradient animate-gradient leading-snug">
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
          <div class="bg-base-100 rounded-xl shadow-lg p-6 transform transition-all hover:shadow-xl">
            <div class="flex items-center mb-6">
              <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center mr-3">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
              </div>
              <h2 class="text-2xl font-bold text-base-content">攻击Agent性能指标</h2>
            </div>
            <!-- 红方核心能力维度 -->
            <div class="mb-6">
              <h3 class="text-lg font-semibold mb-3 text-base-content/80">红方核心能力维度</h3>
              <!-- 红方能力维度选项卡 -->
              <div class="grid grid-cols-3 gap-2 mb-4">
                <a class="tab tab-lifted text-center bg-base-200 rounded-btn py-4 px-2 min-h-12 h-auto whitespace-normal break-words transition-all duration-300 ease-in-out transform hover:scale-105" :class="{ 'tab-active bg-blue-600 text-white scale-105': redActiveTab === 'A' }" @click="setRedActiveTab('A')">目标识别与情报收集</a>
                <a class="tab tab-lifted text-center bg-base-200 rounded-btn py-4 px-2 min-h-12 h-auto whitespace-normal break-words transition-all duration-300 ease-in-out transform hover:scale-105" :class="{ 'tab-active bg-blue-600 text-white scale-105': redActiveTab === 'B' }" @click="setRedActiveTab('B')">漏洞利用与攻击执行</a>
                <a class="tab tab-lifted text-center bg-base-200 rounded-btn py-4 px-2 min-h-12 h-auto whitespace-normal break-words transition-all duration-300 ease-in-out transform hover:scale-105" :class="{ 'tab-active bg-blue-600 text-white scale-105': redActiveTab === 'C' }" @click="setRedActiveTab('C')">横向移动与权限提升</a>
              </div>
              <div class="flex justify-center gap-2 mb-4">
                <a class="tab tab-lifted text-center bg-base-200 rounded-btn py-4 px-2 min-h-12 h-auto whitespace-normal break-words w-2/5 transition-all duration-300 ease-in-out transform hover:scale-105" :class="{ 'tab-active bg-blue-600 text-white scale-105': redActiveTab === 'D' }" @click="setRedActiveTab('D')">攻击链完整性与任务完成度</a>
                <a class="tab tab-lifted text-center bg-base-200 rounded-btn py-4 px-2 min-h-12 h-auto whitespace-normal break-words w-2/5 transition-all duration-300 ease-in-out transform hover:scale-105" :class="{ 'tab-active bg-blue-600 text-white scale-105': redActiveTab === 'E' }" @click="setRedActiveTab('E')">智能决策与策略演化</a>
              </div>
              <!-- 目标识别与情报收集能力（A） -->
              <div v-show="redActiveTab === 'A'" class="mt-4 transition-all duration-300 ease-in-out">
                <div class="grid grid-cols-1 gap-4">
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">A1：资产探测成功率</span>
                      <span class="text-lg font-bold text-primary">92%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-primary h-2.5 rounded-full" style="width: 92%"></div>
                    </div>
                  </div>
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">A2：端口/服务识别准确率</span>
                      <span class="text-lg font-bold text-primary">88%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-primary h-2.5 rounded-full" style="width: 88%"></div>
                    </div>
                  </div>
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">A3：漏洞指纹识别广度</span>
                      <span class="text-lg font-bold text-primary">85%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-primary h-2.5 rounded-full" style="width: 85%"></div>
                    </div>
                  </div>
                </div>
                
                <!-- 总体评分 -->
                <div class="bg-primary/10 border border-primary/20 rounded-lg p-4 mt-4">
                  <div class="flex justify-between items-center">
                    <h3 class="font-semibold text-base-content/90">目标识别与情报收集能力总评分</h3>
                    <div class="radial-progress text-primary" style="--value:88; --size:3rem;">88%</div>
                  </div>
                </div>
              </div>
              <!-- 漏洞利用与攻击执行能力（B） -->
              <div v-show="redActiveTab === 'B'" class="mt-4 transition-all duration-300 ease-in-out">
                <div class="grid grid-cols-1 gap-4">
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">B1：漏洞利用成功率</span>
                      <span class="text-lg font-bold text-primary">78%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-primary h-2.5 rounded-full" style="width: 78%"></div>
                    </div>
                  </div>
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">B2：漏洞利用自动化程度</span>
                      <span class="text-lg font-bold text-primary">85%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-primary h-2.5 rounded-full" style="width: 85%"></div>
                    </div>
                  </div>
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">B3：武器化工具多样性</span>
                      <span class="text-lg font-bold text-primary">90%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-primary h-2.5 rounded-full" style="width: 90%"></div>
                    </div>
                  </div>
                </div>
                
                <!-- 总体评分 -->
                <div class="bg-primary/10 border border-primary/20 rounded-lg p-4 mt-4">
                  <div class="flex justify-between items-center">
                    <h3 class="font-semibold text-base-content/90">漏洞利用与攻击执行能力总评分</h3>
                    <div class="radial-progress text-primary" style="--value:84; --size:3rem;">84%</div>
                  </div>
                </div>
              </div>
              <!-- 横向移动与权限提升能力（C） -->
              <div v-show="redActiveTab === 'C'" class="mt-4 transition-all duration-300 ease-in-out">
                <div class="grid grid-cols-1 gap-4">
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">C1：横向路径深度（跳数）</span>
                      <span class="text-lg font-bold text-primary">5.2</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-primary h-2.5 rounded-full" style="width: 85%"></div>
                    </div>
                  </div>
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">C2：提权成功率</span>
                      <span class="text-lg font-bold text-primary">72%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-primary h-2.5 rounded-full" style="width: 72%"></div>
                    </div>
                  </div>
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">C3：持久化机制多样性</span>
                      <span class="text-lg font-bold text-primary">80%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-primary h-2.5 rounded-full" style="width: 80%"></div>
                    </div>
                  </div>
                </div>
                
                <!-- 总体评分 -->
                <div class="bg-primary/10 border border-primary/20 rounded-lg p-4 mt-4">
                  <div class="flex justify-between items-center">
                    <h3 class="font-semibold text-base-content/90">横向移动与权限提升能力总评分</h3>
                    <div class="radial-progress text-primary" style="--value:79; --size:3rem;">79%</div>
                  </div>
                </div>
              </div>
              <!-- 攻击链完整性与任务完成度（D） -->
              <div v-show="redActiveTab === 'D'" class="mt-4 transition-all duration-300 ease-in-out">
                <div class="grid grid-cols-1 gap-4">
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">D1：攻击链完整度</span>
                      <span class="text-lg font-bold text-primary">85%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-primary h-2.5 rounded-full" style="width: 85%"></div>
                    </div>
                  </div>
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">D2：任务完成率</span>
                      <span class="text-lg font-bold text-primary">92%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-primary h-2.5 rounded-full" style="width: 92%"></div>
                    </div>
                  </div>
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">D3：目标达成度</span>
                      <span class="text-lg font-bold text-primary">78%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-primary h-2.5 rounded-full" style="width: 78%"></div>
                    </div>
                  </div>
                </div>
                
                <!-- 总体评分 -->
                <div class="bg-primary/10 border border-primary/20 rounded-lg p-4 mt-4">
                  <div class="flex justify-between items-center">
                    <h3 class="font-semibold text-base-content/90">攻击链完整性与任务完成度总评分</h3>
                    <div class="radial-progress text-primary" style="--value:81; --size:3rem;">81%</div>
                  </div>
                </div>
              </div>
              <!-- 智能决策与策略演化能力（E） -->
              <div v-show="redActiveTab === 'E'" class="mt-4 transition-all duration-300 ease-in-out">
                <div class="grid grid-cols-1 gap-4">
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">E1：决策响应时间</span>
                      <span class="text-lg font-bold text-primary">1.3s</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-primary h-2.5 rounded-full" style="width: 88%"></div>
                    </div>
                  </div>
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">E2：策略变化频次</span>
                      <span class="text-lg font-bold text-primary">中</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-primary h-2.5 rounded-full" style="width: 75%"></div>
                    </div>
                  </div>
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">E3：环境自适应性得分</span>
                      <span class="text-lg font-bold text-primary">86%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-primary h-2.5 rounded-full" style="width: 86%"></div>
                    </div>
                  </div>
                </div>
                
                <!-- 总体评分 -->
                <div class="bg-primary/10 border border-primary/20 rounded-lg p-4 mt-4">
                  <div class="flex justify-between items-center">
                    <h3 class="font-semibold text-base-content/90">智能决策与策略演化能力总评分</h3>
                    <div class="radial-progress text-primary" style="--value:83; --size:3rem;">83%</div>
                  </div>
                </div>
              </div>
            </div>
            <!-- 决策成功率 -->
            <div class="mb-8">
              <h3 class="text-lg font-semibold mb-3 text-base-content/80">决策成功率</h3>
              <div class="h-64 w-full"><canvas id="attackSuccessRateChart"></canvas></div>
            </div>
            <!-- 攻击类型分布 -->
            <div>
              <h3 class="text-lg font-semibold mb-3 text-base-content/80">攻击类型分布</h3>
              <div class="h-64 w-full"><canvas id="attackTypeChart"></canvas></div>
            </div>
          </div>
          
          <!-- 防御Agent指标 -->
          <div class="bg-base-100 rounded-xl shadow-lg p-6 transform transition-all hover:shadow-xl">
            <div class="flex items-center mb-6">
              <div class="w-10 h-10 rounded-full bg-secondary/10 flex items-center justify-center mr-3">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-secondary" fill="none" viewBox="0 0 24 24"
                  stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h2 class="text-2xl font-bold text-base-content">
                防御Agent性能指标
              </h2>
            </div>

            <!-- 蓝方核心能力维度 -->
            <div class="mb-6">
              <h3 class="text-lg font-semibold mb-3 text-base-content/80">
                蓝方核心能力维度
              </h3>
              <!-- 蓝方能力维度选项卡 -->
              <div class="grid grid-cols-3 gap-2 mb-4">
                <a class="tab tab-lifted text-center bg-base-200 rounded-btn py-4 px-2 min-h-12 h-auto whitespace-normal break-words transition-all duration-300 ease-in-out transform hover:scale-105" :class="{ 'tab-active bg-blue-600 text-white scale-105': blueActiveTab === 'F' }" @click="setBlueActiveTab('F')">攻击预防能力</a>
                <a class="tab tab-lifted text-center bg-base-200 rounded-btn py-4 px-2 min-h-12 h-auto whitespace-normal break-words transition-all duration-300 ease-in-out transform hover:scale-105" :class="{ 'tab-active bg-blue-600 text-white scale-105': blueActiveTab === 'G' }" @click="setBlueActiveTab('G')">防御加固能力</a>
                <a class="tab tab-lifted text-center bg-base-200 rounded-btn py-4 px-2 min-h-12 h-auto whitespace-normal break-words transition-all duration-300 ease-in-out transform hover:scale-105" :class="{ 'tab-active bg-blue-600 text-white scale-105': blueActiveTab === 'H' }" @click="setBlueActiveTab('H')">反制能力</a>
              </div>
              <div class="flex justify-center gap-2 mb-4">
                <a class="tab tab-lifted text-center bg-base-200 rounded-btn py-4 px-2 min-h-12 h-auto whitespace-normal break-words w-2/5 transition-all duration-300 ease-in-out transform hover:scale-105" :class="{ 'tab-active bg-blue-600 text-white scale-105': blueActiveTab === 'I' }" @click="setBlueActiveTab('I')">事件检测能力</a>
                <a class="tab tab-lifted text-center bg-base-200 rounded-btn py-4 px-2 min-h-12 h-auto whitespace-normal break-words w-2/5 transition-all duration-300 ease-in-out transform hover:scale-105" :class="{ 'tab-active bg-blue-600 text-white scale-105': blueActiveTab === 'J' }" @click="setBlueActiveTab('J')">事件响应能力</a>
              </div>

              <!-- 蓝方能力维度内容 -->
              <!-- 攻击预防能力（F） -->
              <div v-show="blueActiveTab === 'F'" class="mt-4 transition-all duration-300 ease-in-out">
                <div class="grid grid-cols-1 gap-4">
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">F1：漏洞预警能力</span>
                      <span class="text-lg font-bold text-secondary">85%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-secondary h-2.5 rounded-full" style="width: 85%"></div>
                    </div>
                  </div>
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">F2：漏洞评估能力</span>
                      <span class="text-lg font-bold text-secondary">92%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-secondary h-2.5 rounded-full" style="width: 92%"></div>
                    </div>
                  </div>
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">F3：漏洞修复能力</span>
                      <span class="text-lg font-bold text-secondary">78%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-secondary h-2.5 rounded-full" style="width: 78%"></div>
                    </div>
                  </div>
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">F4：威胁预警能力</span>
                      <span class="text-lg font-bold text-secondary">80%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-secondary h-2.5 rounded-full" style="width: 80%"></div>
                    </div>
                  </div>
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">F5：威胁评估能力</span>
                      <span class="text-lg font-bold text-secondary">88%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-secondary h-2.5 rounded-full" style="width: 88%"></div>
                    </div>
                  </div>
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">F6：威胁抵御能力</span>
                      <span class="text-lg font-bold text-secondary">75%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-secondary h-2.5 rounded-full" style="width: 75%"></div>
                    </div>
                  </div>
                </div>
                
                <!-- 总体评分 -->
                <div class="bg-secondary/10 border border-secondary/20 rounded-lg p-4 mt-4">
                  <div class="flex justify-between items-center">
                    <h3 class="font-semibold text-base-content/90">攻击预防能力总评分</h3>
                    <div class="radial-progress text-secondary" style="--value:83; --size:3rem;">83%</div>
                  </div>
                </div>
              </div>
              <!-- 防御加固能力（G） -->
              <div v-show="blueActiveTab === 'G'" class="mt-4 transition-all duration-300 ease-in-out">
                <div class="grid grid-cols-1 gap-4">
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">基础防护管理（安全功能+配置）</span>
                      <span class="text-lg font-bold text-secondary">87%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-secondary h-2.5 rounded-full" style="width: 87%"></div>
                    </div>
                  </div>
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">访问控制管理（身份+权限+域）</span>
                      <span class="text-lg font-bold text-secondary">89%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-secondary h-2.5 rounded-full" style="width: 89%"></div>
                    </div>
                  </div>
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">可持续保障能力（更新+备份）</span>
                      <span class="text-lg font-bold text-secondary">91%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-secondary h-2.5 rounded-full" style="width: 91%"></div>
                    </div>
                  </div>
                </div>
                
                <!-- 总体评分 -->
                <div class="bg-secondary/10 border border-secondary/20 rounded-lg p-4 mt-4">
                  <div class="flex justify-between items-center">
                    <h3 class="font-semibold text-base-content/90">防御加固能力总评分</h3>
                    <div class="radial-progress text-secondary" style="--value:89; --size:3rem;">89%</div>
                  </div>
                </div>
              </div>
              <!-- 反制能力（H） -->
              <div v-show="blueActiveTab === 'H'" class="mt-4 transition-all duration-300 ease-in-out">
                <div class="grid grid-cols-1 gap-4">
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">H1：威胁情报收集能力</span>
                      <span class="text-lg font-bold text-secondary">85%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-secondary h-2.5 rounded-full" style="width: 85%"></div>
                    </div>
                  </div>
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">H2：溯源分析能力</span>
                      <span class="text-lg font-bold text-secondary">78%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-secondary h-2.5 rounded-full" style="width: 78%"></div>
                    </div>
                  </div>
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">H3：反制策略多样性</span>
                      <span class="text-lg font-bold text-secondary">82%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-secondary h-2.5 rounded-full" style="width: 82%"></div>
                    </div>
                  </div>
                </div>
                
                <!-- 总体评分 -->
                <div class="bg-secondary/10 border border-secondary/20 rounded-lg p-4 mt-4">
                  <div class="flex justify-between items-center">
                    <h3 class="font-semibold text-base-content/90">反制能力总评分</h3>
                    <div class="radial-progress text-secondary" style="--value:81; --size:3rem;">81%</div>
                  </div>
                </div>
              </div>
              <!-- 事件检测能力（I） -->
              <div v-show="blueActiveTab === 'I'" class="mt-4 transition-all duration-300 ease-in-out">
                <div class="grid grid-cols-1 gap-4">
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">I1：威胁检测准确率</span>
                      <span class="text-lg font-bold text-secondary">88%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-secondary h-2.5 rounded-full" style="width: 88%"></div>
                    </div>
                  </div>
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">I2：误报率</span>
                      <span class="text-lg font-bold text-secondary">12%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-secondary h-2.5 rounded-full" style="width: 12%"></div>
                    </div>
                  </div>
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">I3：检测覆盖范围</span>
                      <span class="text-lg font-bold text-secondary">92%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-secondary h-2.5 rounded-full" style="width: 92%"></div>
                    </div>
                  </div>
                </div>
                
                <!-- 总体评分 -->
                <div class="bg-secondary/10 border border-secondary/20 rounded-lg p-4 mt-4">
                  <div class="flex justify-between items-center">
                    <h3 class="font-semibold text-base-content/90">事件检测能力总评分</h3>
                    <div class="radial-progress text-secondary" style="--value:87; --size:3rem;">87%</div>
                  </div>
                </div>
              </div>
              <!-- 事件响应能力（J） -->
              <div v-show="blueActiveTab === 'J'" class="mt-4 transition-all duration-300 ease-in-out">
                <div class="grid grid-cols-1 gap-4">
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">J1：响应时间</span>
                      <span class="text-lg font-bold text-secondary">2.1s</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-secondary h-2.5 rounded-full" style="width: 85%"></div>
                    </div>
                  </div>
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">J2：处置成功率</span>
                      <span class="text-lg font-bold text-secondary">92%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-secondary h-2.5 rounded-full" style="width: 92%"></div>
                    </div>
                  </div>
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">J3：恢复时间</span>
                      <span class="text-lg font-bold text-secondary">3.5s</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-secondary h-2.5 rounded-full" style="width: 88%"></div>
                    </div>
                  </div>
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">主机&终端</span>
                      <span class="text-lg font-bold text-secondary">88%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-secondary h-2.5 rounded-full" style="width: 88%"></div>
                    </div>
                  </div>
                  <div class="bg-base-300/30 rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                      <span class="font-medium">网络</span>
                      <span class="text-lg font-bold text-secondary">89%</span>
                    </div>
                    <div class="w-full bg-base-300 rounded-full h-2.5">
                      <div class="bg-secondary h-2.5 rounded-full" style="width: 89%"></div>
                    </div>
                  </div>
                </div>
                
                <!-- 总体评分 -->
                <div class="bg-secondary/10 border border-secondary/20 rounded-lg p-4 mt-4">
                  <div class="flex justify-between items-center">
                    <h3 class="font-semibold text-base-content/90">事件响应能力总评分</h3>
                    <div class="radial-progress text-secondary" style="--value:87; --size:3rem;">87%</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 防御成功率 -->
            <div class="mb-8">
              <h3 class="text-lg font-semibold mb-3 text-base-content/80">
                防御成功率
              </h3>
              <div class="h-64 w-full">
                <canvas id="defenseSuccessRateChart"></canvas>
              </div>
            </div>

            <!-- 威胁检测时间 -->
            <div>
              <h3 class="text-lg font-semibold mb-3 text-base-content/80">
                威胁检测响应时间 (ms)
              </h3>
              <div class="h-64 w-full">
                <canvas id="detectionTimeChart"></canvas>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 系统稳定性指标区域 -->
      <section class="bg-base-100 rounded-xl shadow-lg p-6">
        <h2 class="text-2xl font-bold mb-6 flex items-center text-base-content">
          <div class="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center mr-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-accent" fill="none" viewBox="0 0 24 24"
              stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
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
            <div class="h-48 w-full">
              <canvas id="cpuUsageChart"></canvas>
            </div>
          </div>

          <!-- 内存使用率 -->
          <div class="bg-base-300/50 rounded-lg p-4">
            <h3 class="text-lg font-semibold mb-2 text-base-content/80">
              内存使用率
            </h3>
            <div class="h-48 w-full">
              <canvas id="memoryUsageChart"></canvas>
            </div>
          </div>

          <!-- 系统负载 -->
          <div class="bg-base-300/50 rounded-lg p-4">
            <h3 class="text-lg font-semibold mb-2 text-base-content/80">
              系统负载
            </h3>
            <div class="h-48 w-full">
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

          <div class="bg-secondary/10 border border-secondary/20 rounded-lg p-4">
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
import { onMounted, ref } from "vue";
import Chart from "chart.js/auto";

// 红蓝方能力维度选项卡状态
const redActiveTab = ref('A');
const blueActiveTab = ref('F');

// 选项卡切换函数
const setRedActiveTab = (tab) => {
  redActiveTab.value = tab;
};

const setBlueActiveTab = (tab) => {
  blueActiveTab.value = tab;
};

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
      maintainAspectRatio: false,
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
      maintainAspectRatio: false,
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
      maintainAspectRatio: false,
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
      maintainAspectRatio: false,
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
      maintainAspectRatio: false,
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
      maintainAspectRatio: false,
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
      maintainAspectRatio: false,
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