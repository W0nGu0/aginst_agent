<template>
    <div class="phishing-attack-visualization">
        <div class="visualization-container" ref="visualizationContainer">
            <!-- 攻击流程可视化将在这里渲染 -->
        </div>

        <div v-if="showDetails" class="attack-details">
            <div class="details-header">
                <h3>钓鱼攻击详情</h3>
                <button class="close-btn" @click="closeDetails">&times;</button>
            </div>

            <div class="details-content">
                <!-- 攻击阶段 -->
                <div class="attack-stages">
                    <h4>攻击阶段</h4>
                    <div class="stages-timeline">
                        <div v-for="(stage, index) in attackStages" :key="index" class="stage-item"
                            :class="{ 'completed': currentStage > index, 'active': currentStage === index }">
                            <div class="stage-icon">
                                <i :class="stage.icon"></i>
                            </div>
                            <div class="stage-info">
                                <div class="stage-name">{{ stage.name }}</div>
                                <div class="stage-description">{{ stage.description }}</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 目标信息 -->
                <div class="target-info">
                    <h4>目标信息</h4>
                    <div class="info-grid">
                        <div class="info-item">
                            <div class="info-label">主机名</div>
                            <div class="info-value">{{ targetInfo.name || '未知' }}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">IP地址</div>
                            <div class="info-value">{{ targetInfo.ip || '未知' }}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">用户名</div>
                            <div class="info-value">{{ targetInfo.username || '未知' }}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">部门</div>
                            <div class="info-value">{{ targetInfo.department || '未知' }}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">职位</div>
                            <div class="info-value">{{ targetInfo.role || '未知' }}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">邮箱</div>
                            <div class="info-value">{{ targetInfo.email || '未知' }}</div>
                        </div>
                    </div>
                </div>

                <!-- 钓鱼邮件预览 -->
                <div v-if="phishingEmail" class="phishing-email">
                    <h4>钓鱼邮件</h4>
                    <div class="email-preview">
                        <div class="email-header">
                            <div class="email-field">
                                <span class="field-label">发件人:</span>
                                <span class="field-value">{{ phishingEmail.sender }}</span>
                            </div>
                            <div class="email-field">
                                <span class="field-label">收件人:</span>
                                <span class="field-value">{{ phishingEmail.recipient }}</span>
                            </div>
                            <div class="email-field">
                                <span class="field-label">主题:</span>
                                <span class="field-value">{{ phishingEmail.subject }}</span>
                            </div>
                            <div class="email-field">
                                <span class="field-label">时间:</span>
                                <span class="field-value">{{ formatDate(phishingEmail.timestamp) }}</span>
                            </div>
                        </div>
                        <div class="email-body" v-html="phishingEmail.content"></div>
                    </div>
                </div>

                <!-- 攻击结果 -->
                <div v-if="attackResult" class="attack-result">
                    <h4>攻击结果</h4>
                    <div class="result-status"
                        :class="{ 'success': attackResult.success, 'failure': !attackResult.success }">
                        <i :class="attackResult.success ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i>
                        <span>{{ attackResult.message }}</span>
                    </div>

                    <div v-if="attackResult.success" class="result-details">
                        <div class="result-item">
                            <div class="result-label">成功率</div>
                            <div class="result-value">{{ (attackResult.successRate * 100).toFixed(0) }}%</div>
                        </div>
                        <div v-if="attackResult.obtainedInfo" class="result-item">
                            <div class="result-label">获取的凭据</div>
                            <div class="result-value">{{ attackResult.obtainedInfo.credentials }}</div>
                        </div>
                        <div v-if="attackResult.obtainedInfo" class="result-item">
                            <div class="result-label">访问级别</div>
                            <div class="result-value">{{ translateAccessLevel(attackResult.obtainedInfo.accessLevel) }}
                            </div>
                        </div>
                    </div>

                    <div v-else class="result-details">
                        <div class="result-item">
                            <div class="result-label">失败原因</div>
                            <div class="result-value">{{ attackResult.reason }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, watch } from 'vue'
import HostInfoService from '../services/HostInfoService'

