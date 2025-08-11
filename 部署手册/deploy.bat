@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: AI Agent攻防推演平台 - Windows一键部署脚本

echo ========================================
echo AI Agent攻防推演平台 - 一键部署脚本
echo ========================================
echo.

:: 检查是否在正确目录
if not exist "..\package.json" (
    echo ❌ 错误: 请将此脚本放在项目根目录的部署手册文件夹中运行
    pause
    exit /b 1
)

if not exist "..\backend" (
    echo ❌ 错误: 未找到backend目录，请确认在正确的项目目录下
    pause
    exit /b 1
)

echo 🔍 1. 检查系统依赖...
echo.

:: 检查Docker
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Docker
    echo 请先安装Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
) else (
    echo ✅ Docker 已安装
)

:: 检查Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Node.js
    echo 请先安装Node.js: https://nodejs.org/
    pause
    exit /b 1
) else (
    echo ✅ Node.js 已安装
)

:: 检查NPM
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到NPM
    echo NPM通常随Node.js一起安装，请重新安装Node.js
    pause
    exit /b 1
) else (
    echo ✅ NPM 已安装
)

:: 检查Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Python
    echo 请先安装Python 3.9+: https://www.python.org/downloads/
    pause
    exit /b 1
) else (
    echo ✅ Python 已安装
)

:: 检查pip
where pip >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到pip
    echo pip通常随Python一起安装，请重新安装Python
    pause
    exit /b 1
) else (
    echo ✅ pip 已安装
)

echo.
echo 🚀 2. 安装前端依赖...
echo.

cd ..
npm install
if %errorlevel% neq 0 (
    echo ❌ 错误: 前端依赖安装失败
    echo 尝试清除缓存后重新安装...
    npm cache clean --force
    rmdir /s /q node_modules 2>nul
    del package-lock.json 2>nul
    npm install
    if %errorlevel% neq 0 (
        echo ❌ 前端依赖安装仍然失败，请检查网络连接
        cd 部署手册
        pause
        exit /b 1
    )
)
echo ✅ 前端依赖安装成功

echo.
echo 🐍 3. 安装Python依赖...
echo.

:: 安装全局依赖
if exist "requirements.txt" (
    echo 正在安装全局Python依赖...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ⚠️  全局依赖安装失败，尝试使用国内镜像源...
        pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
        if %errorlevel% neq 0 (
            echo ❌ 全局Python依赖安装失败
            cd 部署手册
            pause
            exit /b 1
        )
    )
    echo ✅ 全局Python依赖安装成功
)

:: 安装后端依赖
if exist "backend\requirements.txt" (
    echo 正在安装后端Python依赖...
    cd backend
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ⚠️  后端依赖安装失败，尝试使用国内镜像源...
        pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
        if %errorlevel% neq 0 (
            echo ❌ 后端Python依赖安装失败
            cd ..\部署手册
            pause
            exit /b 1
        )
    )
    cd ..
    echo ✅ 后端Python依赖安装成功
)

echo.
echo ⚙️  4. 检查环境配置...
echo.

:: 检查环境配置文件
if not exist "agents\scenario_agent\.env" (
    echo ⚠️  警告: 未找到agents\scenario_agent\.env文件
    echo.
    echo 请创建该文件并配置以下内容:
    echo DEEPSEEK_API_KEY=your_deepseek_api_key_here
    echo DEEPSEEK_BASE_URL=https://api.deepseek.com
    echo MODEL_NAME=deepseek-chat
    echo.
    
    set /p create_env="是否现在创建环境配置文件? (y/n): "
    if /i "!create_env!"=="y" (
        if not exist "agents\scenario_agent" mkdir "agents\scenario_agent"
        set /p api_key="请输入您的DeepSeek API密钥: "
        if not "!api_key!"=="" (
            echo DEEPSEEK_API_KEY=!api_key!> "agents\scenario_agent\.env"
            echo DEEPSEEK_BASE_URL=https://api.deepseek.com>> "agents\scenario_agent\.env"
            echo MODEL_NAME=deepseek-chat>> "agents\scenario_agent\.env"
            echo MAX_TOKENS=4000>> "agents\scenario_agent\.env"
            echo TEMPERATURE=0.7>> "agents\scenario_agent\.env"
            echo TIMEOUT=30>> "agents\scenario_agent\.env"
            echo ✅ 环境配置文件创建成功
        ) else (
            echo ⚠️  未输入API密钥，请稍后手动配置
        )
    ) else (
        echo ⚠️  请稍后手动创建环境配置文件
    )
) else (
    echo ✅ 环境配置文件已存在
)

echo.
echo 🚀 5. 启动服务...
echo.

if not exist "start_all_services.py" (
    echo ❌ 错误: 未找到start_all_services.py文件
    cd 部署手册
    pause
    exit /b 1
)

echo 正在启动所有服务...
echo.
echo 🌐 访问地址:
echo   前端界面: http://localhost:5173
echo   后端API: http://localhost:8080
echo   场景服务: http://localhost:8002
echo   场景智能体: http://localhost:8007
echo.
echo ⚠️  注意事项:
echo   1. 确保已配置DeepSeek API密钥
echo   2. 确保Docker已安装并运行
echo   3. 按Ctrl+C停止所有服务
echo.
echo ========================================
echo 🎉 部署完成! 正在启动服务...
echo ========================================
echo.

:: 启动服务
python start_all_services.py

cd 部署手册
pause
