/**
 * 攻击阶段动画处理器
 * 根据后端日志中的攻击信息触发对应的可视化动画
 */

// 侦察阶段动画处理
export function handleReconnaissanceAnimation(technique, sourceNode, targetNode, status, progress, attackVisualization) {
  console.log('🔍 侦察阶段动画:', { technique, status, progress })
  
  if (!attackVisualization) return
  
  switch (technique) {
    case 'port_scan':
    case '端口扫描':
    case '网络扫描':
      if (targetNode) {
        // 连续扫描动画
        attackVisualization.createScanningPulse(targetNode)
        
        // 如果是开始状态，启动连续扫描
        if (status === 'starting' || status === 'in_progress') {
          attackVisualization.startContinuousScanning([targetNode], `recon-${targetNode.id}`)
        } else if (status === 'completed') {
          attackVisualization.stopContinuousScanning(`recon-${targetNode.id}`)
        }
      }
      break
      
    case 'vulnerability_scan':
    case '漏洞扫描':
      if (targetNode) {
        attackVisualization.createScanningPulse(targetNode, { pulseColor: '#f59e0b' })
      }
      break
      
    case 'info_gathering':
    case '信息收集':
    case '情报收集':
      if (sourceNode) {
        attackVisualization.createThinkingAnimation(sourceNode, 2)
      }
      break
      
    default:
      // 默认扫描动画
      if (targetNode) {
        attackVisualization.createScanningPulse(targetNode)
      }
  }
}

// 武器化阶段动画处理
export function handleWeaponizationAnimation(technique, sourceNode, targetNode, status, progress, attackVisualization) {
  console.log('🔧 武器化阶段动画:', { technique, status, progress })
  
  if (!attackVisualization) return
  
  switch (technique) {
    case 'phishing_email':
    case '钓鱼邮件':
    case '钓鱼邮件生成':
      if (sourceNode) {
        // 显示加载动画表示正在生成
        attackVisualization.createThinkingAnimation(sourceNode, 3)
      }
      break
      
    case 'malware_generation':
    case '恶意软件生成':
      if (sourceNode) {
        attackVisualization.createThinkingAnimation(sourceNode, 4)
      }
      break
      
    case 'exploit_creation':
    case '漏洞利用创建':
      if (sourceNode) {
        attackVisualization.createThinkingAnimation(sourceNode, 3)
      }
      break
      
    default:
      if (sourceNode) {
        attackVisualization.createThinkingAnimation(sourceNode, 2)
      }
  }
}

// 投递阶段动画处理
export function handleDeliveryAnimation(technique, sourceNode, targetNode, status, progress, attackVisualization) {
  console.log('📧 投递阶段动画:', { technique, status, progress })
  
  if (!attackVisualization) return
  
  switch (technique) {
    case 'email_delivery':
    case '邮件投递':
    case '邮件发送':
      if (sourceNode && targetNode) {
        // 创建攻击路径动画
        attackVisualization.createAttackPath(sourceNode, targetNode, {
          color: '#3b82f6',
          dashArray: [5, 5]
        })
      }
      break
      
    case 'web_delivery':
    case 'Web投递':
      if (sourceNode && targetNode) {
        attackVisualization.createAttackPath(sourceNode, targetNode, {
          color: '#10b981'
        })
      }
      break
      
    case 'usb_delivery':
    case 'USB投递':
      if (targetNode) {
        // 显示特殊的USB插入动画
        attackVisualization.createThinkingAnimation(targetNode, 2)
      }
      break
      
    default:
      if (sourceNode && targetNode) {
        attackVisualization.createAttackPath(sourceNode, targetNode)
      }
  }
}

// 利用阶段动画处理
export function handleExploitationAnimation(technique, sourceNode, targetNode, status, progress, attackVisualization) {
  console.log('💥 利用阶段动画:', { technique, status, progress })
  
  if (!attackVisualization) return
  
  switch (technique) {
    case 'buffer_overflow':
    case '缓冲区溢出':
      if (targetNode) {
        attackVisualization.updateNodeStatus(targetNode, 'targeted')
        attackVisualization.createScanningPulse(targetNode, { pulseColor: '#dc2626' })
      }
      break
      
    case 'sql_injection':
    case 'SQL注入':
      if (targetNode) {
        attackVisualization.updateNodeStatus(targetNode, 'targeted')
        // 创建数据窃取动画
        if (sourceNode) {
          attackVisualization.createDataTheftAnimation(targetNode, sourceNode, 2)
        }
      }
      break
      
    case 'xss_attack':
    case 'XSS攻击':
      if (targetNode) {
        attackVisualization.updateNodeStatus(targetNode, 'targeted')
      }
      break
      
    case 'credential_theft':
    case '凭据窃取':
      if (sourceNode && targetNode) {
        attackVisualization.createDataTheftAnimation(targetNode, sourceNode, 1.5)
      }
      break
      
    default:
      if (targetNode) {
        attackVisualization.updateNodeStatus(targetNode, 'targeted')
        if (sourceNode) {
          attackVisualization.createAttackPath(sourceNode, targetNode, {
            color: '#dc2626'
          })
        }
      }
  }
}

// 安装阶段动画处理
export function handleInstallationAnimation(technique, sourceNode, targetNode, status, progress, attackVisualization) {
  console.log('📥 安装阶段动画:', { technique, status, progress })
  
  if (!attackVisualization) return
  
  switch (technique) {
    case 'backdoor_install':
    case '后门安装':
      if (targetNode) {
        attackVisualization.updateNodeStatus(targetNode, 'compromised')
        attackVisualization.createThinkingAnimation(targetNode, 3)
      }
      break
      
    case 'persistence_mechanism':
    case '持久化机制':
      if (targetNode) {
        attackVisualization.updateNodeStatus(targetNode, 'compromised')
      }
      break
      
    case 'privilege_escalation':
    case '权限提升':
      if (targetNode) {
        attackVisualization.updateNodeStatus(targetNode, 'compromised')
        attackVisualization.createScanningPulse(targetNode, { pulseColor: '#dc2626' })
      }
      break
      
    default:
      if (targetNode) {
        attackVisualization.updateNodeStatus(targetNode, 'compromised')
      }
  }
}

