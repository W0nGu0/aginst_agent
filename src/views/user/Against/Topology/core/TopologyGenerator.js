/**
 * 拓扑生成器类
 * 负责创建各种预设拓扑图
 */
class TopologyGenerator {
  /**
   * 创建公司拓扑图
   * @param {NetworkTopology} topology - 网络拓扑实例
   * @param {boolean} isTransparent - 是否使用透明效果（用于表示未启动的设备）
   * @returns {Promise<Object>} - 返回创建的设备对象
   */
  static async createCompanyTopology(topology, isTransparent = false) {
    // 防止重复生成
    topology.clear();

    // 设置透明度
    const opacity = isTransparent ? 0.6 : 1;

    // 创建防火墙设备
    const internalFW = await topology.createDevice('firewall', {
      left: 400,
      top: 300,
      deviceData: {
        name: '内部防火墙',
        ip: '192.168.200.254',
        description: '内部网络防火墙'
      }
    });
    internalFW.set({ opacity });

    const externalFW = await topology.createDevice('firewall', {
      left: 650,
      top: 300,
      deviceData: {
        name: '外部防火墙',
        ip: '199.203.100.2',
        description: 'DMZ区域防火墙'
      }
    });
    externalFW.set({ opacity });

    // 连接两个防火墙，并添加网络信息
    topology.addConnection(internalFW, externalFW, 'ethernet', {
      subnet: '192.168.254.0/29',
      firewallIP: '192.168.254.3',
      deviceIP: '192.168.254.2'
    });

    // 创建服务器段设备
    const sqlServer = await topology.createDevice('db', {
      left: 200,
      top: 50,
      deviceData: {
        name: '数据库',
        ip: '192.168.200.23',
        description: 'MySQL数据库服务器'
      }
    });
    sqlServer.set({ opacity });

    const fileServer = await topology.createDevice('file', {
      left: 200,
      top: 175,
      deviceData: {
        name: '文件服务器',
        ip: '192.168.200.6',
        description: '企业文件存储服务器'
      }
    });
    fileServer.set({ opacity });

    // 创建服务器
    const syslogServer = await topology.createDevice('server', {
      left: 200,
      top: 300,
      deviceData: {
        name: '服务器',
        ip: '192.168.66.20',
        description: '服务器'
      }
    });
    syslogServer.set({ opacity });

    // 创建用户段设备
    const workstation1 = await topology.createDevice('pc', {
      left: 200,
      top: 425,
      deviceData: {
        name: 'PC-1',
        ip: '192.168.100.9',
        description: '开发人员工作站'
      }
    });
    workstation1.set({ opacity });

    const workstation2 = await topology.createDevice('pc', {
      left: 200,
      top: 550,
      deviceData: {
        name: 'PC-2',
        ip: '192.168.100.34',
        description: 'QA测试工作站'
      }
    });
    workstation2.set({ opacity });

    // 创建 VPN 设备
    const vpnServer = await topology.createDevice('vpn', {
      left: 400,
      top: 150,
      deviceData: {
        name: 'VPN网关',
        ip: '192.168.110.5',
        description: '远程访问VPN服务器'
      }
    });
    vpnServer.set({ opacity });

    // 创建数据库段设备
    const pgdbServer = await topology.createDevice('db', {
      left: 400,
      top: 450,
      deviceData: {
        name: 'PostgreSQL',
        ip: '192.168.214.10',
        description: 'PostgreSQL数据库服务器'
      }
    });
    pgdbServer.set({ opacity });

    // 连接内部设备到内部防火墙，并添加网络信息
    topology.addConnection(internalFW, sqlServer, 'ethernet', {
      subnet: '192.168.200.0/24',
      firewallIP: '192.168.200.254',
      deviceIP: '192.168.200.23'
    });
    
    topology.addConnection(internalFW, fileServer, 'ethernet', {
      subnet: '192.168.200.0/24',
      firewallIP: '192.168.200.254',
      deviceIP: '192.168.200.6'
    });
    
    topology.addConnection(internalFW, syslogServer, 'ethernet', {
      subnet: '192.168.66.0/24',
      firewallIP: '192.168.66.254',
      deviceIP: '192.168.66.20'
    });
    
    topology.addConnection(internalFW, workstation1, 'ethernet', {
      subnet: '192.168.100.0/24',
      firewallIP: '192.168.100.254',
      deviceIP: '192.168.100.9'
    });
    
    topology.addConnection(internalFW, workstation2, 'ethernet', {
      subnet: '192.168.100.0/24',
      firewallIP: '192.168.100.254',
      deviceIP: '192.168.100.34'
    });
    
    topology.addConnection(internalFW, vpnServer, 'ethernet', {
      subnet: '192.168.110.0/24',
      firewallIP: '192.168.110.254',
      deviceIP: '192.168.110.5'
    });
    
    topology.addConnection(internalFW, pgdbServer, 'ethernet', {
      subnet: '192.168.214.0/24',
      firewallIP: '192.168.214.254',
      deviceIP: '192.168.214.10'
    });

    // 创建 DMZ 段设备
    const wpServer = await topology.createDevice('web', {
      left: 600,
      top: 150,
      deviceData: {
        name: 'WordPress网站',
        ip: '172.16.100.10',
        description: '企业WordPress网站'
      }
    });
    wpServer.set({ opacity });

    const apacheServer = await topology.createDevice('web', {
      left: 750,
      top: 150,
      deviceData: {
        name: 'Apache_web服务器',
        ip: '172.16.100.11',
        description: 'Apache Web服务器'
      }
    });
    apacheServer.set({ opacity });

    const dnsServer = await topology.createDevice('dns', {
      left: 600,
      top: 450,
      deviceData: {
        name: 'DNS服务器',
        ip: '172.16.100.53',
        description: '域名解析服务器'
      }
    });
    dnsServer.set({ opacity });

    const mailServer = await topology.createDevice('mail', {
      left: 750,
      top: 450,
      deviceData: {
        name: '邮件服务器',
        ip: '172.16.100.25',
        description: '企业邮件中继服务器'
      }
    });
    mailServer.set({ opacity });

    // 创建攻击者
    const attacker = await topology.createDevice('pc', {
      left: 1000,
      top: 250,
      deviceData: {
        name: '攻击者',
        ip: '199.203.100.10',
        description: '外部攻击者'
      }
    });
    attacker.set({ opacity });

    const attackNode = await topology.createDevice('pc', {
      left: 1000,
      top: 350,
      deviceData: {
        name: '攻击节点',
        ip: '199.203.100.11',
        description: '攻击跳板机'
      }
    });
    attackNode.set({ opacity });

    // 连接 DMZ 设备到外部防火墙，并添加网络信息
    topology.addConnection(externalFW, wpServer, 'ethernet', {
      subnet: '172.16.100.0/24',
      firewallIP: '172.16.100.254',
      deviceIP: '172.16.100.10'
    });
    
    topology.addConnection(externalFW, apacheServer, 'ethernet', {
      subnet: '172.16.100.0/24',
      firewallIP: '172.16.100.254',
      deviceIP: '172.16.100.11'
    });
    
    topology.addConnection(externalFW, dnsServer, 'ethernet', {
      subnet: '172.16.100.0/24',
      firewallIP: '172.16.100.254',
      deviceIP: '172.16.100.53'
    });
    
    topology.addConnection(externalFW, mailServer, 'ethernet', {
      subnet: '172.16.100.0/24',
      firewallIP: '172.16.100.254',
      deviceIP: '172.16.100.25'
    });

    // 直接将攻击者和攻击节点连接到外部防火墙，并添加网络信息
    topology.addConnection(externalFW, attacker, 'ethernet', {
      subnet: '199.203.100.0/24',
      firewallIP: '199.203.100.2',
      deviceIP: '199.203.100.10'
    });
    
    topology.addConnection(externalFW, attackNode, 'ethernet', {
      subnet: '199.203.100.0/24',
      firewallIP: '199.203.100.2',
      deviceIP: '199.203.100.11'
    });

    return {
      internalFW, externalFW, sqlServer, fileServer, syslogServer, workstation1, workstation2,
      vpnServer, pgdbServer, wpServer, apacheServer, dnsServer, mailServer,
      attacker, attackNode
    };
  }

