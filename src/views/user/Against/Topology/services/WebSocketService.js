/**
 * WebSocket服务
 * 提供与后端WebSocket的连接和消息处理
 */

class WebSocketService {
  // WebSocket实例
  static ws = null;
  
  // 连接状态
  static connected = false;
  
  // 消息处理器
  static messageHandlers = [];
  
  // 重连次数和最大重连次数
  static reconnectCount = 0;
  static maxReconnectCount = 5;
  
  // 重连延迟（毫秒）
  static reconnectDelay = 2000;
  
  // 自动重连标志
  static autoReconnect = true;
  
  /**
   * 连接到WebSocket服务器
   * @returns {Promise<boolean>} - 连接是否成功
   */
  static async connect() {
    return new Promise((resolve) => {
      try {
        // 如果已经连接，直接返回
        if (this.connected && this.ws && this.ws.readyState === WebSocket.OPEN) {
          console.log('WebSocket已连接');
          resolve(true);
          return;
        }
        
        // 如果有旧的连接，先关闭
        if (this.ws) {
          try {
            this.ws.close();
          } catch (e) {
            console.warn('关闭旧WebSocket连接失败:', e);
          }
          this.ws = null;
        }
        
        // 构建WebSocket URL
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        const wsUrl = `${protocol}//${host}/ws/logs`;
        
        console.log(`正在连接WebSocket: ${wsUrl}`);
        
        // 创建WebSocket实例
        this.ws = new WebSocket(wsUrl);
        
        // 连接成功
        this.ws.onopen = () => {
          console.log('WebSocket连接成功');
          this.connected = true;
          this.reconnectCount = 0;
          
          // 发送一个心跳消息，确保连接正常
          this.sendPing();
          
          resolve(true);
        };
        
        // 连接关闭
        this.ws.onclose = (event) => {
          console.log(`WebSocket连接关闭，代码: ${event.code}, 原因: ${event.reason}`);
          this.connected = false;
          
          // 尝试重连
          if (this.autoReconnect && this.reconnectCount < this.maxReconnectCount) {
            this.reconnectCount++;
            console.log(`WebSocket尝试重连 (${this.reconnectCount}/${this.maxReconnectCount})...`);
            setTimeout(() => this.connect(), this.reconnectDelay * this.reconnectCount); // 指数退避
          }
        };
        
        // 连接错误
        this.ws.onerror = (error) => {
          console.error('WebSocket连接错误:', error);
          this.connected = false;
          resolve(false);
        };
        
        // 接收消息
        this.ws.onmessage = (event) => {
          try {
            // 如果是心跳响应，不做处理
            if (event.data === 'pong') {
              console.debug('收到心跳响应');
              return;
            }
            
            let message;
            try {
              message = JSON.parse(event.data);
            } catch (e) {
              console.debug('收到非JSON消息:', event.data);
              return;
            }
            
            console.debug('收到WebSocket消息:', message);
            
            // 调用所有消息处理器
            this.messageHandlers.forEach(handler => {
              try {
                handler(message);
              } catch (error) {
                console.error('消息处理器执行错误:', error);
              }
            });
          } catch (error) {
            console.error('处理WebSocket消息失败:', error);
          }
        };
      } catch (error) {
        console.error('创建WebSocket连接失败:', error);
        resolve(false);
      }
    });
  }
  
  /**
   * 发送心跳消息
   */
  static sendPing() {
    if (this.connected && this.ws && this.ws.readyState === WebSocket.OPEN) {
      try {
        this.ws.send('ping');
        // 每30秒发送一次心跳
        setTimeout(() => this.sendPing(), 30000);
      } catch (error) {
        console.error('发送心跳消息失败:', error);
      }
    }
  }
  
  /**
   * 添加消息处理器
   * @param {Function} handler - 消息处理函数
   */
  static addMessageHandler(handler) {
    if (typeof handler === 'function' && !this.messageHandlers.includes(handler)) {
      this.messageHandlers.push(handler);
    }
  }
  
  /**
   * 移除消息处理器
   * @param {Function} handler - 消息处理函数
   */
  static removeMessageHandler(handler) {
    const index = this.messageHandlers.indexOf(handler);
    if (index !== -1) {
      this.messageHandlers.splice(index, 1);
    }
  }
  
  /**
   * 关闭WebSocket连接
   */
  static disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.connected = false;
    }
  }
  
  /**
   * 发送消息到WebSocket服务器
   * @param {Object} message - 要发送的消息
   * @returns {boolean} - 发送是否成功
   */
  static sendMessage(message) {
    if (!this.connected || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket未连接，无法发送消息');
      return false;
    }
    
    try {
      this.ws.send(JSON.stringify(message));
      return true;
    } catch (error) {
      console.error('发送WebSocket消息失败:', error);
      return false;
    }
  }
}

export default WebSocketService;