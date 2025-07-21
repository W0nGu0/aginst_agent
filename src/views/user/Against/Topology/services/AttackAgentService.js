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
      const requestData = {
        target_host: "http://127.0.0.1:8005", // 目标主机URL
        attack_type: "auto" // 攻击类型，让中控智能体决定具体使用哪种攻击
      }
      
      console.log('发送攻击请求到中控智能体:', requestData)
      
      // 发送请求到中控智能体
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
      const requestData = {
        victim_url: "http://127.0.0.1:8005", // 目标主机URL
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