export default {
    name: 'PhishingAttackVisualization',
    props: {
        show: {
            type: Boolean,
            default: false
        },
        attacker: {
            type: Object,
            default: () => ({})
        },
        target: {
            type: Object,
            default: () => ({})
        },
        attackType: {
            type: String,
            default: 'phishing'
        }
    },

    setup(props, { emit }) {
        const visualizationContainer = ref(null)
        const showDetails = ref(false)
        const currentStage = ref(0)
        const targetInfo = ref({})
        const phishingEmail = ref(null)
        const attackResult = ref(null)

        // 攻击阶段定义
        const attackStages = [
            {
                name: '侦察',
                description: '收集目标信息',
                icon: 'fas fa-search'
            },
            {
                name: '制作钓鱼邮件',
                description: '根据目标信息制作定制化钓鱼邮件',
                icon: 'fas fa-edit'
            },
            {
                name: '发送邮件',
                description: '将钓鱼邮件发送给目标',
                icon: 'fas fa-paper-plane'
            },
            {
                name: '目标接收',
                description: '目标接收并查看邮件',
                icon: 'fas fa-envelope-open'
            },
            {
                name: '点击链接',
                description: '目标点击邮件中的恶意链接',
                icon: 'fas fa-mouse-pointer'
            },
            {
                name: '凭据窃取',
                description: '获取目标的登录凭据',
                icon: 'fas fa-key'
            },
            {
                name: '攻击完成',
                description: '攻击流程结束',
                icon: 'fas fa-flag-checkered'
            }
        ]

        // 监听显示状态变化
        watch(() => props.show, (newVal) => {
            if (newVal) {
                // 当组件显示时，重置状态并开始可视化
                resetVisualization()
                startVisualization()
            }
        })

        // 重置可视化状态
        const resetVisualization = () => {
            currentStage.value = 0
            targetInfo.value = {}
            phishingEmail.value = null
            attackResult.value = null
            showDetails.value = false

            // 清空可视化容器
            if (visualizationContainer.value) {
                visualizationContainer.value.innerHTML = ''
            }
        }

        // 开始可视化
        const startVisualization = async () => {
            // 创建可视化图表
            createVisualization()

            // 模拟攻击流程
            await simulateAttackFlow()

            // 显示详细信息
            showDetails.value = true
        }

        // 创建可视化图表
        const createVisualization = () => {
            if (!visualizationContainer.value) return

            const container = visualizationContainer.value
            const width = container.clientWidth
            const height = container.clientHeight

            // 创建SVG
            const svg = d3.select(container)
                .append('svg')
                .attr('width', width)
                .attr('height', height)

            // 创建攻击者和目标节点
            const nodes = [
                { id: 'attacker', name: '攻击者', x: width * 0.2, y: height * 0.5, type: 'attacker' },
                { id: 'target', name: props.target.deviceData?.name || '目标', x: width * 0.8, y: height * 0.5, type: 'target' }
            ]

            // 创建连接线
            const links = [
                { source: 'attacker', target: 'target', id: 'attack-path' }
            ]

            // 绘制连接线
            svg.selectAll('line')
                .data(links)
                .enter()
                .append('line')
                .attr('id', d => d.id)
                .attr('x1', d => nodes.find(n => n.id === d.source).x)
                .attr('y1', d => nodes.find(n => n.id === d.source).y)
                .attr('x2', d => nodes.find(n => n.id === d.target).x)
                .attr('y2', d => nodes.find(n => n.id === d.target).y)
                .attr('stroke', '#3498db')
                .attr('stroke-width', 2)
                .attr('stroke-dasharray', '5,5')

            // 绘制节点
            const nodeGroups = svg.selectAll('g')
                .data(nodes)
                .enter()
                .append('g')
                .attr('id', d => d.id)
                .attr('transform', d => `translate(${d.x}, ${d.y})`)

            // 添加节点图标
            nodeGroups.append('circle')
                .attr('r', 30)
                .attr('fill', d => d.type === 'attacker' ? '#e74c3c' : '#3498db')

            // 添加节点图标
            nodeGroups.append('text')
                .attr('text-anchor', 'middle')
                .attr('dominant-baseline', 'central')
                .attr('fill', 'white')
                .attr('font-family', 'FontAwesome')
                .attr('font-size', '20px')
                .text(d => d.type === 'attacker' ? '\uf21b' : '\uf109') // 攻击者图标和电脑图标

            // 添加节点标签
            nodeGroups.append('text')
                .attr('text-anchor', 'middle')
                .attr('y', 45)
                .attr('fill', 'white')
                .text(d => d.name)
        }

        // 模拟攻击流程
        const simulateAttackFlow = async () => {
            // 第1阶段：侦察
            await simulateStage(0, 1000)

            // 获取目标信息
            targetInfo.value = await getTargetInfo()

            // 第2阶段：制作钓鱼邮件
            await simulateStage(1, 1500)

            // 生成钓鱼邮件
            phishingEmail.value = await generatePhishingEmail()

            // 第3阶段：发送邮件
            await simulateStage(2, 1000)

            // 创建并动画显示邮件图标
            animateEmailDelivery()

            // 第4阶段：目标接收
            await simulateStage(3, 2000)

            // 第5阶段：点击链接
            await simulateStage(4, 1500)

            // 第6阶段：凭据窃取
            await simulateStage(5, 2000)

            // 创建并动画显示数据窃取
            animateDataTheft()

            // 生成攻击结果
            attackResult.value = await generateAttackResult()

            // 第7阶段：攻击完成
            await simulateStage(6, 1000)
        }

        // 模拟单个攻击阶段
        const simulateStage = async (stage, duration) => {
            currentStage.value = stage

            // 创建阶段图标
            createStageIcon(stage)

            // 等待指定时间
            await new Promise(resolve => setTimeout(resolve, duration))
        }

        // 创建阶段图标
        const createStageIcon = (stage) => {
            if (!visualizationContainer.value) return

            const container = visualizationContainer.value
            const svg = d3.select(container).select('svg')
            const width = container.clientWidth
            const height = container.clientHeight

            // 计算图标位置
            const progress = stage / (attackStages.length - 1)
            const x = width * (0.2 + progress * 0.6)
            const y = height * 0.3

            // 创建图标组
            const iconGroup = svg.append('g')
                .attr('class', 'stage-icon')
                .attr('transform', `translate(${x}, ${y})`)
                .style('opacity', 0)

            // 添加图标背景
            iconGroup.append('circle')
                .attr('r', 25)
                .attr('fill', 'rgba(0, 0, 0, 0.7)')
                .attr('stroke', 'white')
                .attr('stroke-width', 2)

            // 添加图标
            iconGroup.append('text')
                .attr('text-anchor', 'middle')
                .attr('dominant-baseline', 'central')
                .attr('fill', 'white')
                .attr('font-family', 'FontAwesome')
                .attr('font-size', '16px')
                .text(() => {
                    // 根据图标类名获取对应的Unicode字符
                    const iconMap = {
                        'fas fa-search': '\uf002',
                        'fas fa-edit': '\uf044',
                        'fas fa-paper-plane': '\uf1d8',
                        'fas fa-envelope-open': '\uf2b6',
                        'fas fa-mouse-pointer': '\uf245',
                        'fas fa-key': '\uf084',
                        'fas fa-flag-checkered': '\uf11e'
                    };
                    return iconMap[attackStages[stage].icon] || '\uf059'; // 默认为问号图标
                })

            // 添加标签
            iconGroup.append('text')
                .attr('text-anchor', 'middle')
                .attr('y', 40)
                .attr('fill', 'white')
                .attr('font-size', '12px')
                .text(attackStages[stage].name)

            // 动画显示图标
            gsap.to(iconGroup.node(), {
                opacity: 1,
                duration: 0.5,
                ease: 'power1.inOut'
            })

            // 2秒后淡出图标
            gsap.to(iconGroup.node(), {
                opacity: 0,
                duration: 0.5,
                delay: 2,
                ease: 'power1.inOut',
                onComplete: () => {
                    iconGroup.remove()
                }
            })
        }

        // 动画显示邮件传递
        const animateEmailDelivery = () => {
            if (!visualizationContainer.value) return

            const container = visualizationContainer.value
            const svg = d3.select(container).select('svg')
            const attackerNode = d3.select('#attacker')
            const targetNode = d3.select('#target')

            // 获取节点位置
            const attackerX = parseFloat(attackerNode.attr('transform').split('(')[1].split(',')[0])
            const attackerY = parseFloat(attackerNode.attr('transform').split(',')[1].split(')')[0])
            const targetX = parseFloat(targetNode.attr('transform').split('(')[1].split(',')[0])
            const targetY = parseFloat(targetNode.attr('transform').split(',')[1].split(')')[0])

            // 创建邮件图标
            const email = svg.append('text')
                .attr('class', 'email-icon')
                .attr('x', attackerX)
                .attr('y', attackerY)
                .attr('text-anchor', 'middle')
                .attr('dominant-baseline', 'central')
                .attr('fill', '#2ecc71')
                .attr('font-family', 'FontAwesome')
                .attr('font-size', '24px')
                .text('\uf0e0') // 邮件图标
                .style('opacity', 0)

            // 动画显示邮件图标
            gsap.to(email.node(), {
                opacity: 1,
                duration: 0.3,
                ease: 'power1.in'
            })

            // 动画移动邮件图标
            gsap.to(email.node(), {
                x: targetX,
                y: targetY,
                duration: 1.5,
                delay: 0.3,
                ease: 'power1.inOut'
            })

            // 动画隐藏邮件图标
            gsap.to(email.node(), {
                opacity: 0,
                duration: 0.3,
                delay: 1.8,
                ease: 'power1.out',
                onComplete: () => {
                    email.remove()
                }
            })
        }

        // 动画显示数据窃取
        const animateDataTheft = () => {
            if (!visualizationContainer.value) return

            const container = visualizationContainer.value
            const svg = d3.select(container).select('svg')
            const attackerNode = d3.select('#attacker')
            const targetNode = d3.select('#target')

            // 获取节点位置
            const attackerX = parseFloat(attackerNode.attr('transform').split('(')[1].split(',')[0])
            const attackerY = parseFloat(attackerNode.attr('transform').split(',')[1].split(')')[0])
            const targetX = parseFloat(targetNode.attr('transform').split('(')[1].split(',')[0])
            const targetY = parseFloat(targetNode.attr('transform').split(',')[1].split(')')[0])

            // 创建数据图标
            const data = svg.append('text')
                .attr('class', 'data-icon')
                .attr('x', targetX)
                .attr('y', targetY)
                .attr('text-anchor', 'middle')
                .attr('dominant-baseline', 'central')
                .attr('fill', '#e74c3c')
                .attr('font-family', 'FontAwesome')
                .attr('font-size', '24px')
                .text('\uf1c0') // 数据库图标
                .style('opacity', 0)

            // 动画显示数据图标
            gsap.to(data.node(), {
                opacity: 1,
                duration: 0.3,
                ease: 'power1.in'
            })

            // 动画移动数据图标
            gsap.to(data.node(), {
                x: attackerX,
                y: attackerY,
                duration: 1.5,
                delay: 0.3,
                ease: 'power1.inOut'
            })

            // 动画隐藏数据图标
            gsap.to(data.node(), {
                opacity: 0,
                duration: 0.3,
                delay: 1.8,
                ease: 'power1.out',
                onComplete: () => {
                    data.remove()
                }
            })
        }

        // 获取目标信息
        const getTargetInfo = async () => {
            try {
                // 使用HostInfoService获取更真实的主机信息
                const hostInfo = await HostInfoService.getHostInfo(props.target)

                // 添加兴趣爱好信息，用于社会工程学攻击
                let interests = []

                // 根据部门和角色推断可能的兴趣爱好
                if (hostInfo.department === '研发部' || hostInfo.role.includes('开发') || hostInfo.role.includes('工程师')) {
                    interests = ['技术', '编程', '云计算', '人工智能', '开源项目']
                } else if (hostInfo.department === 'IT运维' || hostInfo.role.includes('管理员')) {
                    interests = ['服务器管理', '网络安全', '自动化', '容器技术', '监控系统']
                } else if (hostInfo.department === '数据库管理' || hostInfo.role.includes('数据')) {
                    interests = ['数据库', 'SQL', '数据安全', '大数据', '数据分析']
                } else if (hostInfo.department === '网络安全' || hostInfo.role.includes('安全')) {
                    interests = ['网络安全', '渗透测试', '安全框架', '密码学', '威胁情报']
                } else if (hostInfo.department === '市场部' || hostInfo.role.includes('市场')) {
                    interests = ['市场营销', '品牌推广', '社交媒体', '数字营销', '市场分析']
                } else {
                    interests = ['办公自动化', '团队协作', '职业发展', '行业动态', '企业管理']
                }

                // 返回增强后的主机信息
                return {
                    ...hostInfo,
                    interests
                }
            } catch (error) {
                console.error('获取主机信息失败:', error)

                // 如果获取失败，返回基本信息
                const { deviceData } = props.target
                return {
                    id: props.target.id,
                    name: deviceData?.name || '未知',
                    ip: deviceData?.ip || '0.0.0.0',
                    mac: deviceData?.mac || '00:00:00:00:00:00',
                    type: deviceData?.type || '未知',
                    username: 'unknown',
                    company: 'ACME_CORP',
                    department: '未知',
                    role: '未知',
                    email: 'unknown@acmecorp.com',
                    interests: ['一般业务']
                }
            }
        }

        // 生成钓鱼邮件
        const generatePhishingEmail = async () => {
            // 模拟API调用延迟
            await new Promise(resolve => setTimeout(resolve, 1000))

            // 根据攻击类型和目标信息生成不同的钓鱼邮件
            let subject, content, sender

            if (props.attackType === 'phishing') {
                // 密码重置钓鱼邮件
                sender = `IT部门 <it@${targetInfo.value.company.toLowerCase().replace(/\s+/g, '')}.com>`
                subject = `[紧急] ${targetInfo.value.company} 账户安全通知`
                content = `
<div style="font-family: Arial, sans-serif; color: #333;">
  <p>尊敬的 ${targetInfo.value.username}，</p>
  
  <p>我们的系统检测到您的账户存在异常登录活动。为了保障您的账户安全，请立即点击以下链接重置您的密码：</p>
  
  <p><a href="http://evil-phishing-site.com/reset?email=${targetInfo.value.email}" style="color: #1a73e8; text-decoration: underline;">https://${targetInfo.value.company.toLowerCase().replace(/\s+/g, '')}.com/account/security/reset</a></p>
  
  <p>如果您没有进行过可疑操作，请务必在24小时内完成密码重置，否则您的账户将被临时冻结。</p>
  
  <p>此致，<br>${targetInfo.value.company} IT安全团队</p>
</div>
        `
            } else if (props.attackType === 'social_engineering') {
                // 社会工程学攻击邮件
                const randomInterest = targetInfo.value.interests[Math.floor(Math.random() * targetInfo.value.interests.length)]
                sender = `${targetInfo.value.company} 人力资源部 <hr@${targetInfo.value.company.toLowerCase().replace(/\s+/g, '')}.com>`
                subject = `关于${randomInterest}的内部培训通知`
                content = `
<div style="font-family: Arial, sans-serif; color: #333;">
  <p>亲爱的 ${targetInfo.value.username}，</p>
  
  <p>根据公司的人才发展计划，我们注意到您对${randomInterest}领域有浓厚的兴趣。</p>
  
  <p>我们将于下周举办一场关于${randomInterest}的内部培训，由行业顶尖专家主讲。由于名额有限，请点击以下链接确认您的参与：</p>
  
  <p><a href="http://evil-phishing-site.com/confirm?email=${targetInfo.value.email}" style="color: #1a73e8; text-decoration: underline;">https://training.${targetInfo.value.company.toLowerCase().replace(/\s+/g, '')}.com/confirm</a></p>
  
  <p>确认参与需要使用您的公司账户登录。</p>
  
  <p>期待您的参与！</p>
  
  <p>此致，<br>${targetInfo.value.company} 人力资源部</p>
</div>
        `
            } else {
                // 默认钓鱼邮件
                sender = `系统管理员 <admin@${targetInfo.value.company.toLowerCase().replace(/\s+/g, '')}.com>`
                subject = `重要：系统更新通知`
                content = `
<div style="font-family: Arial, sans-serif; color: #333;">
  <p>${targetInfo.value.username}，</p>
  
  <p>我们的系统需要进行重要更新。请点击以下链接登录系统完成必要的配置：</p>
  
  <p><a href="http://evil-phishing-site.com/login?email=${targetInfo.value.email}" style="color: #1a73e8; text-decoration: underline;">https://system.${targetInfo.value.company.toLowerCase().replace(/\s+/g, '')}.com/update</a></p>
  
  <p>此更新对于系统安全至关重要，请在今天内完成。</p>
  
  <p>谢谢配合。</p>
</div>
        `
            }

            return {
                sender,
                recipient: `${targetInfo.value.username} <${targetInfo.value.email}>`,
                subject,
                content,
                timestamp: new Date().toISOString()
            }
        }

        // 生成攻击结果
        const generateAttackResult = async () => {
            // 模拟API调用延迟
            await new Promise(resolve => setTimeout(resolve, 1000))

            // 模拟攻击成功率
            const baseSuccessRate = 0.7 // 基础成功率70%

            // 根据攻击类型调整成功率
            let typeModifier = 0
            if (props.attackType === 'phishing') {
                typeModifier = 0.1 // +10%
            } else if (props.attackType === 'social_engineering') {
                typeModifier = 0.05 // +5%
            }

            // 根据目标角色调整成功率
            let roleModifier = 0
            if (targetInfo.value.role.includes('管理员')) {
                roleModifier = -0.2 // 管理员更警惕，-20%
            } else if (targetInfo.value.role.includes('工程师')) {
                roleModifier = -0.1 // 工程师更警惕，-10%
            } else {
                roleModifier = 0.1 // 其他角色可能更容易受骗，+10%
            }

            // 计算最终成功率
            const finalSuccessRate = Math.max(0.1, Math.min(0.9, baseSuccessRate + typeModifier + roleModifier))

            // 随机决定是否成功
            const isSuccess = Math.random() < finalSuccessRate

            if (isSuccess) {
                return {
                    success: true,
                    message: `成功对 ${targetInfo.value.username} 执行钓鱼攻击`,
                    successRate: finalSuccessRate,
                    obtainedInfo: {
                        credentials: targetInfo.value.role.includes('管理员') ? '部分凭据' : '完整凭据',
                        personalInfo: true,
                        accessLevel: targetInfo.value.role.includes('管理员') ? 'medium' : 'high'
                    }
                }
            } else {
                return {
                    success: false,
                    message: `对 ${targetInfo.value.username} 执行钓鱼攻击失败`,
                    successRate: finalSuccessRate,
                    reason: '目标警觉性高，识别出了钓鱼邮件'
                }
            }
        }

        // 格式化日期
        const formatDate = (dateString) => {
            if (!dateString) return ''

            const date = new Date(dateString)
            return date.toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            })
        }

        // 翻译访问级别
        const translateAccessLevel = (level) => {
            const levels = {
                low: '低',
                medium: '中',
                high: '高'
            }

            return levels[level] || level
        }

        // 关闭详情面板
        const closeDetails = () => {
            showDetails.value = false
            emit('close')
        }

        return {
            visualizationContainer,
            showDetails,
            currentStage,
            attackStages,
            targetInfo,
            phishingEmail,
            attackResult,
            formatDate,
            translateAccessLevel,
            closeDetails
        }
    }
}
</script>

