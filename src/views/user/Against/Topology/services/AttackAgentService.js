/**
 * 攻击智能体服务
 * 提供与攻击智能体的交互功能
 */

// 模拟API调用延迟
const simulateDelay = (ms = 500) => new Promise(resolve => setTimeout(resolve, ms))

/**
 * 攻击智能体服务类
 */
class AttackAgentService {
  /**
   * 执行自动攻击
   * @param {Object} attackData - 攻击数据
   * @returns {Promise<Object>} - 返回攻击结果
   */
  static async executeAutoAttack(attackData) {
    try {
      console.log('开始执行自动攻击:', attackData)
      
      // 构建API请求URL
      const apiUrl = `/api/attack/execute_full_attack`
      
      // 构建请求数据
      // 根据攻击目标选择不同的主机URL
      let targetHost = "http://localhost:5001"; // 默认使用alice容器
      
      // 如果有目标设备，根据设备名称或IP选择不同的主机
      if (attackData.target) {
        const targetName = attackData.target.deviceData?.name || "";
        const targetIp = attackData.target.deviceData?.ip || "";
        
        if (targetName.includes("PC-1") || targetIp.includes("192.168.100.9")) {
          targetHost = "http://localhost:5001"; // alice
        } else if (targetName.includes("PC-2") || targetIp.includes("192.168.100.34")) {
          targetHost = "http://localhost:5002"; // bob
        }
      }
      
      console.log(`选择目标主机: ${targetHost}`);
      
      const requestData = {
        target_host: targetHost,
        attack_type: "auto" // 攻击类型，让中控智能体决定具体使用哪种攻击
      }
      
      console.log('发送攻击请求到中控智能体:', requestData)
      
      // 添加错误处理和超时设置
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30秒超时
      
      // 发送请求到中控智能体
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData),
        signal: controller.signal
      })
      
      clearTimeout(timeoutId); // 清除超时计时器
      
      // 检查响应状态
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`攻击智能体请求失败: ${response.status} ${errorText}`)
      }
      
      // 解析响应数据
      const result = await response.json()
      
      return {
        success: true,
        message: '自动攻击执行成功',
        details: result
      }
    } catch (error) {
      console.error('执行自动攻击失败:', error)
      return {
        success: false,
        message: `执行自动攻击失败: ${error.message}`,
        error
      }
    }
  }
  
  /**
   * 执行社会工程学攻击
   * @param {Object} attackData - 攻击数据
   * @returns {Promise<Object>} - 返回攻击结果
   */
  static async executeSocialEngineeringAttack(attackData) {
    try {
      console.log('开始执行社会工程学攻击:', attackData)
      
      // 构建API请求URL
      const apiUrl = `/api/attack/execute_random_social_attack`
      
      // 构建请求数据
      // 根据攻击目标选择不同的主机URL
      let targetHost = "http://localhost:5001"; // 默认使用alice容器
      
      // 如果有目标设备，根据设备名称或IP选择不同的主机
      if (attackData.target) {
        const targetName = attackData.target.deviceData?.name || "";
        const targetIp = attackData.target.deviceData?.ip || "";
        
        if (targetName.includes("PC-1") || targetIp.includes("192.168.100.9")) {
          targetHost = "http://localhost:5001"; // alice
        } else if (targetName.includes("PC-2") || targetIp.includes("192.168.100.34")) {
          targetHost = "http://localhost:5002"; // bob
        }
      }
      
      console.log(`选择社会工程学攻击目标主机: ${targetHost}`);
      
      // 构建请求数据
      const requestData = {
        victim_url: targetHost, // 目标主机URL
        victim_name: attackData.target?.deviceData?.name || "未知用户",
        company: "ACME_CORP" // 公司名称，实际环境中应该从配置或参数中获取
      }
      
      // 发送请求到攻击智能体
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      })
      
      // 检查响应状态
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`攻击智能体请求失败: ${response.status} ${errorText}`)
      }
      
      // 解析响应数据
      const result = await response.json()
      
      return {
        success: true,
        message: '社会工程学攻击执行成功',
        details: result
      }
    } catch (error) {
      console.error('执行社会工程学攻击失败:', error)
      return {
        success: false,
        message: `执行社会工程学攻击失败: ${error.message}`,
        error
      }
    }
  }
  
  /**
   * 获取攻击智能体状态
   * @returns {Promise<Object>} - 返回攻击智能体状态
   */
  static async getAgentStatus() {
    try {
      // 构建API请求URL
      const apiUrl = `/api/attack/status`
      
      // 发送请求到攻击智能体
      const response = await fetch(apiUrl)
      
      // 检查响应状态
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`获取攻击智能体状态失败: ${response.status} ${errorText}`)
      }
      
      // 解析响应数据
      const result = await response.json()
      
      return {
        success: true,
        status: result.status,
        details: result
      }
    } catch (error) {
      console.error('获取攻击智能体状态失败:', error)
      return {
        success: false,
        message: `获取攻击智能体状态失败: ${error.message}`,
        error
      }
    }
  }
}

export default AttackAgentService