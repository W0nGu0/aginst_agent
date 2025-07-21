/**
 * 钓鱼攻击服务类
 * 负责与攻击代理API交互，执行钓鱼攻击
 */
class PhishingService {
  /**
   * 执行完整的钓鱼攻击
   * @param {string} targetHost - 目标主机地址
   * @returns {Promise} - 返回攻击结果的Promise
   */
  static async executeFullAttack(targetHost) {
    try {
      console.log('发起钓鱼攻击请求:', targetHost);
      
      const response = await fetch('/api/attack/execute_full_attack', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          target_host: targetHost
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('钓鱼攻击请求失败:', response.status, response.statusText, errorText);
        throw new Error(`钓鱼攻击请求失败: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      console.log('钓鱼攻击结果:', data);
      return data;
    } catch (error) {
      console.error('执行钓鱼攻击失败:', error);
      throw error;
    }
  }

  /**
   * 执行随机社会工程学攻击
   * @param {string} victimUrl - 受害者主机地址
   * @param {string} victimName - 受害者名称
   * @param {string} company - 公司名称
   * @returns {Promise} - 返回攻击结果的Promise
   */
  static async executeRandomSocialAttack(victimUrl, victimName, company) {
    try {
      console.log('发起随机社会工程学攻击请求:', { victimUrl, victimName, company });
      
      const response = await fetch('/api/attack/execute_random_social_attack', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          victim_url: victimUrl,
          victim_name: victimName,
          company: company
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('社会工程学攻击请求失败:', response.status, response.statusText, errorText);
        throw new Error(`社会工程学攻击请求失败: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      console.log('社会工程学攻击结果:', data);
      return data;
    } catch (error) {
      console.error('执行社会工程学攻击失败:', error);
      throw error;
    }
  }

  /**
   * 模拟钓鱼攻击（用于前端演示）
   * @param {Object} attackData - 攻击数据
   * @returns {Promise} - 返回模拟攻击结果的Promise
   */
  static simulatePhishingAttack(attackData) {
    return new Promise((resolve) => {
      console.log('模拟钓鱼攻击:', attackData);
      
      // 模拟攻击延迟
      setTimeout(() => {
        // 模拟攻击流程
        const attackSteps = [
          { 
            step: 'reconnaissance', 
            description: '侦察目标信息', 
            details: `发现目标 ${attackData.target.deviceData.name} 属于 ACME Corp 公司`,
            success: true
          },
          { 
            step: 'email_crafting', 
            description: '撰写钓鱼邮件', 
            details: '根据目标公司和用户信息生成定制化钓鱼邮件',
            success: true
          },
          { 
            step: 'email_delivery', 
            description: '投递钓鱼邮件', 
            details: `成功将钓鱼邮件发送至目标 ${attackData.target.deviceData.ip}`,
            success: true
          },
          { 
            step: 'victim_action', 
            description: '目标操作', 
            details: '目标打开邮件并点击恶意链接',
            success: Math.random() > 0.3 // 70%成功率
          }
        ];
        
        // 如果目标操作成功，添加后续步骤
        if (attackSteps[3].success) {
          attackSteps.push(
            { 
              step: 'credential_harvest', 
              description: '获取凭证', 
              details: `成功获取目标 ${attackData.target.deviceData.name} 的用户凭证`,
              success: true
            },
            { 
              step: 'privilege_escalation', 
              description: '权限提升', 
              details: '利用获取的凭证成功提升权限',
              success: Math.random() > 0.2 // 80%成功率
            }
          );
          
          // 如果权限提升成功，添加横向移动步骤
          if (attackSteps[5].success) {
            attackSteps.push(
              { 
                step: 'lateral_movement', 
                description: '横向移动', 
                details: '成功访问内网其他主机',
                success: Math.random() > 0.3 // 70%成功率
              }
            );
          }
        }
        
        // 确定最终攻击结果
        const finalSuccess = attackSteps[attackSteps.length - 1].success;
        
        // 生成日志
        const logs = attackSteps.map(step => ({
          timestamp: new Date().toISOString(),
          level: step.success ? 'info' : 'error',
          message: `${step.description}: ${step.success ? '成功' : '失败'} - ${step.details}`
        }));
        
        resolve({
          success: finalSuccess,
          attackId: `phish_${Date.now()}`,
          steps: attackSteps,
          logs: logs
        });
      }, 2000); // 2秒延迟模拟网络请求
    });
  }
}

export default PhishingService;