#!/bin/bash

# AI Agent攻防推演平台 - Linux/macOS一键部署脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# 打印函数
print_header() {
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}========================================${NC}"
}

print_step() {
    echo -e "\n${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查命令是否存在
check_command() {
    if command -v $1 &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# 检查是否在正确目录
check_directory() {
    if [ ! -f "../package.json" ] || [ ! -d "../backend" ]; then
        print_error "请将此脚本放在项目根目录的部署手册文件夹中运行"
        exit 1
    fi
}

# 检查依赖
check_dependencies() {
    print_step "🔍 1. 检查系统依赖..."
    
    local missing_deps=()
    
    # 检查Docker
    if check_command docker; then
        print_success "Docker 已安装"
    else
        print_error "未找到Docker"
        missing_deps+=("Docker")
    fi
    
    # 检查Node.js
    if check_command node; then
        print_success "Node.js 已安装"
    else
        print_error "未找到Node.js"
        missing_deps+=("Node.js")
    fi
    
    # 检查NPM
    if check_command npm; then
        print_success "NPM 已安装"
    else
        print_error "未找到NPM"
        missing_deps+=("NPM")
    fi
    
    # 检查Python3
    if check_command python3; then
        print_success "Python3 已安装"
    else
        print_error "未找到Python3"
        missing_deps+=("Python3")
    fi
    
    # 检查pip3
    if check_command pip3; then
        print_success "pip3 已安装"
    else
        print_error "未找到pip3"
        missing_deps+=("pip3")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "缺少依赖: ${missing_deps[*]}"
        echo -e "${YELLOW}请安装缺少的依赖后重新运行部署脚本${NC}"
        
        # 提供安装建议
        echo -e "\n${CYAN}安装建议:${NC}"
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            echo "Ubuntu/Debian: sudo apt update && sudo apt install docker.io nodejs npm python3 python3-pip"
            echo "CentOS/RHEL: sudo yum install docker nodejs npm python3 python3-pip"
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            echo "macOS: brew install docker node python3"
        fi
        
        exit 1
    fi
}

# 安装前端依赖
install_frontend_deps() {
    print_step "🚀 2. 安装前端依赖..."
    
    cd ..
    
    echo "正在安装前端依赖..."
    if npm install; then
        print_success "前端依赖安装成功"
    else
        print_warning "前端依赖安装失败，尝试清除缓存后重新安装..."
        npm cache clean --force
        rm -rf node_modules package-lock.json
        if npm install; then
            print_success "前端依赖安装成功"
        else
            print_error "前端依赖安装失败，请检查网络连接"
            cd 部署手册
            exit 1
        fi
    fi
    
    cd 部署手册
}

# 安装Python依赖
install_python_deps() {
    print_step "🐍 3. 安装Python依赖..."
    
    cd ..
    
    # 安装全局依赖
    if [ -f "requirements.txt" ]; then
        echo "正在安装全局Python依赖..."
        if pip3 install -r requirements.txt; then
            print_success "全局Python依赖安装成功"
        else
            print_warning "全局依赖安装失败，尝试使用国内镜像源..."
            if pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/; then
                print_success "全局Python依赖安装成功"
            else
                print_error "全局Python依赖安装失败"
                cd 部署手册
                exit 1
            fi
        fi
    fi
    
    # 安装后端依赖
    if [ -f "backend/requirements.txt" ]; then
        echo "正在安装后端Python依赖..."
        cd backend
        if pip3 install -r requirements.txt; then
            print_success "后端Python依赖安装成功"
        else
            print_warning "后端依赖安装失败，尝试使用国内镜像源..."
            if pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/; then
                print_success "后端Python依赖安装成功"
            else
                print_error "后端Python依赖安装失败"
                cd ../部署手册
                exit 1
            fi
        fi
        cd ..
    fi
    
    cd 部署手册
}

# 检查环境配置
check_env_config() {
    print_step "⚙️  4. 检查环境配置..."
    
    cd ..
    
    if [ ! -f "agents/scenario_agent/.env" ]; then
        print_warning "未找到agents/scenario_agent/.env文件"
        echo
        echo -e "${YELLOW}请创建该文件并配置以下内容:${NC}"
        echo -e "${CYAN}DEEPSEEK_API_KEY=your_deepseek_api_key_here"
        echo -e "DEEPSEEK_BASE_URL=https://api.deepseek.com"
        echo -e "MODEL_NAME=deepseek-chat${NC}"
        echo
        
        read -p "是否现在创建环境配置文件? (y/n): " create_env
        if [[ $create_env =~ ^[Yy]$ ]]; then
            mkdir -p "agents/scenario_agent"
            read -p "请输入您的DeepSeek API密钥: " api_key
            if [ ! -z "$api_key" ]; then
                cat > "agents/scenario_agent/.env" << EOF
DEEPSEEK_API_KEY=$api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
MODEL_NAME=deepseek-chat
MAX_TOKENS=4000
TEMPERATURE=0.7
TIMEOUT=30
EOF
                print_success "环境配置文件创建成功"
            else
                print_warning "未输入API密钥，请稍后手动配置"
            fi
        else
            print_warning "请稍后手动创建环境配置文件"
        fi
    else
        print_success "环境配置文件已存在"
    fi
    
    cd 部署手册
}

# 启动服务
start_services() {
    print_step "🚀 5. 启动服务..."
    
    cd ..
    
    if [ ! -f "start_all_services.py" ]; then
        print_error "未找到start_all_services.py文件"
        cd 部署手册
        exit 1
    fi
    
    echo "正在启动所有服务..."
    echo
    echo -e "${GREEN}🌐 访问地址:${NC}"
    echo -e "${GREEN}  前端界面: http://localhost:5173${NC}"
    echo -e "${GREEN}  后端API: http://localhost:8080${NC}"
    echo -e "${GREEN}  场景服务: http://localhost:8002${NC}"
    echo -e "${GREEN}  场景智能体: http://localhost:8007${NC}"
    echo
    echo -e "${YELLOW}⚠️  注意事项:${NC}"
    echo -e "${YELLOW}  1. 确保已配置DeepSeek API密钥${NC}"
    echo -e "${YELLOW}  2. 确保Docker已安装并运行${NC}"
    echo -e "${YELLOW}  3. 按Ctrl+C停止所有服务${NC}"
    echo
    
    print_header "🎉 部署完成! 正在启动服务..."
    echo
    
    # 启动服务
    python3 start_all_services.py
    
    cd 部署手册
}

# 主函数
main() {
    print_header "AI Agent攻防推演平台 - 一键部署脚本"
    echo -e "${CYAN}操作系统: $(uname -s) $(uname -r)${NC}"
    echo -e "${CYAN}Python版本: $(python3 --version)${NC}"
    
    # 检查目录
    check_directory
    
    # 执行部署步骤
    check_dependencies
    install_frontend_deps
    install_python_deps
    check_env_config
    start_services
}

# 设置脚本权限
chmod +x "$0"

# 捕获中断信号
trap 'echo -e "\n\n${YELLOW}部署被用户中断${NC}"; exit 0' INT

# 运行主函数
main "$@"
