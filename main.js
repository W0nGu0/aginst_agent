// 动态粒子效果
document.addEventListener('DOMContentLoaded', () => {
    // 生成随机粒子
    const createParticles = () => {
        const graphicContainer = document.querySelector('.cyber-graphic');
        if (!graphicContainer) return;
        
        for (let i = 0; i < 20; i++) {
            const particle = document.createElement('div');
            particle.classList.add('cyber-particle');
            
            // 随机位置和大小
            const size = Math.random() * 3 + 1;
            const posX = Math.random() * 100;
            const posY = Math.random() * 100;
            const delay = Math.random() * 5;
            const duration = Math.random() * 10 + 10;
            
            // 随机颜色
            const colors = ['var(--primary)', 'var(--secondary)', 'var(--accent)'];
            const color = colors[Math.floor(Math.random() * colors.length)];
            
            // 设置样式
            particle.style.cssText = `
                position: absolute;
                top: ${posY}%;
                left: ${posX}%;
                width: ${size}px;
                height: ${size}px;
                background-color: ${color};
                border-radius: 50%;
                opacity: ${Math.random() * 0.5 + 0.3};
                animation: floatParticle ${duration}s ease-in-out ${delay}s infinite;
            `;
            
            graphicContainer.appendChild(particle);
        }
        
        // 添加漂浮动画
        const style = document.createElement('style');
        style.textContent = `
            @keyframes floatParticle {
                0% { transform: translate(0, 0); }
                25% { transform: translate(${Math.random() * 30 - 15}px, ${Math.random() * 30 - 15}px); }
                50% { transform: translate(${Math.random() * 30 - 15}px, ${Math.random() * 30 - 15}px); }
                75% { transform: translate(${Math.random() * 30 - 15}px, ${Math.random() * 30 - 15}px); }
                100% { transform: translate(0, 0); }
            }
        `;
        document.head.appendChild(style);
    };
    
    createParticles();
    
    // 修复动态滚动效果
    const fixScrollAnimation = () => {
        const container = document.querySelector('.scene-prompts-container');
        const prompts = document.querySelector('.scene-prompts');
        
        if (!container || !prompts) return;
        
        // 获取所有提示项
        const items = document.querySelectorAll('.scene-prompt-item');
        const itemWidth = 64 * 4; // 4个卡片的宽度
        const itemSpacing = 16; // 每个卡片之间的间距
        
        // 计算动画总宽度
        const totalWidth = items.length * (itemWidth + itemSpacing);
        
        // 更新滚动动画
        const styleSheet = document.createElement('style');
        styleSheet.textContent = `
            @keyframes scrollPrompts {
                0% { transform: translateX(0); }
                100% { transform: translateX(-${totalWidth / 2}px); }
            }
            
            .scene-prompts {
                animation: scrollPrompts 30s linear infinite;
            }
        `;
        document.head.appendChild(styleSheet);
    };
    
    fixScrollAnimation();
    
    // 为提示词方块添加点击事件
    const addPromptCardClickEvents = () => {
        const promptCards = document.querySelectorAll('.scene-prompt-item');
        if (promptCards.length === 0) return;
        
        promptCards.forEach(card => {
            card.style.cursor = 'pointer';
            card.addEventListener('click', () => {
                // 显示加载指示器
                const loadingIndicator = document.createElement('div');
                loadingIndicator.classList.add('loading-overlay');
                loadingIndicator.innerHTML = `
                    <div class="loading-spinner">
                        <div class="spinner"></div>
                        <div class="mt-3 text-base-content">场景生成中...</div>
                    </div>
                `;
                document.body.appendChild(loadingIndicator);
                
                // 延迟跳转以显示加载效果
                setTimeout(() => {
                    window.location.href = 'scene-detail.html';
                }, 1500);
            });
        });
        
        // 添加加载指示器样式
        const loadingStyle = document.createElement('style');
        loadingStyle.textContent = `
            .loading-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(17, 24, 39, 0.8);
                backdrop-filter: blur(5px);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
            }
            .loading-spinner {
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .spinner {
                width: 50px;
                height: 50px;
                border: 3px solid rgba(74, 158, 255, 0.3);
                border-radius: 50%;
                border-top-color: var(--primary);
                animation: spin 1s ease-in-out infinite;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(loadingStyle);
    };
    
    addPromptCardClickEvents();
    
    // 场景生成按钮交互效果
    const sceneGenerateBtn = document.querySelector('button');
    const sceneInput = document.querySelector('textarea');
    
    if (sceneGenerateBtn && sceneInput) {
        sceneGenerateBtn.addEventListener('click', () => {
            const inputValue = sceneInput.value.trim();
            if (!inputValue) {
                // 添加一个抖动效果提示用户输入内容
                sceneInput.classList.add('input-shake');
                setTimeout(() => {
                    sceneInput.classList.remove('input-shake');
                }, 500);
                return;
            }
            
            // 显示加载效果
            sceneGenerateBtn.innerHTML = `<span>生成中</span><span class="loading-dots">...</span>`;
            sceneGenerateBtn.disabled = true;
            
            // 模拟场景生成的加载时间
            setTimeout(() => {
                // 创建加载覆盖层
                const loadingOverlay = document.createElement('div');
                loadingOverlay.classList.add('loading-overlay');
                loadingOverlay.innerHTML = `
                    <div class="loading-spinner">
                        <div class="spinner"></div>
                        <div class="mt-3 text-base-content">正在创建您的自定义场景...</div>
                    </div>
                `;
                document.body.appendChild(loadingOverlay);
                
                // 短暂延迟后跳转到场景详情页
                setTimeout(() => {
                    window.location.href = 'scene-detail.html';
                }, 2000);
            }, 1000);
        });
    }
    
    // 添加抖动和成功效果的样式
    const styleSheet = document.createElement('style');
    styleSheet.textContent = `
        @keyframes shake {
            0% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            50% { transform: translateX(5px); }
            75% { transform: translateX(-5px); }
            100% { transform: translateX(0); }
        }
        
        .input-shake {
            animation: shake 0.5s ease-in-out;
            border: 1px solid #ff5252 !important;
        }
        
        .success-input {
            border: 1px solid var(--accent) !important;
            box-shadow: 0 0 10px var(--accent-light) !important;
        }
        
        .loading-dots {
            display: inline-block;
            width: 20px;
            text-align: left;
        }
        
        .loading-dots::after {
            content: '.';
            animation: dots 1.5s steps(4, end) infinite;
        }
        
        @keyframes dots {
            0%, 20% { content: '.'; }
            40% { content: '..'; }
            60% { content: '...'; }
            80%, 100% { content: ''; }
        }
    `;
    document.head.appendChild(styleSheet);
}); 