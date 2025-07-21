/**
 * 钓鱼攻击服务
 * 提供钓鱼攻击相关的API调用和模拟功能
 */

// 模拟API调用延迟
const simulateDelay = (ms = 1000) => new Promise(resolve => setTimeout(resolve, ms))

/**
 * 钓鱼攻击服务类
 */
class PhishingService {
  /**
   * 模拟钓鱼攻击
   * @param {Object} attackData - 攻击数据
   * @returns {Promise<Object>} - 返回攻击结果
   */
  static async simulatePhishingAttack(attackData) {
    try {
      // 模拟API调用延迟
      await simulateDelay(2000)
      
      // 获取目标主机的详细信息
      const targetInfo = await this.getTargetInfo(attackData.target)
      
      // 根据目标信息生成定制化的钓鱼邮件
      const phishingEmail = await this.generatePhishingEmail(targetInfo, attackData.attackType)
      
      // 模拟发送钓鱼邮件
      const result = await this.sendPhishingEmail(targetInfo, phishingEmail)
      
      return {
        success: true,
        message: `成功对 ${targetInfo.name} 发起钓鱼攻击`,
        details: {
          targetInfo,
          phishingEmail,
          result
        }
      }
    } catch (error) {
      console.error('钓鱼攻击失败:', error)
      return {
        success: false,
        message: `钓鱼攻击失败: ${error.message}`,
        error
      }
    }
  }
  
  /**
   * 获取目标主机的详细信息
   * @param {Object} target - 目标主机
   * @returns {Promise<Object>} - 返回目标信息
   */
  static async getTargetInfo(target) {
    // 模拟API调用延迟
    await simulateDelay(500)
    
    // 从目标主机获取信息
    const { deviceData } = target
    
    // 根据主机名生成模拟数据
    let userInfo = {}
    
    if (deviceData.name.includes('PC')) {
      userInfo = {
        username: deviceData.name.includes('1') ? 'John Smith' : 'Alice Johnson',
        company: 'ACME Corp',
        department: '研发部',
        role: '软件工程师',
        email: deviceData.name.includes('1') ? 'john.smith@acmecorp.com' : 'alice.johnson@acmecorp.com',
        interests: ['技术', '编程', '云计算']
      }
    } else if (deviceData.name.includes('服务器')) {
      userInfo = {
        username: 'admin',
        company: 'ACME Corp',
        department: 'IT运维',
        role: '系统管理员',
        email: 'admin@acmecorp.com',
        interests: ['服务器管理', '网络安全', '自动化']
      }
    } else if (deviceData.name.includes('数据库')) {
      userInfo = {
        username: 'dbadmin',
        company: 'ACME Corp',
        department: '数据库管理',
        role: '数据库管理员',
        email: 'dbadmin@acmecorp.com',
        interests: ['数据库', 'SQL', '数据安全']
      }
    } else {
      userInfo = {
        username: 'user',
        company: 'ACME Corp',
        department: '未知',
        role: '未知',
        email: 'user@acmecorp.com',
        interests: ['一般业务']
      }
    }
    
    return {
      id: target.id,
      name: deviceData.name,
      ip: deviceData.ip,
      mac: deviceData.mac,
      type: deviceData.type,
      ...userInfo
    }
  }
  
