/**
 * 拓扑服务类
 * 负责与后端交互，管理拓扑图的创建、保存和加载
 */
class TopologyService {
  /**
   * 启动预设拓扑
   * @param {string} templateName - 模板名称，如 'company-topology'
   * @returns {Promise} - 返回包含容器信息的Promise
   */
  static async startTopology(templateName) {
    try {
      // 设置超时控制
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000); // 120秒超时，容器启动可能需要较长时间

      console.log('开始发送请求到后端...');

      // 向后端请求启动预设的 docker-compose 文件
      const resp = await fetch('/api/topology', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          action: 'start',
          template: templateName // 指定使用哪个预设模板
        }),
        signal: controller.signal
      });

      clearTimeout(timeoutId); // 清除超时

      console.log('请求已发送，状态码:', resp.status);

      if (!resp.ok) {
        const errorText = await resp.text();
        console.error('请求失败:', resp.status, resp.statusText, errorText);
        throw new Error(`请求失败: ${resp.status} ${resp.statusText}`);
      }

      const data = await resp.json();
      console.log('后端返回的容器信息', data);
      
      return data;
    } catch (error) {
      console.error('启动拓扑失败:', error);
      
      // 如果是超时错误，尝试获取当前容器状态
      if (error.name === 'AbortError') {
        console.log('请求超时，尝试获取当前容器状态...');
        return this.getTopologyStatus('company-topology');
      }
      
      throw error;
    }
  }

  /**
   * 启动动态生成的拓扑
   * @param {Object} scenarioConfig - 动态生成的场景配置
   * @returns {Promise} - 返回包含容器信息的Promise
   */
  static async startDynamicTopology(scenarioConfig) {
    try {
      // 设置超时控制
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 180000); // 3分钟超时

      console.log('开始发送动态拓扑请求到后端...');
      console.log('场景配置:', scenarioConfig);

      // 向后端请求启动动态生成的 docker-compose 配置
      const resp = await fetch('/api/topology/dynamic', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          action: 'start',
          config: scenarioConfig
        }),
        signal: controller.signal
      });

      clearTimeout(timeoutId); // 清除超时

      console.log('动态拓扑请求已发送，状态码:', resp.status);

      if (!resp.ok) {
        const errorText = await resp.text();
        console.error('动态拓扑请求失败:', resp.status, resp.statusText, errorText);
        throw new Error(`动态拓扑请求失败: ${resp.status} ${resp.statusText}`);
      }

      const data = await resp.json();
      console.log('后端返回的动态容器信息', data);

      return data;
    } catch (error) {
      console.error('启动动态拓扑失败:', error);

      // 如果是超时错误，提供友好的错误信息
      if (error.name === 'AbortError') {
        throw new Error('容器启动超时，请检查Docker服务状态');
      }

      throw error;
    }
  }

  /**
   * 停止拓扑
   * @returns {Promise} - 返回操作结果的Promise
   */
  static async stopTopology() {
    try {
      // 设置超时控制
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 60秒超时

      // 发送请求销毁容器
      const response = await fetch('/api/topology', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'stop' }),
        signal: controller.signal
      });

      clearTimeout(timeoutId); // 清除超时

      if (!response.ok) {
        throw new Error(`销毁场景失败: ${response.status} ${response.statusText}`);
      }

      console.log('场景销毁成功');
      return { success: true };
    } catch (error) {
      console.error('销毁场景失败', error);
      throw error;
    }
  }

  /**
   * 部署场景容器（通过场景智能体）
   * @param {Object} topologyData - 拓扑数据
   * @returns {Promise} - 返回包含容器信息的Promise
   */
  static async deployScenarioContainers(topologyData) {
    try {
      // 设置超时控制
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 300000); // 5分钟超时

      console.log('开始发送场景部署请求到后端...');
      console.log('拓扑数据:', topologyData);

      // 向后端请求部署场景容器
      const resp = await fetch('/api/scenario/deploy_containers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          topology_data: topologyData
        }),
        signal: controller.signal
      });

      clearTimeout(timeoutId); // 清除超时

      console.log('场景部署请求已发送，状态码:', resp.status);

      if (!resp.ok) {
        const errorText = await resp.text();
        console.error('场景部署请求失败:', resp.status, resp.statusText, errorText);
        throw new Error(`场景部署请求失败: ${resp.status} ${resp.statusText} - ${errorText}`);
      }

      const data = await resp.json();
      console.log('后端返回的容器部署信息', data);

      return data;
    } catch (error) {
      console.error('部署场景容器失败:', error);

      // 如果是超时错误，提供友好的错误信息
      if (error.name === 'AbortError') {
        throw new Error('容器部署超时，请检查场景智能体服务状态');
      }

      throw error;
    }
  }

  /**
   * 部署apt-ready场景容器
   * @returns {Promise} - 返回包含容器信息的Promise
   */
  static async deployAptReadyScenario() {
    try {
      // 设置超时控制
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 300000); // 5分钟超时

      console.log('开始部署apt-ready场景容器...');

      // 向后端请求启动apt-ready场景
      const resp = await fetch('/api/scenario/deploy_apt_ready', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({}),
        signal: controller.signal
      });

      clearTimeout(timeoutId); // 清除超时

      console.log('apt-ready场景部署请求已发送，状态码:', resp.status);

      if (!resp.ok) {
        const errorText = await resp.text();
        console.error('apt-ready场景部署请求失败:', resp.status, resp.statusText, errorText);
        throw new Error(`apt-ready场景部署请求失败: ${resp.status} ${resp.statusText} - ${errorText}`);
      }

      const data = await resp.json();
      console.log('后端返回的apt-ready容器部署信息', data);

      return data;
    } catch (error) {
      console.error('部署apt-ready场景容器失败:', error);

      // 如果是超时错误，提供友好的错误信息
      if (error.name === 'AbortError') {
        throw new Error('apt-ready容器部署超时，请检查场景智能体服务状态');
      }

      throw error;
    }
  }

  /**
   * 获取拓扑状态
   * @param {string} templateName - 模板名称
   * @returns {Promise} - 返回包含容器状态的Promise
   */
  static async getTopologyStatus(templateName) {
    try {
      const statusResp = await fetch('/api/topology', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'status',
          template: templateName
        })
      });

      if (!statusResp.ok) {
        throw new Error(`获取状态失败: ${statusResp.status} ${statusResp.statusText}`);
      }

      const statusData = await statusResp.json();
      console.log('获取到容器状态:', statusData);
      return statusData;
    } catch (error) {
      console.error('获取容器状态失败:', error);
      throw error;
    }
  }
}

export default TopologyService;