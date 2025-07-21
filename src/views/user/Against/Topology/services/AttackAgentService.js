/**
 * 攻击智能体服务
 * 提供与攻击智能体的交互功能
 */

// 模拟API调用延迟
const simulateDelay = (ms = 500) =>
  new Promise((resolve) => setTimeout(resolve, ms));

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

      // 启动一个并行的真实攻击过程，但不等待其完成
      this.startRealAttack(requestData);

      // 同时返回一个模拟的攻击结果，让前端可以立即开始显示动画
      // 这样可以避免前端等待后端长时间处理的问题
      return await this.simulateAttackProcess(attackData, targetHost);
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
   */
  static async startRealAttack(requestData) {
    try {
      // 构建API请求URL
      const apiUrl = `/api/attack/execute_full_attack`;

      // 直接调用攻击API，但不等待响应
      fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      })
        .then(async (response) => {
          if (response.ok) {
            const result = await response.json();
            console.log("真实攻击执行成功:", result);

            // 这里可以触发一个事件，通知前端攻击已完成
            // 例如，可以使用自定义事件
            const event = new CustomEvent("attack-completed", {
              detail: {
                success: true,
                result,
              },
            });
            window.dispatchEvent(event);
          } else {
            const errorText = await response.text();
            console.error(`真实攻击执行失败: ${response.status} ${errorText}`);

            // 触发失败事件
            const event = new CustomEvent("attack-completed", {
              detail: {
                success: false,
                error: `${response.status} ${errorText}`,
              },
            });
            window.dispatchEvent(event);
          }
        })
        .catch((error) => {
          console.error("真实攻击请求发送失败:", error);

          // 触发失败事件
          const event = new CustomEvent("attack-completed", {
            detail: {
              success: false,
              error: error.message,
            },
          });
          window.dispatchEvent(event);
        });

      // 注意：这个函数不会等待攻击完成，而是立即返回
    } catch (error) {
      console.error("启动真实攻击过程失败:", error);
    }
  }

  /**
   * 模拟攻击流程
   * @param {Object} attackData - 攻击数据
   * @param {string} targetHost - 目标主机URL
   * @returns {Promise<Object>} - 返回模拟的攻击结果
   */
  static async simulateAttackProcess(attackData, targetHost) {
    // 返回立即成功的响应，让前端可以继续执行动画
    // 实际上后端会继续处理攻击流程

    // 模拟侦察阶段
    await this.simulateDelay(500);

    // 构造模拟的攻击结果
    const simulatedResult = {
      success: true,
      message: "自动攻击执行成功",
      details: {
        final_output: `
侦察阶段：成功获取目标主机信息
目标：${targetHost}
操作系统：Ubuntu 20.04 LTS
用户：alice
部门：研发部
职位：高级软件工程师

武器化阶段：成功生成针对性钓鱼邮件
邮件主题：新开发工具许可证
目标：alice@acmecorp.com

投递阶段：成功发送钓鱼邮件
目标已点击恶意链接
成功获取目标凭据

利用阶段：成功利用Apache漏洞
获取会话ID：sess_12345678

横向移动：成功枚举内网主机
可达主机：10.0.0.5, 10.0.0.6
执行命令：cat /etc/passwd
命令输出：command executed successfully.
        `,
      },
    };

    return simulatedResult;
  }

  /**
   * 模拟延迟
   * @param {number} ms - 延迟毫秒数
   * @returns {Promise<void>}
   */
  static simulateDelay(ms = 500) {
    return new Promise((resolve) => setTimeout(resolve, ms));
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

      // 发送请求到攻击智能体
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

      return {
        success: true,
        message: "社会工程学攻击执行成功",
        details: result,
      };
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
