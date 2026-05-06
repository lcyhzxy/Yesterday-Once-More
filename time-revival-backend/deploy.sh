#!/bin/bash

# 时光重现 - 一键部署脚本
# 支持 Railway、Render 或任何支持 Dockerfile 的平台

set -e

echo "=========================================="
echo "时光重现 AI视频生成系统 - 部署脚本"
echo "=========================================="
echo ""

# 检查依赖
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

if ! command_exists docker; then
    echo "❌ Docker 未安装，请安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker 已安装"
echo ""

# 部署选项
echo "请选择部署平台："
echo "1) Railway (推荐 - 最简单)"
echo "2) Render"
echo "3) 本地Docker"
echo "4) 直接运行 (开发模式)"
echo ""
read -p "请输入选项 [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "部署到 Railway..."
        echo ""
        echo "步骤："
        echo "1. 访问 https://railway.app 并登录"
        echo "2. 点击 'New Project' → 'Deploy from GitHub repo'"
        echo "3. 连接包含此文件的仓库"
        echo "4. Railway 会自动检测 Dockerfile"
        echo "5. 在环境变量中添加任何必要的配置"
        echo "6. 点击 'Deploy'"
        echo ""
        echo "📖 详细指南: https://railway.app/docs"
        echo ""
        echo "⚡ 快速开始："
        echo "   railway login"
        echo "   railway init"
        echo "   railway up"
        echo ""
        ;;
    2)
        echo ""
        echo "部署到 Render..."
        echo ""
        echo "步骤："
        echo "1. 访问 https://render.com 并登录"
        echo "2. 点击 'New' → 'Web Service'"
        echo "3. 连接 GitHub 仓库"
        echo "4. 设置："
        echo "   - Build Command: pip install -r requirements.txt"
        echo "   - Start Command: gunicorn app:app"
        echo "   - Environment: Python 3.11"
        echo "5. 添加环境变量"
        echo "6. 点击 'Create Web Service'"
        echo ""
        echo "📖 详细指南: https://render.com/docs/deploy-python-flask"
        echo ""
        ;;
    3)
        echo ""
        echo "本地Docker部署..."
        echo ""

        # 构建Docker镜像
        echo "🔨 构建Docker镜像..."
        docker build -t time-revival-backend .

        # 运行容器
        echo ""
        echo "🚀 启动容器..."
        echo "   端口映射: 5000:5000"
        docker run -d \
            --name time-revival-backend \
            -p 5000:5000 \
            -e FLASK_ENV=production \
            time-revival-backend

        echo ""
        echo "✅ 部署完成！"
        echo "   服务地址: http://localhost:5000"
        echo "   API文档: http://localhost:5000/api/health"
        echo ""
        echo "常用命令："
        echo "   查看日志: docker logs -f time-revival-backend"
        echo "   停止服务: docker stop time-revival-backend"
        echo "   删除容器: docker rm time-revival-backend"
        echo ""
        ;;
    4)
        echo ""
        echo "开发模式启动..."
        echo ""

        # 安装依赖
        echo "📦 安装Python依赖..."
        if command_exists pip; then
            pip install -r requirements.txt
        elif command_exists pip3; then
            pip3 install -r requirements.txt
        else
            echo "❌ pip 未安装，请先安装 Python 3.11+"
            exit 1
        fi

        echo ""
        echo "🚀 启动开发服务器..."
        echo "   服务地址: http://localhost:5000"
        echo "   按 Ctrl+C 停止"
        echo ""
        python app.py
        ;;
    *)
        echo ""
        echo "❌ 无效选项"
        exit 1
        ;;
esac

echo "=========================================="
echo "部署完成！"
echo "=========================================="