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
尊敬的 ${targetInfo.username}，

我们的系统检测到您的账户存在异常登录活动。为了保障您的账户安全，请立即点击以下链接重置您的密码：

<a href="http://evil-phishing-site.com/reset?email=${targetInfo.email}">https://${targetInfo.company.toLowerCase().replace(/\s+/g, '')}.com/account/security/reset</a>

如果您没有进行过可疑操作，请务必在24小时内完成密码重置，否则您的账户将被临时冻结。

此致，
${targetInfo.company} IT安全团队
      `
    } else if (attackType === 'social_engineering') {
      // 社会工程学攻击邮件
      const randomInterest = targetInfo.interests[Math.floor(Math.random() * targetInfo.interests.length)]
      sender = `${targetInfo.company} 人力资源部 <hr@${targetInfo.company.toLowerCase().replace(/\s+/g, '')}.com>`
      subject = `关于${randomInterest}的内部培训通知`
      content = `
亲爱的 ${targetInfo.username}，

根据公司的人才发展计划，我们注意到您对${randomInterest}领域有浓厚的兴趣。

我们将于下周举办一场关于${randomInterest}的内部培训，由行业顶尖专家主讲。由于名额有限，请点击以下链接确认您的参与：

<a href="http://evil-phishing-site.com/confirm?email=${targetInfo.email}">https://training.${targetInfo.company.toLowerCase().replace(/\s+/g, '')}.com/confirm</a>

确认参与需要使用您的公司账户登录。

期待您的参与！

此致，
${targetInfo.company} 人力资源部
      `
    } else {
      // 默认钓鱼邮件
      sender = `系统管理员 <admin@${targetInfo.company.toLowerCase().replace(/\s+/g, '')}.com>`
      subject = `重要：系统更新通知`
      content = `
${targetInfo.username}，

我们的系统需要进行重要更新。请点击以下链接登录系统完成必要的配置：

<a href="http://evil-phishing-site.com/login?email=${targetInfo.email}">https://system.${targetInfo.company.toLowerCase().replace(/\s+/g, '')}.com/update</a>

此更新对于系统安全至关重要，请在今天内完成。

谢谢配合。
      `
    }
    
    return {
      sender,
      recipient: `${targetInfo.username} <${targetInfo.email}>`,
      subject,
      content,
      timestamp: new Date().toISOString()
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
        success: true,
        message: `成功向 ${targetInfo.email} 发送钓鱼邮件`,
        deliveryStatus: 'delivered',
        openRate: Math.random() * 0.7 + 0.3, // 30%-100%的打开率
        clickRate: Math.random() * 0.6 + 0.2 // 20%-80%的点击率
      }
    } else {
      throw new Error(`向 ${targetInfo.email} 发送钓鱼邮件失败：邮件被拦截`)
    }
  }
  
  /**
   * 模拟社会工程学攻击
   * @param {Object} attackData - 攻击数据
   * @returns {Promise<Object>} - 返回攻击结果
   */
  static async simulateSocialEngineeringAttack(attackData) {
    try {
      // 模拟API调用延迟
      await simulateDelay(2500)
      
      // 获取目标主机的详细信息
      const targetInfo = await this.getTargetInfo(attackData.target)
      
      // 生成社会工程学攻击脚本
      const script = await this.generateSocialEngineeringScript(targetInfo)
      
      // 模拟执行社会工程学攻击
      const result = await this.executeSocialEngineering(targetInfo, script)
      
      return {
        success: true,
        message: `成功对 ${targetInfo.name} 发起社会工程学攻击`,
        details: {
          targetInfo,
          script,
          result
        }
      }
    } catch (error) {
      console.error('社会工程学攻击失败:', error)
      return {
        success: false,
        message: `社会工程学攻击失败: ${error.message}`,
        error
      }
    }
  }
  
  /**
   * 生成社会工程学攻击脚本
   * @param {Object} targetInfo - 目标信息
   * @returns {Promise<Object>} - 返回攻击脚本
   */
  static async generateSocialEngineeringScript(targetInfo) {
    // 模拟API调用延迟
    await simulateDelay(1000)
    
    // 根据目标信息生成社会工程学攻击脚本
    const attackTypes = [
      'pretexting', // 借口攻击
      'baiting',    // 诱饵攻击
      'quid_pro_quo', // 交换条件攻击
      'tailgating', // 尾随攻击
      'vishing'     // 语音钓鱼
    ]
    
    const attackType = attackTypes[Math.floor(Math.random() * attackTypes.length)]
    let script = {}
    
    switch (attackType) {
      case 'pretexting':
        script = {
          type: 'pretexting',
          name: '借口攻击',
          scenario: `以IT支持人员身份联系${targetInfo.username}`,
          approach: `声称需要远程访问其计算机解决${targetInfo.department}部门报告的系统问题`,
          goal: '获取远程访问权限和登录凭据',
          script: `
您好，${targetInfo.username}。我是IT支持部门的Alex。我们收到${targetInfo.department}部门报告，说您的计算机可能受到了安全漏洞的影响。

为了解决这个问题，我需要远程访问您的计算机进行安全扫描。这只需要几分钟时间，不会影响您的工作。

