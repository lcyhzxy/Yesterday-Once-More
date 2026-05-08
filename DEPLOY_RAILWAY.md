---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 30440220192e9e292253f32c41cae1a39951c73aa906dc54f2f61abb5875961c0d207e98022069fe0404e22f579b08d71e5768f8ba5f01f2441a651667d6ecbf20d2adeb4252
    ReservedCode2: 30460221008f4d8bf3521c5ef38e73ce4d45bdee88c29452efd709da6289f1835dee96bd0c022100cdda3eba2547a3e35707f521e9f5b388e79635ee1c0e29771f1ce2438b4571b1
---

# 时光重现后端服务 - Railway一键部署指南

## 部署到Railway（最简单方式）

### 步骤1：注册Railway账号
1. 访问 https://railway.app
2. 使用GitHub账号登录
3. 免费额度足够运行服务

### 步骤2：创建新项目
1. 点击 "New Project" → "Deploy from GitHub repo"
2. 连接你的GitHub仓库（将time-revival-backend文件夹作为独立仓库）
3. Railway会自动检测Python应用

### 步骤3：配置环境变量
在Railway控制台添加以下环境变量：
- `REPLICATE_API_TOKEN` = 你的Replicate API密钥
- `PORT` = 5000

### 步骤4：部署
1. 点击 "Deploy"
2. 等待构建完成
3. 获取公共URL（格式：https://your-app.railway.app）

### 步骤5：更新前端配置
在前端环境变量中设置：
```
VITE_API_URL=https://your-app.railway.app/api
```

## 或者：部署到Render

### 步骤1：创建Render账号
https://render.com

### 步骤2：创建Web Service
1. 连接GitHub仓库
2. 设置：
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Environment: Python 3.11

### 步骤3：添加环境变量
同Railway步骤3

### 步骤4：部署并获取URL

## Docker本地运行

如果想在本地运行后端：

```bash
cd time-revival-backend

# 构建镜像
docker build -t time-revival-backend .

# 运行容器
docker run -p 5000:5000 \
  -e REPLICATE_API_TOKEN=your_token_here \
  time-revival-backend
```

## 获取Replicate API密钥

1. 访问 https://replicate.com
2. 注册/登录账户
3. 进入 Dashboard → API Tokens
4. 复制Token并设置为环境变量

## 验证部署

部署成功后，访问：
```
https://your-backend-url.railway.app/api/health
```

应该返回：
```json
{
  "status": "healthy",
  "ai_configured": true
}
```

## 前端集成

更新前端应用的 `.env` 文件：
```env
VITE_API_URL=https://your-backend-url.railway.app/api
VITE_USE_LOCAL=false
```

然后重新构建并部署前端。

## 注意

- 免费Railway额度：500小时/月，足够个人使用
- Replicate免费额度：可生成少量视频测试
- 需要更高质量可升级到付费计划