// 命令控制阶段动画处理
export function handleCommandControlAnimation(technique, sourceNode, targetNode, status, progress, attackVisualization) {
  console.log('🎮 命令控制阶段动画:', { technique, status, progress })
  
  if (!attackVisualization) return
  
  switch (technique) {
    case 'c2_communication':
    case 'C2通信':
      if (sourceNode && targetNode) {
        // 创建持续的通信动画
        attackVisualization.startNetworkTraffic([sourceNode, targetNode], `c2-${targetNode.id}`)
      }
      break
      
    case 'remote_access':
    case '远程访问':
      if (sourceNode && targetNode) {
        attackVisualization.createAttackPath(sourceNode, targetNode, {
          color: '#8b5cf6',
          dashArray: [3, 3]
        })
      }
      break
      
    case 'lateral_movement':
    case '横向移动':
      if (sourceNode && targetNode) {
        attackVisualization.createAttackPath(sourceNode, targetNode, {
          color: '#f59e0b'
        })
      }
      break
      
    default:
      if (sourceNode && targetNode) {
        attackVisualization.createAttackPath(sourceNode, targetNode, {
          color: '#8b5cf6'
        })
      }
  }
}

// 行动目标阶段动画处理
export function handleActionsAnimation(technique, sourceNode, targetNode, status, progress, attackVisualization) {
  console.log('🎯 行动目标阶段动画:', { technique, status, progress })
  
  if (!attackVisualization) return
  
  switch (technique) {
    case 'data_theft':
    case '数据窃取':
    case '数据泄露':
      if (sourceNode && targetNode) {
        attackVisualization.createDataTheftAnimation(targetNode, sourceNode, 4)
      }
      break
      
    case 'system_compromise':
    case '系统攻陷':
      if (targetNode) {
        attackVisualization.updateNodeStatus(targetNode, 'compromised')
        attackVisualization.createSuccessAnimation(targetNode, 2)
      }
      break
      
    case 'data_destruction':
    case '数据销毁':
      if (targetNode) {
        attackVisualization.createFailureAnimation(targetNode)
      }
      break
      
    case 'network_disruption':
    case '网络中断':
      if (targetNode) {
        attackVisualization.createFailureAnimation(targetNode)
      }
      break
      
    default:
      if (sourceNode && targetNode) {
        attackVisualization.createDataTheftAnimation(targetNode, sourceNode, 3)
      } else if (targetNode) {
        attackVisualization.createSuccessAnimation(targetNode, 2)
      }
  }
}

// 根据日志消息内容智能匹配动画
export function handleLogBasedAnimation(log, sourceNode, targetNode, attackVisualization) {
  if (!attackVisualization) return

  const message = log.message.toLowerCase()
  const source = log.source.toLowerCase()

  console.log('🎨 智能匹配动画:', {
    message: log.message,
    sourceNode: sourceNode?.deviceData?.name,
    targetNode: targetNode?.deviceData?.name
  })

  // 基于关键词的智能匹配
  if (message.includes('扫描') || message.includes('scan') || message.includes('nmap')) {
    if (targetNode) {
      console.log('  → 触发扫描动画')
      attackVisualization.createScanningPulse(targetNode)
    }
  } else if (message.includes('攻击') || message.includes('attack') || message.includes('exploit')) {
    if (sourceNode && targetNode) {
      console.log('  → 触发攻击路径动画')
      attackVisualization.createAttackPath(sourceNode, targetNode)
    }
  } else if (message.includes('分析') || message.includes('处理') || message.includes('生成') || message.includes('思考')) {
    if (sourceNode) {
      console.log('  → 触发加载动画')
      attackVisualization.createThinkingAnimation(sourceNode, 2)
    }
  } else if (message.includes('数据') || message.includes('窃取') || message.includes('传输') || message.includes('下载')) {
    if (sourceNode && targetNode) {
      console.log('  → 触发数据窃取动画')
      attackVisualization.createDataTheftAnimation(targetNode, sourceNode, 2)
    }
  } else if (message.includes('成功') || message.includes('完成') || message.includes('攻陷') || message.includes('获得')) {
    if (targetNode) {
      console.log('  → 触发成功动画')
      attackVisualization.createSuccessAnimation(targetNode, 1.5)
      attackVisualization.updateNodeStatus(targetNode, 'compromised')
    } else if (sourceNode) {
      attackVisualization.createSuccessAnimation(sourceNode, 1.5)
    }
  } else if (message.includes('失败') || message.includes('错误') || message.includes('阻止') || message.includes('拒绝')) {
    if (targetNode) {
      console.log('  → 触发失败动画')
      attackVisualization.createFailureAnimation(targetNode)
    } else if (sourceNode) {
      attackVisualization.createFailureAnimation(sourceNode)
    }
  } else if (message.includes('连接') || message.includes('建立') || message.includes('通信')) {
    if (sourceNode && targetNode) {
      console.log('  → 触发连接动画')
      attackVisualization.createAttackPath(sourceNode, targetNode, { color: '#8b5cf6' })
    }
  } else {
    // 默认动画
    if (sourceNode) {
      console.log('  → 触发默认思考动画')
      attackVisualization.createThinkingAnimation(sourceNode, 1)
    }
  }
}
