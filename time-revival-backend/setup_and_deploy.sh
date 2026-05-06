#!/bin/bash

# =====================================================
# Time Revival - 自动化 GitHub + Railway 部署脚本
# =====================================================

echo "╔════════════════════════════════════════════════════════╗"
echo "║  时光重现 - 一键部署到 GitHub + Railway               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查是否在正确的目录
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ 错误：未找到 app.py 文件${NC}"
    echo "   请确保在 time-revival-backend 目录中运行此脚本"
    exit 1
fi

echo -e "${GREEN}✅ 找到应用文件${NC}"
echo ""

# 步骤1: Git初始化
echo "📦 步骤1: 初始化Git仓库..."
echo "=================================="

if [ -d ".git" ]; then
    echo -e "${YELLOW}⚠️  Git仓库已存在，跳过初始化${NC}"
else
    git init
    echo -e "${GREEN}✅ Git仓库已初始化${NC}"
fi

# 创建 .gitignore
if [ ! -f ".gitignore" ]; then
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# 临时文件
*.log
*.tmp
.DS_Store

# 忽略大文件目录
uploads/
output/
temp/
EOF
    echo -e "${GREEN}✅ 已创建 .gitignore${NC}"
fi

echo ""

# 步骤2: 添加文件并提交
echo "📝 步骤2: 提交代码..."
echo "=================================="

git add .
git commit -m "✨ 初始提交: 时光重现 AI视频生成后端服务

- Flask REST API 服务
- OpenCV 视频生成
- 支持10种运动模式
- 支持10种视频风格
- Docker 支持
- Railway 部署配置"

echo -e "${GREEN}✅ 代码已提交${NC}"
echo ""

# 步骤3: 创建GitHub仓库
echo "🌐 步骤3: 创建GitHub仓库..."
echo "=================================="

read -p "请输入你的GitHub用户名: " GITHUB_USER
read -p "请确认你的仓库名称 (默认为 time-revival-backend): " REPO_NAME
REPO_NAME=${REPO_NAME:-time-revival-backend}

if [ -z "$GITHUB_USER" ]; then
    echo -e "${RED}❌ 用户名不能为空${NC}"
    exit 1
fi

REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"

echo ""
echo "📋 仓库信息："
echo "   用户名: $GITHUB_USER"
echo "   仓库名: $REPO_NAME"
echo "   URL: $REPO_URL"
echo ""

read -p "确认信息正确？按 Enter 继续，或按 Ctrl+C 取消..."

# 添加远程仓库
git remote add origin $REPO_URL 2>/dev/null || git remote set-url origin $REPO_URL

echo ""
echo -e "${YELLOW}⚠️  重要提示：${NC}"
echo ""
echo "请在浏览器中访问以下链接创建GitHub仓库："
echo -e "${BLUE}👉 https://github.com/new${NC}"
echo ""
echo "创建仓库时选择："
echo "   - Repository name: $REPO_NAME"
echo "   - Description: 时光重现 - AI照片视频生成后端服务"
echo "   - Private (推荐)"
echo "   - 不要勾选 'Add a README file'"
echo ""
read -p "创建完仓库后按 Enter 继续..."

# 推送代码
echo ""
echo "🚀 正在推送代码到GitHub..."
echo "=================================="

git branch -M main
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅✅✅ 代码已成功推送到GitHub！${NC}"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🎉 恭喜！现在请访问 Railway 部署："
    echo ""
    echo -e "${BLUE}👉 https://railway.app/new${NC}"
    echo ""
    echo "在 Railway 中："
    echo "   1. 点击 'Deploy from GitHub repo'"
    echo "   2. 选择 '$GITHUB_USER/$REPO_NAME'"
    echo "   3. Railway 自动检测并部署"
    echo "   4. 等待部署完成，获取API URL"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📖 详细文档："
    echo "   查看 GITHUB_RAILWAY_GUIDE.md 获取完整图文教程"
    echo ""
else
    echo ""
    echo -e "${RED}❌ 推送失败${NC}"
    echo ""
    echo "可能原因："
    echo "   1. GitHub认证失败"
    echo "   2. 仓库不存在"
    echo "   3. 网络问题"
    echo ""
    echo "解决方案："
    echo "   1. 访问 https://github.com/$GITHUB_USER/$REPO_NAME"
    echo "   2. 确保仓库已创建"
    echo "   3. 使用 Personal Access Token 认证"
    echo ""
fi

echo ""
echo "✨ 脚本执行完成！"
echo ""