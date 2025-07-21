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