  /**
   * 生成定制化的钓鱼邮件
   * @param {Object} targetInfo - 目标信息
   * @param {string} attackType - 攻击类型
   * @returns {Promise<Object>} - 返回钓鱼邮件内容
   */
  static async generatePhishingEmail(targetInfo, attackType) {
    // 模拟API调用延迟
    await simulateDelay(1000)
    
    // 根据攻击类型和目标信息生成不同的钓鱼邮件
    let subject, content, sender
    
    if (attackType === 'phishing') {
      // 密码重置钓鱼邮件
      sender = `IT部门 <it@${targetInfo.company.toLowerCase().replace(/\s+/g, '')}.com>`
      subject = `[紧急] ${targetInfo.company} 账户安全通知`
      content = `
<div style="font-family: Arial, sans-serif; color: #333;">
  <p>尊敬的 ${targetInfo.username}，</p>
  
  <p>我们的系统检测到您的账户存在异常登录活动。为了保障您的账户安全，请立即点击以下链接重置您的密码：</p>
  
  <p><a href="http://evil-phishing-site.com/reset?email=${targetInfo.email}" style="color: #1a73e8; text-decoration: underline;">https://${targetInfo.company.toLowerCase().replace(/\s+/g, '')}.com/account/security/reset</a></p>
  
  <p>如果您没有进行过可疑操作，请务必在24小时内完成密码重置，否则您的账户将被临时冻结。</p>
  
  <p>此致，<br>${targetInfo.company} IT安全团队</p>
</div>
      `
    } else if (attackType === 'social_engineering') {
      // 社会工程学攻击邮件
      const randomInterest = targetInfo.interests[Math.floor(Math.random() * targetInfo.interests.length)]
      sender = `${targetInfo.company} 人力资源部 <hr@${targetInfo.company.toLowerCase().replace(/\s+/g, '')}.com>`
      subject = `关于${randomInterest}的内部培训通知`
      content = `
<div style="font-family: Arial, sans-serif; color: #333;">
  <p>亲爱的 ${targetInfo.username}，</p>
  
  <p>根据公司的人才发展计划，我们注意到您对${randomInterest}领域有浓厚的兴趣。</p>
  
  <p>我们将于下周举办一场关于${randomInterest}的内部培训，由行业顶尖专家主讲。由于名额有限，请点击以下链接确认您的参与：</p>
  
  <p><a href="http://evil-phishing-site.com/confirm?email=${targetInfo.email}" style="color: #1a73e8; text-decoration: underline;">https://training.${targetInfo.company.toLowerCase().replace(/\s+/g, '')}.com/confirm</a></p>
  
  <p>确认参与需要使用您的公司账户登录。</p>
  
  <p>期待您的参与！</p>
  
  <p>此致，<br>${targetInfo.company} 人力资源部</p>
</div>
      `
    } else {
      // 默认钓鱼邮件
      sender = `系统管理员 <admin@${targetInfo.company.toLowerCase().replace(/\s+/g, '')}.com>`
      subject = `重要：系统更新通知`
      content = `
<div style="font-family: Arial, sans-serif; color: #333;">
  <p>${targetInfo.username}，</p>
  
  <p>我们的系统需要进行重要更新。请点击以下链接登录系统完成必要的配置：</p>
  
  <p><a href="http://evil-phishing-site.com/login?email=${targetInfo.email}" style="color: #1a73e8; text-decoration: underline;">https://system.${targetInfo.company.toLowerCase().replace(/\s+/g, '')}.com/update</a></p>
  
  <p>此更新对于系统安全至关重要，请在今天内完成。</p>
  
  <p>谢谢配合。</p>
</div>
      `
    }
    
    return {
      subject,
      content,
      sender,
      recipient: `${targetInfo.username} <${targetInfo.email}>`,
      timestamp: new Date().toISOString(),
      malicious_link: 'http://evil-corp-phishing.com/login'
    }
  }
  
  /**
   * 模拟发送钓鱼邮件
   * @param {Object} targetInfo - 目标信息
   * @param {Object} email - 钓鱼邮件内容
   * @returns {Promise<Object>} - 返回发送结果
   */
  static async sendPhishingEmail(targetInfo, email) {
    // 模拟API调用延迟
    await simulateDelay(1500)
    
    // 模拟发送成功率
    const successRate = Math.random()
    const isSuccess = successRate > 0.2 // 80%的成功率
    
    if (isSuccess) {
      return {
        status: "compromised",
        detail: "凭据已发送给攻击者。",
        match_score: 3,
        max_score: 4,
        success_rate: "75%"
      }
    } else {
      return {
        status: "ignored",
        detail: "邮件与受害者信息匹配度不足。",
        match_score: 1,
        max_score: 4,
        success_rate: "25%"
      }
    }
  }
}

export default PhishingService