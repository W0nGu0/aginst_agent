/**
 * 场景数据服务 - 处理apt-ready.yml场景数据的解析和转换
 */

export class ScenarioDataService {
  constructor() {
    this.scenarioAgentUrl = '/api/scenario'
  }

  /**
   * 获取APT医疗场景的拓扑数据
   */
  async getAptMedicalScenario() {
    try {
      const response = await fetch(`${this.scenarioAgentUrl}/parse_apt_scenario`)
      const result = await response.json()
      
      if (result.status === 'success' && result.data.topology) {
        return this.convertToTopologyFormat(result.data.topology)
      } else {
        throw new Error(result.message || '获取场景数据失败')
      }
    } catch (error) {
      console.error('获取APT医疗场景失败:', error)
      // 返回模拟数据作为备选
      return this.getMockAptScenario()
    }
  }

  /**
   * 将场景智能体返回的数据转换为前端拓扑图格式
   */
  convertToTopologyFormat(scenarioTopology) {
    const topology = {
      nodes: [],
      connections: [],
      networks: [],
      metadata: {
        scenario: 'apt-medical',
        description: 'APT医疗场景 - 高级持续威胁攻击医疗机构',
        nodeCount: scenarioTopology.nodes?.length || 0,
        networkCount: scenarioTopology.networks?.length || 0
      }
    }

    // 转换网络数据
    if (scenarioTopology.networks) {
      topology.networks = scenarioTopology.networks.map(network => ({
        id: network.id,
        name: network.name || network.id,
        subnet: network.subnet,
        type: network.type || 'network_segment',
        color: this.getNetworkColor(network.id)
      }))
    }

    // 转换节点数据
    if (scenarioTopology.nodes) {
      topology.nodes = scenarioTopology.nodes.map(node => ({
        id: node.id,
        name: node.name || node.id,
        type: node.type,
        x: this.calculateNodePosition(node, 'x'),
        y: this.calculateNodePosition(node, 'y'),
        networks: node.networks || [],
        ipAddresses: node.ip_addresses || {},
        ports: node.ports || [],
        status: node.status || 'virtual', // virtual, starting, running, stopped
        environment: node.environment || [],
        labels: node.labels || [],
        // 前端渲染属性
        fill: this.getNodeColor(node.type),
        stroke: this.getNodeStrokeColor(node.status),
        strokeWidth: node.status === 'virtual' ? 2 : 3,
        opacity: node.status === 'virtual' ? 0.5 : 1.0,
        strokeDashArray: node.status === 'virtual' ? [5, 5] : [],
        // 图标和显示
        icon: this.getNodeIcon(node.type),
        displayName: this.getNodeDisplayName(node)
      }))
    }

    // 转换连接数据
    if (scenarioTopology.connections) {
      topology.connections = scenarioTopology.connections.map(conn => ({
        id: conn.id || `${conn.source}-${conn.target}`,
        source: conn.source,
        target: conn.target,
        network: conn.network,
        type: conn.type || 'ethernet',
        // 前端渲染属性
        stroke: this.getConnectionColor(conn.network),
        strokeWidth: 2,
        strokeDashArray: conn.type === 'wireless' ? [3, 3] : [],
        opacity: 0.7
      }))
    }

    return topology
  }

  /**
   * 计算节点位置 - 基于网络分组和节点类型
   */
  calculateNodePosition(node, axis) {
    const basePositions = {
      // 网络分组位置
      internet: { x: 100, y: 100 },
      dmz_segment: { x: 300, y: 200 },
      user_segment: { x: 500, y: 300 },
      server_segment: { x: 700, y: 200 },
      db_segment: { x: 900, y: 300 },
      medical_segment: { x: 900, y: 100 },
      siem_segment: { x: 700, y: 400 }
    }

    // 根据节点所在的主要网络确定基础位置
    const primaryNetwork = node.networks?.[0] || 'default'
    const basePos = basePositions[primaryNetwork] || { x: 400, y: 250 }

    // 根据节点类型进行微调
    const typeOffsets = {
      firewall: { x: 0, y: -50 },
      attacker: { x: -50, y: 0 },
      workstation: { x: 50, y: 50 },
      database: { x: 0, y: 50 },
      web_server: { x: -50, y: 0 },
      dns_server: { x: 50, y: -50 },
      file_server: { x: 0, y: 0 },
      medical_server: { x: 50, y: 0 }
    }

    const offset = typeOffsets[node.type] || { x: 0, y: 0 }
    
    // 添加一些随机偏移避免重叠
    const randomOffset = (Math.random() - 0.5) * 30

    if (axis === 'x') {
      return basePos.x + offset.x + randomOffset
    } else {
      return basePos.y + offset.y + randomOffset
    }
  }