<style scoped>
.phishing-attack-visualization {
    position: relative;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
}

.visualization-container {
    flex: 1;
    background-color: #1e1e2f;
    border-radius: 8px;
    overflow: hidden;
    min-height: 300px;
}

.attack-details {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.8);
    z-index: 10;
    display: flex;
    flex-direction: column;
    border-radius: 8px;
    overflow: hidden;
}

.details-header {
    padding: 16px;
    background-color: #27293d;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.details-header h3 {
    margin: 0;
    color: #ffffff;
}

.close-btn {
    background: none;
    border: none;
    font-size: 24px;
    color: #ffffff;
    cursor: pointer;
}

.details-content {
    flex: 1;
    padding: 16px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 24px;
}

.attack-stages h4,
.target-info h4,
.phishing-email h4,
.attack-result h4 {
    margin: 0 0 16px 0;
    color: #ffffff;
    font-size: 18px;
    border-bottom: 1px solid #3a3a5c;
    padding-bottom: 8px;
}

.stages-timeline {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.stage-item {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    opacity: 0.5;
    transition: opacity 0.3s ease;
}

.stage-item.completed,
.stage-item.active {
    opacity: 1;
}

.stage-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: #27293d;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-shrink: 0;
}

.stage-item.completed .stage-icon {
    background-color: #2ecc71;
}