  /**
   * 根据容器信息更新设备状态
   * @param {NetworkTopology} topology - 网络拓扑实例
   * @param {Object} containerInfo - 容器信息
   */
  static updateDevicesWithContainerInfo(topology, containerInfo) {
    if (!containerInfo) return;

    console.log('更新设备信息:', containerInfo);

    // 手动添加缺失的容器（已退出的容器）
    const missingContainers = [
      { name: 'vpn', status: 'exited', error: 'Container exited with code 1' },
      { name: 'cnt-dmz-fw', status: 'exited', error: 'Container exited with code 1' },
      { name: 'cnt-fw', status: 'exited', error: 'Container exited with code 1' },
      { name: 'cnt-dmz-dns', status: 'exited', error: 'Container exited with code 1' }
    ];

    // 将缺失的容器添加到failed_services中
    if (!containerInfo.failed_services) {
      containerInfo.failed_services = [];
    }

    missingContainers.forEach(container => {
      if (!containerInfo.failed_services.find(s => s.name === container.name)) {
        containerInfo.failed_services.push(container);
      }
    });

    // 遍历所有设备，更新状态
    for (const [id, device] of Object.entries(topology.devices)) {
      const deviceName = device.deviceData.name;

      // 设备名称到容器名称的映射
      const deviceToContainerMap = {
        '内部防火墙': 'cnt-fw',
        '外部防火墙': 'cnt-dmz-fw',
        '数据库': 'cnt-sql',
        'PostgreSQL': 'cnt-db',
        '文件服务器': 'cnt-files',
        '服务器': 'cnt-syslog',
        'PC-1': 'ws-ubuntu-cnt1',
        'PC-2': 'ws-ubuntu-cnt2',
        'VPN网关': 'vpn',
        'WordPress网站': 'cnt-dmz-wp1',
        'Apache_web服务器': 'cnt-dmz-apache1',
        'DNS服务器': 'cnt-dmz-dns',
        '邮件服务器': 'cnt-dmz-mailrelay',
        '互联网': 'internet',
        '攻击者': 'attacker',
        '攻击节点': 'attack-node'
      };

      console.log(`处理设备: ${deviceName}`);

      // 打印所有运行中的容器名称，方便调试
      if (containerInfo.running_services) {
        console.log('运行中的容器:', containerInfo.running_services.map(s => s.name).join(', '));
      }

      // 打印所有失败的容器名称，方便调试
      if (containerInfo.failed_services) {
        console.log('失败的容器:', containerInfo.failed_services.map(s => s.name).join(', '));
      }

      // 获取映射的容器名称
      const containerName = deviceToContainerMap[deviceName] || deviceName;
      console.log(`设备名称: ${deviceName}, 映射到容器: ${containerName}`);

      // 查找对应的容器信息 - 先尝试精确匹配，再尝试部分匹配
      const runningContainer = containerInfo.running_services?.find(
        service => service.name === containerName
      ) || containerInfo.running_services?.find(
        service => containerName.includes(service.name) || service.name.includes(containerName)
      );

      const failedContainer = containerInfo.failed_services?.find(
        service => service.name === containerName
      ) || containerInfo.failed_services?.find(
        service => containerName.includes(service.name) || service.name.includes(containerName)
      );

      if (runningContainer) {
        // 更新运行中的设备
        device.deviceData.status = 'running';
        device.deviceData.containerId = runningContainer.id;
        device.deviceData.containerIp = runningContainer.ip || device.deviceData.ip;

        // 更新设备标签，对于防火墙只显示名称，其他设备显示IP
        if (device.deviceType === 'firewall') {
          topology._updateLabel(device, device.deviceData.name);
        } else {
          topology._updateLabel(device, `${device.deviceData.name}\n${device.deviceData.containerIp}`);
        }

        // 设置为不透明，表示正在运行
        device.set({ opacity: 1 });
      } else if (failedContainer) {
        // 更新失败的设备
        device.deviceData.status = 'failed';
        device.deviceData.error = failedContainer.error;

        // 更新设备标签，显示错误
        topology._updateLabel(device, `${device.deviceData.name}\n[失败]`);

        // 设置为半透明红色，表示失败
        device.set({
          opacity: 0.7,
          filters: [new fabric.Image.filters.BlendColor({
            color: '#FF0000',
            mode: 'tint',
            alpha: 0.3
          })]
        });
      } else {
        // 设备未运行
        device.deviceData.status = 'stopped';
        device.set({ opacity: 0.6 });
      }
    }

    // 刷新画布
    topology.canvas.requestRenderAll();
  }