请您下载并安装这个远程访问工具，然后告诉我访问码，这样我就可以帮您解决问题了。
          `
        }
        break
      
      case 'baiting':
        script = {
          type: 'baiting',
          name: '诱饵攻击',
          scenario: `向${targetInfo.username}发送带有恶意软件的免费礼品卡`,
          approach: `以公司福利的名义提供"员工专属折扣"`,
          goal: '诱导安装恶意软件',
          script: `
亲爱的${targetInfo.username}，

作为我们对${targetInfo.company}优秀员工的感谢，您被选中获得价值500元的亚马逊礼品卡！

作为${targetInfo.department}的${targetInfo.role}，您的贡献对公司至关重要。

请下载附件中的礼品卡兑换程序，输入您的员工ID和密码进行验证后即可获得礼品卡代码。
          `
        }
        break
      
      case 'quid_pro_quo':
        script = {
          type: 'quid_pro_quo',
          name: '交换条件攻击',
          scenario: `提供免费技术支持以换取${targetInfo.username}的信息`,
          approach: `声称可以提供新软件的高级功能`,
          goal: '获取登录凭据',
          script: `
${targetInfo.username}您好，

我是新软件部署团队的成员。我们注意到您还没有激活${targetInfo.department}部门新软件的高级功能。

作为特别优惠，我可以帮您免费激活这些功能，这通常需要额外付费。

我只需要您的登录凭据来完成激活过程。完成后，您将立即获得所有高级功能的访问权限。
          `
        }
        break
      
      case 'tailgating':
        script = {
          type: 'tailgating',
          name: '尾随攻击',
          scenario: `在${targetInfo.company}办公室附近等待${targetInfo.username}`,
          approach: `假装是新员工，手里拿着咖啡和文件，请求帮忙开门`,
          goal: '获取物理访问权限',
          script: `
[看到${targetInfo.username}接近门禁]

嘿，你好！我是${targetInfo.department}部门的新员工，今天是我的第一天。我叫Mike。

[举起手中的咖啡和文件]

抱歉，我的门禁卡还没有激活，我的手又满了。你能帮我开一下门吗？我要去见我的经理。

[如果被问到更多问题]

我是来协助${targetInfo.role}项目的。IT部门说我的门禁卡要到明天才能用。真是不好意思麻烦你了。
          `
        }
        break
      
      case 'vishing':
        script = {
          type: 'vishing',
          name: '语音钓鱼',
          scenario: `给${targetInfo.username}打电话，假装是银行安全部门`,
          approach: `声称检测到可疑交易，需要验证身份`,
          goal: '获取银行账户信息和个人信息',
          script: `
您好，请问是${targetInfo.username}吗？

我是中国银行安全部门的李经理。我们的系统检测到您的账户有一笔可疑的海外交易，金额为25,000元。

为了保护您的账户安全，我们需要立即验证您的身份。请您提供您的银行账号后六位和身份证号码后四位，以便我们确认这不是欺诈交易。

如果您不方便提供，我们将按照程序冻结您的账户48小时进行调查，以防止可能的资金损失。
          `
        }
        break
    }
    
    return script
  }
  
  /**
   * 模拟执行社会工程学攻击
   * @param {Object} targetInfo - 目标信息
   * @param {Object} script - 攻击脚本
   * @returns {Promise<Object>} - 返回执行结果
   */
  static async executeSocialEngineering(targetInfo, script) {
    // 模拟API调用延迟
    await simulateDelay(2000)
    
    // 模拟攻击成功率
    const baseSuccessRate = 0.6 // 基础成功率60%
    
    // 根据攻击类型调整成功率
    let typeModifier = 0
    switch (script.type) {
      case 'pretexting': typeModifier = 0.1; break // +10%
      case 'baiting': typeModifier = 0.05; break // +5%
      case 'quid_pro_quo': typeModifier = 0.15; break // +15%
      case 'tailgating': typeModifier = -0.1; break // -10%
      case 'vishing': typeModifier = 0; break // 不变
    }
    
    // 根据目标角色调整成功率
    let roleModifier = 0
    if (targetInfo.role.includes('管理员')) {
      roleModifier = -0.2 // 管理员更警惕，-20%
    } else if (targetInfo.role.includes('工程师')) {
      roleModifier = -0.1 // 工程师更警惕，-10%
    } else {
      roleModifier = 0.1 // 其他角色可能更容易受骗，+10%
    }
    
    // 计算最终成功率
    const finalSuccessRate = Math.max(0.1, Math.min(0.9, baseSuccessRate + typeModifier + roleModifier))
    
    // 随机决定是否成功
    const isSuccess = Math.random() < finalSuccessRate
    
    if (isSuccess) {
      return {
        success: true,
        message: `成功对 ${targetInfo.username} 执行${script.name}`,
        successRate: finalSuccessRate,
        obtainedInfo: {
          credentials: targetInfo.role.includes('管理员') ? '部分凭据' : '完整凭据',
          personalInfo: true,
          accessLevel: targetInfo.role.includes('管理员') ? 'medium' : 'high'
        }
      }
    } else {
      return {
        success: false,
        message: `对 ${targetInfo.username} 执行${script.name}失败`,
        successRate: finalSuccessRate,
        reason: '目标警觉性高，拒绝提供信息或执行请求的操作'
      }
    }
  }
}

export default PhishingService