.stage-item.active .stage-icon {
    background-color: #3498db;
}

.stage-icon i {
    font-size: 18px;
    color: #ffffff;
}

.stage-info {
    flex: 1;
}

.stage-name {
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 4px;
}

.stage-description {
    color: #a9a9a9;
    font-size: 14px;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
}

.info-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.info-label {
    color: #a9a9a9;
    font-size: 12px;
}

.info-value {
    color: #ffffff;
    font-size: 14px;
}

.email-preview {
    background-color: #27293d;
    border-radius: 8px;
    overflow: hidden;
}

.email-header {
    padding: 16px;
    background-color: #1e1e2f;
    border-bottom: 1px solid #3a3a5c;
}

.email-field {
    margin-bottom: 8px;
}

.email-field:last-child {
    margin-bottom: 0;
}

.field-label {
    color: #a9a9a9;
    margin-right: 8px;
}

.field-value {
    color: #ffffff;
}

.email-body {
    padding: 16px;
    color: #ffffff;
}

.result-status {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
    padding: 12px;
    border-radius: 8px;
}

.result-status.success {
    background-color: rgba(46, 204, 113, 0.2);
    color: #2ecc71;
}

.result-status.failure {
    background-color: rgba(231, 76, 60, 0.2);
    color: #e74c3c;
}

.result-status i {
    font-size: 24px;
}

.result-details {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
}

.result-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.result-label {
    color: #a9a9a9;
    font-size: 12px;
}

.result-value {
    color: #ffffff;
    font-size: 14px;
}
</style>