// 在onMounted中添加事件监听器
onMounted(async () => {
  await loadFabric()
  initializeTopology()
  
  // 添加攻击进度和完成事件监听
  window.addEventListener('attack-progress', handleAttackProgress)
  window.addEventListener('attack-completed', handleAttackCompleted)
})

// 在onUnmounted中移除事件监听器
onUnmounted(() => {
  // 移除事件监听器
  window.removeEventListener('attack-progress', handleAttackProgress)
  window.removeEventListener('attack-completed', handleAttackCompleted)
})

// 处理攻击进度更新事件
function handleAttackProgress(event) {
  const { taskId, status } = event.detail
  
  // 更新当前任务状态
  if (taskId === currentAttackTaskId.value) {
    currentAttackTaskStatus.value = status
    
    // 记录日志
    if (status.logs && status.logs.length > 0) {
      const latestLog = status.logs[status.logs.length - 1]
      logMessage(latestLog.level, latestLog.source, latestLog.message)
    }
    
    // 根据阶段更新可视化
    updateAttackVisualizationByPhase(status.phase, status.progress)
  }
}

// 处理攻击完成事件
function handleAttackCompleted(event) {
  const { success, taskId, result, error } = event.detail
  
  if (taskId === currentAttackTaskId.value) {
    if (success) {
      logSuccess('攻击智能体', '攻击任务已完成')
      
      // 解析结果
      if (result && result.final_output) {
        logInfo('攻击结果', result.final_output)
      }
    } else {
      logError('攻击智能体', `攻击任务失败: ${error}`)
    }
  }
}

// 根据攻击阶段更新可视化
function updateAttackVisualizationByPhase(phase, progress) {
  // 获取攻击者和目标
  const attacker = selectedAttacker.value
  const target = Object.values(topology.devices).find(d => 
    d !== attacker && d.deviceData.name !== '攻击节点'
  )
  
  if (!attacker || !target || !attackVisualization) return
  
  // 根据阶段显示不同的动画
  switch (phase) {
    case 'reconnaissance':
      if (progress <= 5) {
        attackVisualization.createThinkingAnimation(attacker, 3)
      } else if (progress <= 10) {
        attackVisualization.createScanningAnimation(attacker, target, 3)
      }
      break
    case 'weaponization':
      if (progress <= 20) {
        attackVisualization.createThinkingAnimation(attacker, 3)
      } else if (progress <= 25) {
        attackVisualization.createWritingAnimation(attacker, 3)
      }
      break
    case 'delivery':
      if (progress <= 35) {
        attackVisualization.createSendEmailAnimation(attacker, target, 3)
      } else if (progress <= 45) {
        attackVisualization.createThinkingAnimation(target, 3)
      }
      break
    case 'exploitation':
      if (progress <= 60) {
        // 更新目标状态为被瞄准
        updateNodeStatus(target, 'targeted')
      }
      break
    case 'installation':
      if (progress <= 75) {
        // 更新目标状态为已攻陷
        updateNodeStatus(target, 'compromised')
      }
      break
    case 'command_and_control':
      if (progress <= 85) {
        attackVisualization.createDataTheftAnimation(target, attacker, 3)
      }
      break
    case 'actions_on_objectives':
      if (progress >= 95) {
        attackVisualization.createSuccessAnimation(attacker, 3)
      }
      break
  }
}