  /**
   * 获取网络颜色
   */
  getNetworkColor(networkId) {
    const colors = {
      internet: '#ff6b6b',
      dmz_segment: '#4ecdc4',
      user_segment: '#45b7d1',
      server_segment: '#f9ca24',
      db_segment: '#6c5ce7',
      medical_segment: '#a29bfe',
      siem_segment: '#fd79a8'
    }
    return colors[networkId] || '#95a5a6'
  }

  /**
   * 获取节点颜色
   */
  getNodeColor(nodeType) {
    const colors = {
      firewall: '#e74c3c',
      attacker: '#2c3e50',
      workstation: '#3498db',
      database: '#9b59b6',
      web_server: '#e67e22',
      dns_server: '#27ae60',
      file_server: '#f39c12',
      log_server: '#34495e',
      medical_server: '#e91e63',
      update_server: '#16a085',
      vpn_server: '#8e44ad'
    }
    return colors[nodeType] || '#95a5a6'
  }

  /**
   * 获取节点边框颜色（基于状态）
   */
  getNodeStrokeColor(status) {
    const colors = {
      virtual: '#bdc3c7',
      starting: '#f39c12',
      running: '#27ae60',
      stopped: '#e74c3c'
    }
    return colors[status] || '#95a5a6'
  }

  /**
   * 获取连接颜色
   */
  getConnectionColor(network) {
    return this.getNetworkColor(network)
  }

  /**
   * 获取节点图标
   */
  getNodeIcon(nodeType) {
    const icons = {
      firewall: '/icons/firewall.svg',
      attacker: '/icons/attacker.svg',
      workstation: '/icons/workstation.svg',
      database: '/icons/database.svg',
      web_server: '/icons/web-server.svg',
      dns_server: '/icons/dns.svg',
      file_server: '/icons/file-server.svg',
      log_server: '/icons/log-server.svg',
      medical_server: '/icons/medical.svg',
      update_server: '/icons/update.svg',
      vpn_server: '/icons/vpn.svg'
    }
    return icons[nodeType] || '/icons/server.svg'
  }

  /**
   * 获取节点显示名称
   */
  getNodeDisplayName(node) {
    const typeNames = {
      firewall: '防火墙',
      attacker: '攻击者',
      workstation: '工作站',
      database: '数据库',
      web_server: 'Web服务器',
      dns_server: 'DNS服务器',
      file_server: '文件服务器',
      log_server: '日志服务器',
      medical_server: '医疗服务器',
      update_server: '更新服务器',
      vpn_server: 'VPN服务器'
    }
    
    const typeName = typeNames[node.type] || '服务器'
    return `${typeName}\n(${node.name})`
  }

  /**
   * 模拟APT场景数据（备选方案）
   */
  getMockAptScenario() {
    return {
      nodes: [
        {
          id: 'attacker',
          name: 'attacker',
          type: 'attacker',
          x: 100,
          y: 100,
          networks: ['internet'],
          status: 'virtual',
          fill: '#2c3e50',
          stroke: '#bdc3c7',
          opacity: 0.5,
          strokeDashArray: [5, 5],
          displayName: '攻击者\n(attacker)'
        },
        {
          id: 'border-firewall',
          name: 'border-firewall',
          type: 'firewall',
          x: 300,
          y: 150,
          networks: ['internet', 'dmz_segment'],
          status: 'virtual',
          fill: '#e74c3c',
          stroke: '#bdc3c7',
          opacity: 0.5,
          strokeDashArray: [5, 5],
          displayName: '边界防火墙\n(border-firewall)'
        },
        {
          id: 'ws-ubuntu-1',
          name: 'ws-ubuntu-1',
          type: 'workstation',
          x: 500,
          y: 300,
          networks: ['user_segment'],
          status: 'virtual',
          fill: '#3498db',
          stroke: '#bdc3c7',
          opacity: 0.5,
          strokeDashArray: [5, 5],
          displayName: '工作站\n(Alice)'
        }
      ],
      connections: [
        {
          id: 'attacker-border-firewall',
          source: 'attacker',
          target: 'border-firewall',
          network: 'internet',
          stroke: '#ff6b6b',
          opacity: 0.7
        }
      ],
      networks: [
        {
          id: 'internet',
          name: 'Internet',
          subnet: '199.203.100.0/24',
          color: '#ff6b6b'
        },
        {
          id: 'dmz_segment',
          name: 'DMZ',
          subnet: '172.16.100.0/24',
          color: '#4ecdc4'
        }
      ],
      metadata: {
        scenario: 'apt-medical',
        description: 'APT医疗场景（模拟数据）',
        nodeCount: 3,
        networkCount: 2
      }
    }
  }
}

export default new ScenarioDataService()
