/**
 * 容器配置服务
 * 提供容器实时配置管理的API调用功能
 */

// 模拟API调用延迟
const simulateDelay = (ms = 500) => new Promise(resolve => setTimeout(resolve, ms))

/**
 * 容器配置服务类
 */
class ContainerConfigService {
  /**
   * 获取容器详细信息
   * @param {Object} container - 容器对象
   * @returns {Promise<Object>} - 返回容器详细信息
   */
  static async getContainerInfo(container) {
    try {
      console.log('🔍 ContainerConfigService: 开始获取容器信息', container)
      await simulateDelay(200) // 减少延迟时间
      
      const { deviceData } = container
      const containerId = this._getContainerId(container)
      
      console.log('📋 容器基本信息:', { deviceData, containerId })
      
      // 构建API请求URL
      const apiUrl = `/api/containers/${containerId}/info`
      
      // 在实际应用中，这里应该发起真实的API请求
      // const response = await fetch(apiUrl)
      // return await response.json()
      
      // 这里使用模拟数据
      const mockInfo = this._generateMockContainerInfo(deviceData)
      console.log('✅ 生成的模拟容器信息:', mockInfo)
      return mockInfo
    } catch (error) {
      console.error('❌ 获取容器信息失败:', error)
      return this._generateDefaultContainerInfo(container)
    }
  }

