/**
 * 主机信息服务
 * 提供获取主机详细信息的API调用和模拟功能
 */

// 模拟API调用延迟
const simulateDelay = (ms = 500) => new Promise(resolve => setTimeout(resolve, ms))

/**
 * 主机信息服务类
 */
class HostInfoService {
  /**
   * 获取主机详细信息
   * @param {Object} host - 主机对象
   * @returns {Promise<Object>} - 返回主机详细信息
   */
  static async getHostInfo(host) {
    try {
      // 模拟API调用延迟
      await simulateDelay()
      
      // 从主机获取基本信息
      const { deviceData } = host
      
      // 构建API请求URL
      const apiUrl = `/api/hosts/${deviceData.ip}/info`
      
      // 在实际应用中，这里应该发起真实的API请求
      // 这里使用模拟数据
      return this._generateMockHostInfo(deviceData)
    } catch (error) {
      console.error('获取主机信息失败:', error)
      return this._generateDefaultHostInfo(host)
    }
  }
  
  /**
   * 生成模拟的主机信息
   * @private
   * @param {Object} deviceData - 设备数据
   * @returns {Object} - 返回模拟的主机信息
   */
  static _generateMockHostInfo(deviceData) {
    // 根据主机名和类型生成不同的模拟数据
    const name = deviceData.name || ''
    const type = deviceData.type || ''
    
    // 基本信息
    const info = {
      name: deviceData.name,
      ip: deviceData.ip,
      mac: deviceData.mac,
      status: deviceData.status || 'running'
    }
    
    // 根据主机类型和名称添加详细信息
    if (name.includes('PC') || type === 'workstation') {
      return {
        ...info,
        username: name.includes('1') ? 'alice' : 'bob',
        company: 'ACME_CORP',
        department: name.includes('1') ? '研发部' : '测试部',
        role: name.includes('1') ? 'developer' : 'qa',
        email: name.includes('1') ? 'alice@acmecorp.com' : 'bob@acmecorp.com',
        os: 'Ubuntu 20.04 LTS',
        kernel: '5.4.0-42-generic',
        openPorts: ['22', '80', '443'],
        services: ['SSH', 'HTTP', 'HTTPS']
      }
    } else if (name.includes('服务器') || type === 'server') {
      return {
        ...info,
        username: 'admin',
        company: 'ACME_CORP',
        department: 'IT运维',
        role: '系统管理员',
        email: 'admin@acmecorp.com',
        os: 'Ubuntu Server 20.04 LTS',
        kernel: '5.4.0-42-generic',
        openPorts: ['22', '80', '443', '3306'],
        services: ['SSH', 'HTTP', 'HTTPS', 'MySQL']
      }
    } else if (name.includes('数据库') || type === 'database') {
      return {
        ...info,
        username: 'dbadmin',
        company: 'ACME_CORP',
        department: '数据库管理',
        role: '数据库管理员',
        email: 'dbadmin@acmecorp.com',
        os: 'CentOS 8',
        kernel: '4.18.0-240',
        openPorts: ['22', '3306', '5432'],
        services: ['SSH', 'MySQL', 'PostgreSQL']
      }
    } else if (name.includes('防火墙') || type === 'firewall') {
      return {
        ...info,
        username: 'fwadmin',
        company: 'ACME_CORP',
        department: '网络安全',
        role: '防火墙管理员',
        email: 'fwadmin@acmecorp.com',
        os: 'CentOS 8',
        kernel: '4.18.0-240',
        openPorts: ['22'],
        services: ['SSH', 'Firewall']
      }
    } else if (name.includes('DNS') || type === 'dns') {
      return {
        ...info,
        username: 'dnsadmin',
        company: 'ACME_CORP',
        department: '网络运维',
        role: 'DNS服务器管理员',
        email: 'dnsadmin@acmecorp.com',
        os: 'Ubuntu 20.04 LTS',
        kernel: '5.4.0-42-generic',
        openPorts: ['22', '53'],
        services: ['SSH', 'DNS']
      }
    } else if (name.includes('邮件') || type === 'mail') {
      return {
        ...info,
        username: 'mailadmin',
        company: 'ACME_CORP',
        department: 'IT运维',
        role: '邮件服务器管理员',
        email: 'mailadmin@acmecorp.com',
        os: 'Ubuntu 20.04 LTS',
        kernel: '5.4.0-42-generic',
        openPorts: ['22', '25', '143', '587'],
        services: ['SSH', 'SMTP', 'IMAP', 'Submission']
      }
    } else if (name.includes('Web') || type === 'web') {
      return {
        ...info,
        username: 'webadmin',
        company: 'ACME_CORP',
        department: 'IT运维',
        role: 'Web服务器管理员',
        email: 'webadmin@acmecorp.com',
        os: 'Ubuntu 20.04 LTS',
        kernel: '5.4.0-42-generic',
        openPorts: ['22', '80', '443'],
        services: ['SSH', 'HTTP', 'HTTPS']
      }
    } else if (name.includes('文件') || type === 'file') {
      return {
        ...info,
        username: 'fileadmin',
        company: 'ACME_CORP',
        department: 'IT运维',
        role: '文件服务器管理员',
        email: 'fileadmin@acmecorp.com',
        os: 'Ubuntu 20.04 LTS',
        kernel: '5.4.0-42-generic',
        openPorts: ['22', '21', '445'],
        services: ['SSH', 'FTP', 'SMB']
      }
    } else if (name.includes('VPN') || type === 'vpn') {
      return {
        ...info,
        username: 'vpnadmin',
        company: 'ACME_CORP',
        department: '网络安全',
        role: 'VPN管理员',
        email: 'vpnadmin@acmecorp.com',
        os: 'Ubuntu 20.04 LTS',
        kernel: '5.4.0-42-generic',
        openPorts: ['22', '1194', '443'],
        services: ['SSH', 'OpenVPN', 'HTTPS']
      }
    } else {
      // 默认信息
      return {
        ...info,
        username: 'user',
        company: 'ACME_CORP',
        department: '未知',
        role: '未知',
        email: 'user@acmecorp.com',
        os: 'Linux',
        kernel: '5.x',
        openPorts: ['22'],
        services: ['SSH']
      }
    }
  }
  
  /**
   * 生成默认的主机信息
   * @private
   * @param {Object} host - 主机对象
   * @returns {Object} - 返回默认的主机信息
   */
  static _generateDefaultHostInfo(host) {
    const { deviceData } = host
    
    return {
      name: deviceData?.name || '未知',
      ip: deviceData?.ip || '0.0.0.0',
      mac: deviceData?.mac || '00:00:00:00:00:00',
      status: deviceData?.status || 'unknown',
      username: 'unknown',
      company: 'ACME_CORP',
      department: '未知',
      role: '未知',
      email: 'unknown@acmecorp.com',
      os: '未知',
      kernel: '未知',
      openPorts: [],
      services: []
    }
  }
}

export default HostInfoService