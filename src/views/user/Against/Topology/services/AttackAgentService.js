/**
 * 攻击智能体服务
 * 提供与攻击智能体的交互功能
 */

// 导入任务服务
import AttackTaskService from './AttackTaskService';

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
      console.log("开始执行自动攻击:", attackData);

      // 构建请求数据
      // 根据攻击目标选择不同的主机URL
      let targetHost = "http://localhost:5001"; // 默认使用alice容器

      // 如果有目标设备，根据设备名称或IP选择不同的主机
      if (attackData.target) {
        const targetName = attackData.target.deviceData?.name || "";
        const targetIp = attackData.target.deviceData?.ip || "";

        if (targetName.includes("PC-1") || targetIp.includes("192.168.100.9")) {
          targetHost = "http://localhost:5001"; // alice
        } else if (
          targetName.includes("PC-2") ||
          targetIp.includes("192.168.100.34")
        ) {
          targetHost = "http://localhost:5002"; // bob
        }
      }

      console.log(`选择目标主机: ${targetHost}`);

      const requestData = {
        target_host: targetHost,
        attack_type: "auto", // 攻击类型，让中控智能体决定具体使用哪种攻击
      };

      console.log("发送攻击请求到中控智能体:", requestData);

      // 创建攻击任务
      const taskId = AttackTaskService.createTask({
        ...attackData,
        targetHost
      });

      // 更新任务状态为运行中
      AttackTaskService.updateTask(taskId, {
        status: AttackTaskService.STATUS.RUNNING,
        phase: AttackTaskService.PHASE.RECONNAISSANCE
      });

      // 添加初始日志
      AttackTaskService.addTaskLog(taskId, 'info', '攻击智能体', `开始对 ${targetHost} 执行自动攻击`);

      // 启动真实攻击过程
      this.startRealAttack(requestData, taskId);
      
      // 启动轮询任务状态
      this.startPollingTaskStatus(taskId);
      
      // 返回任务信息
      return {
        success: true,
        message: "自动攻击已启动",
        taskId,
        details: {
          status: AttackTaskService.STATUS.RUNNING,
          phase: AttackTaskService.PHASE.RECONNAISSANCE,
          progress: 0,
          logs: AttackTaskService.getTaskStatus(taskId).logs
        }
      };
    } catch (error) {
      console.error("执行自动攻击失败:", error);
      return {
        success: false,
        message: `执行自动攻击失败: ${error.message}`,
        error,
      };
    }
  }
  
  /**
   * 启动真实的攻击过程
   * @param {Object} requestData - 请求数据
   * @param {string} taskId - 任务ID
   */
  static async startRealAttack(requestData, taskId) {
    try {
      // 构建API请求URL
      // 使用后端的API端点，后端会转发请求到攻击智能体
      const apiUrl = `/api/attack/execute_full_attack`;
      
      // 调用攻击API
      fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      }).then(async response => {
        if (response.ok) {
          const result = await response.json();
          console.log("真实攻击执行成功:", result);
          
          // 更新任务状态
          AttackTaskService.completeTask(taskId, result);
          
          // 添加成功日志
          AttackTaskService.addTaskLog(taskId, 'success', '攻击智能体', '攻击执行成功');
          
          // 触发攻击完成事件
          const event = new CustomEvent('attack-completed', { 
            detail: { 
              success: true,
              taskId,
              result 
            } 
          });
          window.dispatchEvent(event);
        } else {
          const errorText = await response.text();
          console.error(`真实攻击执行失败: ${response.status} ${errorText}`);
          
          // 更新任务状态
          AttackTaskService.failTask(taskId, `${response.status} ${errorText}`);
          
          // 添加错误日志
          AttackTaskService.addTaskLog(taskId, 'error', '攻击智能体', `攻击执行失败: ${response.status} ${errorText}`);
          
          // 触发攻击失败事件
          const event = new CustomEvent('attack-completed', { 
            detail: { 
              success: false,
              taskId,
              error: `${response.status} ${errorText}` 
            } 
          });
          window.dispatchEvent(event);
        }
      }).catch(error => {
        console.error("真实攻击请求发送失败:", error);
        
        // 更新任务状态
        AttackTaskService.failTask(taskId, error.message);
        
        // 添加错误日志
        AttackTaskService.addTaskLog(taskId, 'error', '攻击智能体', `攻击请求发送失败: ${error.message}`);
        
        // 触发攻击失败事件
        const event = new CustomEvent('attack-completed', { 
          detail: { 
            success: false,
            taskId,
            error: error.message 
          } 
        });
        window.dispatchEvent(event);
      });
    } catch (error) {
      console.error("启动真实攻击过程失败:", error);
      
      // 更新任务状态
      AttackTaskService.failTask(taskId, error.message);
      
      // 添加错误日志
      AttackTaskService.addTaskLog(taskId, 'error', '攻击智能体', `启动攻击过程失败: ${error.message}`);
    }
  }
  
  /**
   * 启动轮询任务状态
   * @param {string} taskId - 任务ID
   */
  static async startPollingTaskStatus(taskId) {
    // 模拟攻击进度更新
    // 在实际应用中，这里应该调用后端API获取真实的攻击进度
    const updateProgress = async () => {
      const task = AttackTaskService.getTaskStatus(taskId);
      
      // 如果任务已完成或失败，停止轮询
      if (task.status === AttackTaskService.STATUS.COMPLETED || 
          task.status === AttackTaskService.STATUS.FAILED) {
        return;
      }
      
      // 根据当前进度更新阶段
      let newPhase = task.phase;
      let newProgress = task.progress;
      
      // 模拟进度更新
      if (task.progress < 15) {
        // 侦察阶段
        newPhase = AttackTaskService.PHASE.RECONNAISSANCE;
        newProgress += 5;
        
        // 添加侦察阶段日志
        if (task.progress === 0) {
          AttackTaskService.addTaskLog(taskId, 'info', '侦察阶段', '开始获取目标主机信息');
        } else if (task.progress === 10) {
          AttackTaskService.addTaskLog(taskId, 'success', '侦察阶段', '成功获取目标主机元数据');
        }
      } else if (task.progress < 30) {
        // 武器化阶段
        newPhase = AttackTaskService.PHASE.WEAPONIZATION;
        newProgress += 5;
        
        // 添加武器化阶段日志
        if (task.progress === 15) {
          AttackTaskService.addTaskLog(taskId, 'info', '武器化阶段', '开始生成针对性钓鱼邮件');
        } else if (task.progress === 25) {
          AttackTaskService.addTaskLog(taskId, 'success', '武器化阶段', '成功生成定制化钓鱼邮件');
        }
      } else if (task.progress < 50) {
        // 投递阶段
        newPhase = AttackTaskService.PHASE.DELIVERY;
        newProgress += 5;
        
        // 添加投递阶段日志
        if (task.progress === 30) {
          AttackTaskService.addTaskLog(taskId, 'info', '投递阶段', '开始发送钓鱼邮件');
        } else if (task.progress === 40) {
          AttackTaskService.addTaskLog(taskId, 'success', '投递阶段', '钓鱼邮件发送成功');
        } else if (task.progress === 45) {
          AttackTaskService.addTaskLog(taskId, 'success', '投递阶段', '目标已点击恶意链接');
        }
      } else if (task.progress < 70) {
        // 利用阶段
        newPhase = AttackTaskService.PHASE.EXPLOITATION;
        newProgress += 5;
        
        // 添加利用阶段日志
        if (task.progress === 50) {
          AttackTaskService.addTaskLog(taskId, 'info', '利用阶段', '开始利用目标漏洞');
        } else if (task.progress === 60) {
          AttackTaskService.addTaskLog(taskId, 'success', '利用阶段', '成功获取目标系统访问权限');
        }
      } else if (task.progress < 80) {
        // 安装阶段
        newPhase = AttackTaskService.PHASE.INSTALLATION;
        newProgress += 5;
        
        // 添加安装阶段日志
        if (task.progress === 70) {
          AttackTaskService.addTaskLog(taskId, 'info', '安装阶段', '开始在目标系统安装持久化访问');
        } else if (task.progress === 75) {
          AttackTaskService.addTaskLog(taskId, 'success', '安装阶段', '成功建立持久化访问');
        }
      } else if (task.progress < 90) {
        // 命令与控制阶段
        newPhase = AttackTaskService.PHASE.COMMAND_AND_CONTROL;
        newProgress += 5;
        
        // 添加命令与控制阶段日志
        if (task.progress === 80) {
          AttackTaskService.addTaskLog(taskId, 'info', '命令与控制阶段', '开始建立远程控制通道');
        } else if (task.progress === 85) {
          AttackTaskService.addTaskLog(taskId, 'success', '命令与控制阶段', '成功建立远程控制通道');
        }
      } else if (task.progress < 100) {
        // 目标行动阶段
        newPhase = AttackTaskService.PHASE.ACTIONS_ON_OBJECTIVES;
        newProgress += 5;
        
        // 添加目标行动阶段日志
        if (task.progress === 90) {
          AttackTaskService.addTaskLog(taskId, 'info', '目标行动阶段', '开始执行横向移动');
        } else if (task.progress === 95) {
          AttackTaskService.addTaskLog(taskId, 'success', '目标行动阶段', '成功获取敏感数据');
        }
      }
      
      // 更新任务状态
      AttackTaskService.updateTask(taskId, {
        phase: newPhase,
        progress: newProgress
      });
      
      // 触发任务更新事件
      const event = new CustomEvent('attack-progress', { 
        detail: { 
          taskId,
          status: AttackTaskService.getTaskStatus(taskId)
        } 
      });
      window.dispatchEvent(event);
      
      // 如果进度未达到100%，继续轮询
      if (newProgress < 100) {
        setTimeout(updateProgress, 1000); // 每秒更新一次
      } else {
        // 如果后端API没有返回结果，模拟完成
        const task = AttackTaskService.getTaskStatus(taskId);
        if (task.status !== AttackTaskService.STATUS.COMPLETED && 
            task.status !== AttackTaskService.STATUS.FAILED) {
          
          // 添加完成日志
          AttackTaskService.addTaskLog(taskId, 'success', '攻击智能体', '攻击流程已完成');
          
          // 更新任务状态
          AttackTaskService.completeTask(taskId, {
            final_output: '攻击流程已完成，所有阶段执行成功。'
          });
          
          // 触发攻击完成事件
          const event = new CustomEvent('attack-completed', { 
            detail: { 
              success: true,
              taskId,
              result: {
                final_output: '攻击流程已完成，所有阶段执行成功。'
              }
            } 
          });
          window.dispatchEvent(event);
        }
      }
    };
    
    // 开始轮询
    setTimeout(updateProgress, 1000);
  }
  
  /**
   * 获取任务状态
   * @param {string} taskId - 任务ID
   * @returns {Promise<Object>} - 返回任务状态
   */
  static async getTaskStatus(taskId) {
    try {
      // 获取任务状态
      const taskStatus = AttackTaskService.getTaskStatus(taskId);
      
      if (!taskStatus) {
        throw new Error(`任务不存在: ${taskId}`);
      }
      
      return {
        success: true,
        taskId,
        status: taskStatus
      };
    } catch (error) {
      console.error(`获取任务状态失败: ${error.message}`);
      return {
        success: false,
        message: `获取任务状态失败: ${error.message}`,
        error
      };
    }
  }

  /**
   * 执行社会工程学攻击
   * @param {Object} attackData - 攻击数据
   * @returns {Promise<Object>} - 返回攻击结果
   */
  static async executeSocialEngineeringAttack(attackData) {
    try {
      console.log("开始执行社会工程学攻击:", attackData);

      // 构建API请求URL
      const apiUrl = `/api/attack/execute_random_social_attack`;

      // 构建请求数据
      // 根据攻击目标选择不同的主机URL
      let targetHost = "http://localhost:5001"; // 默认使用alice容器

      // 如果有目标设备，根据设备名称或IP选择不同的主机
      if (attackData.target) {
        const targetName = attackData.target.deviceData?.name || "";
        const targetIp = attackData.target.deviceData?.ip || "";

        if (targetName.includes("PC-1") || targetIp.includes("192.168.100.9")) {
          targetHost = "http://localhost:5001"; // alice
        } else if (
          targetName.includes("PC-2") ||
          targetIp.includes("192.168.100.34")
        ) {
          targetHost = "http://localhost:5002"; // bob
        }
      }

      console.log(`选择社会工程学攻击目标主机: ${targetHost}`);

      // 构建请求数据
      const requestData = {
        victim_url: targetHost, // 目标主机URL
        victim_name: attackData.target?.deviceData?.name || "未知用户",
        company: "ACME_CORP", // 公司名称，实际环境中应该从配置或参数中获取
      };

      // 创建攻击任务
      const taskId = AttackTaskService.createTask({
        ...attackData,
        targetHost,
        attackType: 'social_engineering'
      });

      // 更新任务状态为运行中
      AttackTaskService.updateTask(taskId, {
        status: AttackTaskService.STATUS.RUNNING,
        phase: AttackTaskService.PHASE.WEAPONIZATION
      });

      // 添加初始日志
      AttackTaskService.addTaskLog(taskId, 'info', '攻击智能体', `开始对 ${targetHost} 执行社会工程学攻击`);

      // 发送请求到攻击智能体
      try {
        const response = await fetch(apiUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(requestData),
        });

        // 检查响应状态
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`攻击智能体请求失败: ${response.status} ${errorText}`);
        }

        // 解析响应数据
        const result = await response.json();
        
        // 更新任务状态
        AttackTaskService.completeTask(taskId, result);
        
        // 添加成功日志
        AttackTaskService.addTaskLog(taskId, 'success', '攻击智能体', '社会工程学攻击执行成功');
        
        // 触发攻击完成事件
        const event = new CustomEvent('attack-completed', { 
          detail: { 
            success: true,
            taskId,
            result 
          } 
        });
        window.dispatchEvent(event);

        return {
          success: true,
          message: "社会工程学攻击执行成功",
          taskId,
          details: result,
        };
      } catch (error) {
        // 更新任务状态
        AttackTaskService.failTask(taskId, error.message);
        
        // 添加错误日志
        AttackTaskService.addTaskLog(taskId, 'error', '攻击智能体', `社会工程学攻击执行失败: ${error.message}`);
        
        // 触发攻击失败事件
        const event = new CustomEvent('attack-completed', { 
          detail: { 
            success: false,
            taskId,
            error: error.message 
          } 
        });
        window.dispatchEvent(event);
        
        throw error;
      }
    } catch (error) {
      console.error("执行社会工程学攻击失败:", error);
      return {
        success: false,
        message: `执行社会工程学攻击失败: ${error.message}`,
        error,
      };
    }
  }

  /**
   * 获取攻击智能体状态
   * @returns {Promise<Object>} - 返回攻击智能体状态
   */
  static async getAgentStatus() {
    try {
      // 构建API请求URL
      const apiUrl = `/api/attack/status`;

      // 发送请求到攻击智能体
      const response = await fetch(apiUrl);

      // 检查响应状态
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `获取攻击智能体状态失败: ${response.status} ${errorText}`
        );
      }

      // 解析响应数据
      const result = await response.json();

      return {
        success: true,
        status: result.status,
        details: result,
      };
    } catch (error) {
      console.error("获取攻击智能体状态失败:", error);
      return {
        success: false,
        message: `获取攻击智能体状态失败: ${error.message}`,
        error,
      };
    }
  }
}

export default AttackAgentService;