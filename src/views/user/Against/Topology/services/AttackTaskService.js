/**
 * 攻击任务服务
 * 提供攻击任务的创建、查询和管理功能
 */

/**
 * 攻击任务服务类
 */
class AttackTaskService {
  // 存储所有任务
  static tasks = new Map();

  // 任务状态常量
  static STATUS = {
    PENDING: "pending", // 等待执行
    RUNNING: "running", // 正在执行
    COMPLETED: "completed", // 已完成
    FAILED: "failed", // 失败
  };

  // 攻击阶段常量
  static PHASE = {
    RECONNAISSANCE: "reconnaissance", // 侦察
    WEAPONIZATION: "weaponization", // 武器化
    DELIVERY: "delivery", // 投递
    EXPLOITATION: "exploitation", // 利用
    INSTALLATION: "installation", // 安装
    COMMAND_AND_CONTROL: "command_and_control", // 命令与控制
    ACTIONS_ON_OBJECTIVES: "actions_on_objectives", // 目标行动
  };

  /**
   * 创建新任务
   * @param {Object} attackData - 攻击数据
   * @returns {string} - 返回任务ID
   */
  static createTask(attackData) {
    // 生成唯一任务ID
    const taskId = `task_${Date.now()}_${Math.floor(Math.random() * 1000)}`;

    // 创建任务对象
    const task = {
      id: taskId,
      attackData,
      status: this.STATUS.PENDING,
      phase: this.PHASE.RECONNAISSANCE,
      progress: 0,
      logs: [],
      result: null,
      error: null,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    // 存储任务
    this.tasks.set(taskId, task);

    return taskId;
  }

  /**
   * 获取任务状态
   * @param {string} taskId - 任务ID
   * @returns {Object|null} - 返回任务状态，如果任务不存在则返回null
   */
  static getTaskStatus(taskId) {
    if (!this.tasks.has(taskId)) {
      return null;
    }

    return { ...this.tasks.get(taskId) };
  }

  /**
   * 更新任务状态
   * @param {string} taskId - 任务ID
   * @param {Object} updates - 要更新的字段
   * @returns {boolean} - 更新是否成功
   */
  static updateTask(taskId, updates) {
    if (!this.tasks.has(taskId)) {
      return false;
    }

    const task = this.tasks.get(taskId);

    // 更新任务字段
    Object.assign(task, {
      ...updates,
      updatedAt: new Date(),
    });

    return true;
  }

  /**
   * 添加任务日志
   * @param {string} taskId - 任务ID
   * @param {string} level - 日志级别 (info, warning, error, success, debug)
   * @param {string} source - 日志来源
   * @param {string} message - 日志消息
   * @returns {boolean} - 添加是否成功
   */
  static addTaskLog(taskId, level, source, message) {
    if (!this.tasks.has(taskId)) {
      return false;
    }

    const task = this.tasks.get(taskId);

    // 添加日志
    task.logs.push({
      level,
      source,
      message,
      timestamp: new Date(),
    });

    return true;
  }

  /**
   * 完成任务
   * @param {string} taskId - 任务ID
   * @param {Object} result - 任务结果
   * @returns {boolean} - 操作是否成功
   */
  static completeTask(taskId, result) {
    if (!this.tasks.has(taskId)) {
      return false;
    }

    const task = this.tasks.get(taskId);

    // 更新任务状态
    Object.assign(task, {
      status: this.STATUS.COMPLETED,
      progress: 100,
      result,
      updatedAt: new Date(),
    });

    return true;
  }

  /**
   * 标记任务失败
   * @param {string} taskId - 任务ID
   * @param {Error|string} error - 错误信息
   * @returns {boolean} - 操作是否成功
   */
  static failTask(taskId, error) {
    if (!this.tasks.has(taskId)) {
      return false;
    }

    const task = this.tasks.get(taskId);

    // 更新任务状态
    Object.assign(task, {
      status: this.STATUS.FAILED,
      error: error instanceof Error ? error.message : error,
      updatedAt: new Date(),
    });

    return true;
  }

  /**
   * 清理已完成或失败的任务
   * @param {number} maxAge - 最大保留时间（毫秒）
   */
  static cleanupTasks(maxAge = 3600000) {
    // 默认1小时
    const now = Date.now();

    for (const [taskId, task] of this.tasks.entries()) {
      if (
        (task.status === this.STATUS.COMPLETED ||
          task.status === this.STATUS.FAILED) &&
        now - task.updatedAt.getTime() > maxAge
      ) {
        this.tasks.delete(taskId);
      }
    }
  }
}

export default AttackTaskService;