  /**
   * 应用容器配置更改
   * @param {Object} container - 容器对象
   * @param {Object} changes - 配置更改
   * @returns {Promise<Object>} - 返回应用结果
   */
  static async applyContainerConfig(container, changes) {
    try {
      await simulateDelay(1000) // 模拟配置应用时间
      
      const containerId = this._getContainerId(container)
      
      // 构建API请求
      const apiUrl = `/api/containers/${containerId}/config`
      const requestBody = {
        network: changes.network || {},
        firewall: changes.firewall || {},
        services: changes.services || {}
      }
      
      console.log('应用容器配置:', {
        containerId,
        changes: requestBody
      })
      
      // 在实际应用中，这里应该发起真实的API请求
      // const response = await fetch(apiUrl, {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json'
      //   },
      //   body: JSON.stringify(requestBody)
      // })
      // 
      // if (!response.ok) {
      //   throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      // }
      // 
      // return await response.json()
      
      // 模拟成功响应
      return {
        success: true,
        message: '容器配置已成功应用',
        appliedChanges: requestBody
      }
    } catch (error) {
      console.error('应用容器配置失败:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }

  /**
   * 获取容器实时状态
   * @param {Object} container - 容器对象
   * @returns {Promise<Object>} - 返回容器状态
   */
  static async getContainerStatus(container) {
    try {
      await simulateDelay(200)
      
      const containerId = this._getContainerId(container)
      const apiUrl = `/api/containers/${containerId}/status`
      
      // 模拟状态数据
      return {
        id: containerId,
        status: 'running',
        uptime: '2h 15m',
        cpuUsage: Math.floor(Math.random() * 100),
        memoryUsage: Math.floor(Math.random() * 100),
        networkIn: `${(Math.random() * 10).toFixed(1)}KB/s`,
        networkOut: `${(Math.random() * 5).toFixed(1)}KB/s`,
        diskUsage: Math.floor(Math.random() * 100)
      }
    } catch (error) {
      console.error('获取容器状态失败:', error)
      return {
        id: this._getContainerId(container),
        status: 'unknown',
        error: error.message
      }
    }
  }

  /**
   * 重启容器服务
   * @param {Object} container - 容器对象
   * @param {string} serviceName - 服务名称
   * @returns {Promise<Object>} - 返回操作结果
   */
  static async restartContainerService(container, serviceName) {
    try {
      await simulateDelay(2000)
      
      const containerId = this._getContainerId(container)
      const apiUrl = `/api/containers/${containerId}/services/${serviceName}/restart`
      
      console.log(`重启容器服务: ${containerId}/${serviceName}`)
      
      return {
        success: true,
        message: `服务 ${serviceName} 已重启`
      }
    } catch (error) {
      console.error('重启容器服务失败:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }

  /**
   * 更新防火墙规则
   * @param {Object} container - 容器对象
   * @param {Array} rules - 防火墙规则
   * @returns {Promise<Object>} - 返回操作结果
   */
  static async updateFirewallRules(container, rules) {
    try {
      await simulateDelay(1500)
      
      const containerId = this._getContainerId(container)
      const apiUrl = `/api/containers/${containerId}/firewall/rules`
      
      console.log(`更新防火墙规则: ${containerId}`, rules)
      
      return {
        success: true,
        message: `已更新 ${rules.length} 条防火墙规则`,
        appliedRules: rules
      }
    } catch (error) {
      console.error('更新防火墙规则失败:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }

  /**
   * 更新网络配置
   * @param {Object} container - 容器对象
   * @param {Object} networkConfig - 网络配置
   * @returns {Promise<Object>} - 返回操作结果
   */
  static async updateNetworkConfig(container, networkConfig) {
    try {
      await simulateDelay(1000)
      
      const containerId = this._getContainerId(container)
      const apiUrl = `/api/containers/${containerId}/network`
      
      console.log(`更新网络配置: ${containerId}`, networkConfig)
      
      return {
        success: true,
        message: '网络配置已更新',
        appliedConfig: networkConfig
      }
    } catch (error) {
      console.error('更新网络配置失败:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }

  /**
   * 获取容器ID
   * @private
   * @param {Object} container - 容器对象
   * @returns {string} - 容器ID
   */
  static _getContainerId(container) {
    const containerId = container.deviceData?.scenarioData?.id || 
                       container.deviceData?.id || 
                       container.id || 
                       'unknown'
    console.log('🆔 获取容器ID:', { container, containerId })
    return containerId
  }

  /**
   * 生成模拟的容器信息
   * @private
   * @param {Object} deviceData - 设备数据
   * @returns {Object} - 模拟的容器信息
   */
  static _generateMockContainerInfo(deviceData) {
    console.log('🏗️ 生成模拟容器信息，输入数据:', deviceData)
    
    const name = deviceData?.name || '未知容器'
    const ip = deviceData?.ip || '192.168.1.100'
    const network = deviceData?.network || 'default_network'
    
    const mockInfo = {
      id: `container_${Date.now()}`,
      name: name,
      status: 'running',
      ip: ip,
      network: network,
      netmask: '255.255.255.0',
      gateway: this._getGatewayForNetwork(network),
      portMappings: this._generatePortMappings(name),
      primaryDNS: '8.8.8.8',
      secondaryDNS: '8.8.4.4',
      searchDomains: 'company.local',
      enableIPv6: false,
      enableBridge: true,
      enableNAT: false,
      enableDHCP: false,
      mtu: 1500,
      priority: 'normal',
      bandwidthLimit: 100,
      networkMode: 'bridge',
      
      // 防火墙配置
      firewallEnabled: true,
      defaultPolicy: 'deny',
      logEnabled: true,
      logLevel: 'info',
      firewallRules: this._generateFirewallRules(name),
      whitelist: this._generateWhitelist(),
      blacklist: this._generateBlacklist(),
      
      // 服务信息
      services: this._generateServices(name),
      ports: this._generatePorts(name),
      
      // 监控信息
      monitoringEnabled: true,
      monitoringInterval: 10,
      alertEnabled: true,
      cpuThreshold: 80,
      cpuUsage: Math.floor(Math.random() * 100),
      memoryUsage: Math.floor(Math.random() * 100),
      memoryUsed: Math.floor(Math.random() * 2048),
      memoryTotal: 4096,
      networkIn: `${(Math.random() * 10).toFixed(1)}KB/s`,
      networkOut: `${(Math.random() * 5).toFixed(1)}KB/s`,
      diskUsage: Math.floor(Math.random() * 100)
    }
    
    console.log('📦 生成的模拟信息:', mockInfo)
    return mockInfo
  }

  /**
   * 根据网络段获取网关
   * @private
   * @param {string} network - 网络段
   * @returns {string} - 网关地址
   */
  static _getGatewayForNetwork(network) {
    const gateways = {
      'dmz_segment': '172.16.100.1',
      'server_segment': '192.168.200.1',
      'user_segment': '192.168.100.1',
      'db_segment': '192.168.214.1',
      'medical_segment': '192.168.101.1',
      'siem_segment': '192.168.66.1',
      'vpn_segment': '192.168.110.1'
    }
    return gateways[network] || '192.168.1.1'
  }

  /**
   * 生成端口映射
   * @private
   * @param {string} containerName - 容器名称
   * @returns {Array} - 端口映射列表
   */
  static _generatePortMappings(containerName) {
    const mappings = []
    
    // 默认SSH端口
    mappings.push(
      { containerPort: 22, hostPort: 2222, protocol: 'tcp', description: 'SSH访问' }
    )
    
    if (containerName.includes('Web') || containerName.includes('web')) {
      mappings.push(
        { containerPort: 80, hostPort: 8080, protocol: 'tcp', description: 'HTTP服务' },
        { containerPort: 443, hostPort: 8443, protocol: 'tcp', description: 'HTTPS服务' },
        { containerPort: 8080, hostPort: 18080, protocol: 'tcp', description: '管理界面' }
      )
    } else if (containerName.includes('数据库') || containerName.includes('database') || containerName.includes('db')) {
      mappings.push(
        { containerPort: 3306, hostPort: 3306, protocol: 'tcp', description: 'MySQL数据库' },
        { containerPort: 5432, hostPort: 5432, protocol: 'tcp', description: 'PostgreSQL数据库' },
        { containerPort: 6379, hostPort: 6379, protocol: 'tcp', description: 'Redis缓存' }
      )
    } else if (containerName.includes('DNS') || containerName.includes('dns')) {
      mappings.push(
        { containerPort: 53, hostPort: 5353, protocol: 'tcp', description: 'DNS查询(TCP)' },
        { containerPort: 53, hostPort: 5353, protocol: 'udp', description: 'DNS查询(UDP)' }
      )
    } else if (containerName.includes('邮件') || containerName.includes('mail')) {
      mappings.push(
        { containerPort: 25, hostPort: 2525, protocol: 'tcp', description: 'SMTP服务' },
        { containerPort: 110, hostPort: 1110, protocol: 'tcp', description: 'POP3服务' },
        { containerPort: 143, hostPort: 1143, protocol: 'tcp', description: 'IMAP服务' }
      )
    } else if (containerName.includes('防火墙') || containerName.includes('firewall')) {
      mappings.push(
        { containerPort: 443, hostPort: 4443, protocol: 'tcp', description: '管理界面' },
        { containerPort: 161, hostPort: 1161, protocol: 'udp', description: 'SNMP监控' }
      )
    } else {
      // 通用服务器端口
      mappings.push(
        { containerPort: 80, hostPort: 8080, protocol: 'tcp', description: 'HTTP服务' },
        { containerPort: 443, hostPort: 8443, protocol: 'tcp', description: 'HTTPS服务' }
      )
    }
    
    return mappings
  }

  /**
   * 生成防火墙规则
   * @private
   * @param {string} containerName - 容器名称
   * @returns {Array} - 防火墙规则列表
   */
  static _generateFirewallRules(containerName) {
    const rules = [
      { action: 'allow', source: 'any', destination: 'any', protocol: 'tcp', port: '22', description: '允许SSH访问', enabled: true },
      { action: 'allow', source: '192.168.100.0/24', destination: 'any', protocol: 'tcp', port: '80', description: '允许内网HTTP访问', enabled: true },
      { action: 'deny', source: 'any', destination: 'any', protocol: 'tcp', port: '3389', description: '拒绝RDP访问', enabled: true },
      { action: 'allow', source: '127.0.0.1', destination: 'any', protocol: 'any', port: 'any', description: '允许本地回环', enabled: true },
      { action: 'deny', source: '10.0.0.0/8', destination: 'any', protocol: 'any', port: 'any', description: '拒绝私有网段A类', enabled: false },
      { action: 'allow', source: '192.168.0.0/16', destination: 'any', protocol: 'tcp', port: '443', description: '允许内网HTTPS访问', enabled: true }
    ]
    
    if (containerName.includes('数据库') || containerName.includes('database')) {
      rules.push(
        { action: 'allow', source: '192.168.200.0/24', destination: 'any', protocol: 'tcp', port: '3306', description: '允许服务器段访问MySQL', enabled: true },
        { action: 'allow', source: '192.168.200.0/24', destination: 'any', protocol: 'tcp', port: '5432', description: '允许服务器段访问PostgreSQL', enabled: false },
        { action: 'deny', source: 'any', destination: 'any', protocol: 'tcp', port: '3306', description: '拒绝外部访问数据库', enabled: true }
      )
    }
    
    if (containerName.includes('Web') || containerName.includes('web')) {
      rules.push(
        { action: 'allow', source: 'any', destination: 'any', protocol: 'tcp', port: '80', description: '允许HTTP访问', enabled: true },
        { action: 'allow', source: 'any', destination: 'any', protocol: 'tcp', port: '443', description: '允许HTTPS访问', enabled: true },
        { action: 'deny', source: 'any', destination: 'any', protocol: 'tcp', port: '8080', description: '拒绝管理端口访问', enabled: true }
      )
    }
    
    if (containerName.includes('防火墙') || containerName.includes('firewall')) {
      rules.push(
        { action: 'allow', source: '192.168.0.0/16', destination: 'any', protocol: 'any', port: 'any', description: '允许内网流量', enabled: true },
        { action: 'deny', source: 'any', destination: 'any', protocol: 'icmp', port: 'any', description: '拒绝ICMP流量', enabled: false },
        { action: 'allow', source: 'any', destination: 'any', protocol: 'tcp', port: '53', description: '允许DNS查询', enabled: true },
        { action: 'allow', source: 'any', destination: 'any', protocol: 'udp', port: '53', description: '允许DNS查询(UDP)', enabled: true }
      )
    }
    
    return rules
  }

  /**
   * 生成白名单
   * @private
   * @returns {Array} - 白名单列表
   */
  static _generateWhitelist() {
    return [
      { address: '192.168.100.0/24', description: '内网用户段', addedAt: '2024-01-15 10:30:00' },
      { address: '192.168.200.0/24', description: '服务器段', addedAt: '2024-01-15 10:30:00' },
      { address: '192.168.214.0/24', description: '数据库段', addedAt: '2024-01-15 10:30:00' },
      { address: '172.16.100.0/24', description: 'DMZ段', addedAt: '2024-01-15 10:30:00' },
      { address: '8.8.8.8', description: 'Google DNS主服务器', addedAt: '2024-01-15 10:30:00' },
      { address: '8.8.4.4', description: 'Google DNS备用服务器', addedAt: '2024-01-15 10:30:00' },
      { address: '114.114.114.114', description: '114 DNS服务器', addedAt: '2024-01-16 09:15:00' },
      { address: '127.0.0.1', description: '本地回环地址', addedAt: '2024-01-15 10:30:00' },
      { address: '192.168.101.0/24', description: '医疗设备段', addedAt: '2024-01-17 14:20:00' },
      { address: '192.168.66.0/24', description: 'SIEM监控段', addedAt: '2024-01-17 14:20:00' }
    ]
  }

  /**
   * 生成黑名单
   * @private
   * @returns {Array} - 黑名单列表
   */
  static _generateBlacklist() {
    return [
      { address: '10.0.0.0/8', description: '私有网段A类 - 潜在威胁', addedAt: '2024-01-15 10:30:00', reason: '网络扫描' },
      { address: '172.16.0.0/12', description: '私有网段B类 - 受限访问', addedAt: '2024-01-15 10:30:00', reason: '策略限制' },
      { address: '192.168.1.100', description: '可疑主机 - 多次失败登录', addedAt: '2024-01-18 15:45:00', reason: '暴力破解' },
      { address: '203.0.113.0/24', description: '测试网段 - 禁止访问', addedAt: '2024-01-16 11:20:00', reason: '测试流量' },
      { address: '198.51.100.0/24', description: '示例网段 - 文档用途', addedAt: '2024-01-16 11:20:00', reason: '文档示例' },
      { address: '169.254.0.0/16', description: 'APIPA地址段 - 自动配置', addedAt: '2024-01-15 10:30:00', reason: '配置错误' },
      { address: '224.0.0.0/4', description: '组播地址段 - 不允许', addedAt: '2024-01-15 10:30:00', reason: '协议限制' },
      { address: '0.0.0.0/8', description: '保留地址段 - 无效源', addedAt: '2024-01-15 10:30:00', reason: '无效地址' },
      { address: '192.168.999.1', description: '恶意IP - 已知攻击源', addedAt: '2024-01-19 08:30:00', reason: '恶意活动' },
      { address: '1.2.3.4', description: '测试攻击源 - 演练用', addedAt: '2024-01-19 16:00:00', reason: '演练测试' }
    ]
  }

  /**
   * 生成服务列表
   * @private
   * @param {string} containerName - 容器名称
   * @returns {Array} - 服务列表
   */
  static _generateServices(containerName) {
    const services = [
      { name: 'ssh', status: 'running', ports: [22], autostart: true, cpuUsage: '0.1%', memoryUsage: '5MB', description: 'SSH服务' },
      { name: 'systemd', status: 'running', ports: [], autostart: true, cpuUsage: '0.2%', memoryUsage: '8MB', description: '系统管理' },
      { name: 'cron', status: 'running', ports: [], autostart: true, cpuUsage: '0.1%', memoryUsage: '2MB', description: '定时任务' }
    ]
    
    if (containerName.includes('Web') || containerName.includes('web')) {
      services.push(
        { name: 'nginx', status: 'running', ports: [80, 443], autostart: true, cpuUsage: '2.1%', memoryUsage: '45MB', description: 'Web服务器' },
        { name: 'php-fpm', status: 'running', ports: [9000], autostart: true, cpuUsage: '1.8%', memoryUsage: '32MB', description: 'PHP处理器' },
        { name: 'redis', status: 'stopped', ports: [6379], autostart: false, cpuUsage: '0%', memoryUsage: '0MB', description: 'Redis缓存' }
      )
    } else if (containerName.includes('数据库') || containerName.includes('database') || containerName.includes('db')) {
      services.push(
        { name: 'mysql', status: 'running', ports: [3306], autostart: true, cpuUsage: '5.2%', memoryUsage: '128MB', description: 'MySQL数据库' },
        { name: 'mysqld_safe', status: 'running', ports: [], autostart: true, cpuUsage: '0.3%', memoryUsage: '12MB', description: 'MySQL守护进程' },
        { name: 'redis', status: 'running', ports: [6379], autostart: true, cpuUsage: '1.2%', memoryUsage: '24MB', description: 'Redis缓存' }
      )
    } else if (containerName.includes('DNS') || containerName.includes('dns')) {
      services.push(
        { name: 'named', status: 'running', ports: [53], autostart: true, cpuUsage: '0.8%', memoryUsage: '18MB', description: 'DNS服务' },
        { name: 'systemd-resolved', status: 'running', ports: [], autostart: true, cpuUsage: '0.2%', memoryUsage: '6MB', description: '系统DNS解析' }
      )
    } else if (containerName.includes('邮件') || containerName.includes('mail')) {
      services.push(
        { name: 'postfix', status: 'running', ports: [25], autostart: true, cpuUsage: '1.5%', memoryUsage: '28MB', description: 'SMTP服务' },
        { name: 'dovecot', status: 'running', ports: [110, 143], autostart: true, cpuUsage: '1.2%', memoryUsage: '22MB', description: 'POP3/IMAP服务' },
        { name: 'spamassassin', status: 'stopped', ports: [], autostart: false, cpuUsage: '0%', memoryUsage: '0MB', description: '垃圾邮件过滤' }
      )
    } else if (containerName.includes('防火墙') || containerName.includes('firewall')) {
      services.push(
        { name: 'iptables', status: 'running', ports: [], autostart: true, cpuUsage: '0.5%', memoryUsage: '8MB', description: '防火墙服务' },
        { name: 'fail2ban', status: 'running', ports: [], autostart: true, cpuUsage: '0.3%', memoryUsage: '12MB', description: '入侵防护' },
        { name: 'snmpd', status: 'stopped', ports: [161], autostart: false, cpuUsage: '0%', memoryUsage: '0MB', description: 'SNMP监控' }
      )
    } else {
      // 通用服务器服务
      services.push(
        { name: 'apache2', status: 'stopped', ports: [80], autostart: false, cpuUsage: '0%', memoryUsage: '0MB', description: 'Apache Web服务器' },
        { name: 'nginx', status: 'running', ports: [80, 443], autostart: true, cpuUsage: '1.5%', memoryUsage: '35MB', description: 'Nginx Web服务器' }
      )
    }
    
    return services
  }

  /**
   * 生成端口列表
   * @private
   * @param {string} containerName - 容器名称
   * @returns {Array} - 端口列表
   */
  static _generatePorts(containerName) {
    const ports = [
      { port: 22, protocol: 'tcp', status: 'open', service: 'ssh', process: 'sshd', description: 'SSH远程访问' }
    ]
    
    if (containerName.includes('Web') || containerName.includes('web')) {
      ports.push(
        { port: 80, protocol: 'tcp', status: 'open', service: 'http', process: 'nginx', description: 'HTTP Web服务' },
        { port: 443, protocol: 'tcp', status: 'closed', service: 'https', process: '', description: 'HTTPS Web服务' },
        { port: 8080, protocol: 'tcp', status: 'open', service: 'http-alt', process: 'nginx', description: '备用HTTP端口' },
        { port: 9000, protocol: 'tcp', status: 'listening', service: 'php-fpm', process: 'php-fpm', description: 'PHP FastCGI' }
      )
    } else if (containerName.includes('数据库') || containerName.includes('database') || containerName.includes('db')) {
      ports.push(
        { port: 3306, protocol: 'tcp', status: 'listening', service: 'mysql', process: 'mysqld', description: 'MySQL数据库' },
        { port: 5432, protocol: 'tcp', status: 'closed', service: 'postgresql', process: '', description: 'PostgreSQL数据库' },
        { port: 6379, protocol: 'tcp', status: 'open', service: 'redis', process: 'redis-server', description: 'Redis缓存' }
      )
    } else if (containerName.includes('DNS') || containerName.includes('dns')) {
      ports.push(
        { port: 53, protocol: 'tcp', status: 'open', service: 'domain', process: 'named', description: 'DNS查询(TCP)' },
        { port: 53, protocol: 'udp', status: 'open', service: 'domain', process: 'named', description: 'DNS查询(UDP)' },
        { port: 953, protocol: 'tcp', status: 'closed', service: 'rndc', process: '', description: 'DNS管理' }
      )
    } else if (containerName.includes('邮件') || containerName.includes('mail')) {
      ports.push(
        { port: 25, protocol: 'tcp', status: 'open', service: 'smtp', process: 'postfix', description: 'SMTP邮件发送' },
        { port: 110, protocol: 'tcp', status: 'open', service: 'pop3', process: 'dovecot', description: 'POP3邮件接收' },
        { port: 143, protocol: 'tcp', status: 'open', service: 'imap', process: 'dovecot', description: 'IMAP邮件访问' },
        { port: 993, protocol: 'tcp', status: 'closed', service: 'imaps', process: '', description: 'IMAP SSL' },
        { port: 995, protocol: 'tcp', status: 'closed', service: 'pop3s', process: '', description: 'POP3 SSL' }
      )
    } else if (containerName.includes('防火墙') || containerName.includes('firewall')) {
      ports.push(
        { port: 443, protocol: 'tcp', status: 'open', service: 'https', process: 'nginx', description: '管理界面' },
        { port: 161, protocol: 'udp', status: 'closed', service: 'snmp', process: '', description: 'SNMP监控' },
        { port: 514, protocol: 'udp', status: 'open', service: 'syslog', process: 'rsyslog', description: '系统日志' }
      )
    } else {
      // 通用端口
      ports.push(
        { port: 80, protocol: 'tcp', status: 'open', service: 'http', process: 'nginx', description: 'HTTP Web服务' },
        { port: 443, protocol: 'tcp', status: 'closed', service: 'https', process: '', description: 'HTTPS Web服务' },
        { port: 8080, protocol: 'tcp', status: 'filtered', service: 'http-proxy', process: '', description: 'HTTP代理' }
      )
    }
    
    return ports
  }

  /**
   * 生成默认的容器信息
   * @private
   * @param {Object} container - 容器对象
   * @returns {Object} - 默认的容器信息
   */
  static _generateDefaultContainerInfo(container) {
    console.log('🔧 生成默认容器信息，输入:', container)
    
    const { deviceData } = container
    
    const defaultInfo = {
      id: this._getContainerId(container),
      name: deviceData?.name || '未知容器',
      status: 'unknown',
      ip: deviceData?.ip || '192.168.1.100',
      network: deviceData?.network || 'default',
      netmask: '255.255.255.0',
      gateway: '192.168.1.1',
      portMappings: [],
      primaryDNS: '8.8.8.8',
      secondaryDNS: '8.8.4.4',
      searchDomains: '',
      enableIPv6: false,
      enableBridge: true,
      enableNAT: false,
      enableDHCP: false,
      mtu: 1500,
      priority: 'normal',
      bandwidthLimit: 100,
      networkMode: 'bridge',
      firewallEnabled: true,
      defaultPolicy: 'deny',
      logEnabled: true,
      logLevel: 'info',
      firewallRules: [],
      whitelist: [],
      blacklist: [],
      services: [],
      ports: [],
      monitoringEnabled: true,
      monitoringInterval: 10,
      alertEnabled: true,
      cpuThreshold: 80,
      cpuUsage: 50,
      memoryUsage: 60,
      memoryUsed: 1024,
      memoryTotal: 2048,
      networkIn: '1.0KB/s',
      networkOut: '0.5KB/s',
      diskUsage: 30
    }
    
    console.log('📦 生成的默认信息:', defaultInfo)
    return defaultInfo
  }
}

export default ContainerConfigService