  /**
   * 强制更新所有设备的视觉状态
   * @param {NetworkTopology} topology - 网络拓扑实例
   */
  static forceUpdateDevicesVisualState(topology) {
    if (!topology) return;

    console.log('强制更新所有设备的视觉状态');

    // 遍历所有设备，根据状态更新视觉效果
    for (const [id, device] of Object.entries(topology.devices)) {
      const status = device.deviceData.status || 'stopped';

      console.log(`设备 ${device.deviceData.name} 状态: ${status}`);

      if (status === 'running') {
        // 运行中的设备 - 完全不透明
        device.set({
          opacity: 1,
          // 移除任何滤镜
          filters: []
        });

        // 确保标签显示IP（对于防火墙只显示名称）
        if (device.deviceType === 'firewall') {
          topology._updateLabel(device, device.deviceData.name);
        } else if (device.deviceData.containerIp) {
          topology._updateLabel(device, `${device.deviceData.name}\n${device.deviceData.containerIp}`);
        }
      } else if (status === 'failed') {
        // 失败的设备 - 半透明红色
        device.set({
          opacity: 0.7,
          filters: [new fabric.Image.filters.BlendColor({
            color: '#FF0000',
            mode: 'tint',
            alpha: 0.3
          })]
        });

        // 确保标签显示失败
        topology._updateLabel(device, `${device.deviceData.name}\n[失败]`);
      } else {
        // 未运行的设备 - 半透明
        device.set({
          opacity: 0.6,
          // 移除任何滤镜
          filters: []
        });

        // 恢复原始标签
        topology._updateLabel(device, device.deviceData.name);
      }

      // 应用滤镜
      if (device.applyFilters) {
        device.applyFilters();
      }
    }

    // 刷新画布
    topology.canvas.requestRenderAll();
  }
}

export default TopologyGenerator;