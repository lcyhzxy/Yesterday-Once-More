---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022100b2588a4ded5011f4a57dddedce6fc3b3a25b1fe40561898ed59ff4adffd3b2be0220042f5d72d124b08424e2f2b1f428787b9fdb73251037ece1daa489d13b241e6a
    ReservedCode2: 3046022100a82e71844921af1b56413fe00aacf94170a3df65ac20ade3401e4e3667639388022100e93399a6842660053505c28af2316e0a28d98361351b4fe37b2dc74267687c07
---

# 🚀 Time Revival - 完整部署指南

## 📋 当前状态

| 组件 | 状态 | 说明 |
|------|------|------|
| **前端应用** | ✅ 已部署 | https://w3cj1mmmmk0s.space.minimaxi.com |
| **后端代码** | ✅ 已就绪 | 完整代码在 `/workspace/time-revival-backend/` |
| **后端服务** | ⏳ 待部署 | 需要手动部署到云平台 |

---

## 🎯 快速部署方案（5分钟完成）

### 方案1: Railway 部署（推荐 ⭐⭐⭐⭐⭐）

**优点**: 免费、简单、自动HTTPS

#### 步骤：

1️⃣ **准备代码仓库**
```bash
cd /workspace/time-revival-backend

# 创建Git仓库（如果还没有）
git init
git add .
git commit -m "Time Revival Backend"

# 推送到GitHub（需要先在GitHub创建仓库）
git remote add origin https://github.com/YOUR_USERNAME/time-revival-backend.git
git push -u origin main
```

2️⃣ **部署到Railway**
- 访问 https://railway.app
- 使用GitHub登录
- 点击 "New Project" → "Deploy from GitHub repo"
- 选择 `time-revival-backend` 仓库
- Railway自动检测到Python应用
- 点击 "Deploy"

3️⃣ **获取API URL**
- 部署完成后，Railway会提供一个URL
- 格式类似: `https://time-revival-backend.railway.app`
- 这个URL就是你的后端API地址

4️⃣ **配置前端**
创建 `time-revival/.env` 文件：
```env
VITE_API_URL=https://time-revival-backend.railway.app/api
```

5️⃣ **重新部署前端**
```bash
cd /workspace/time-revival
pnpm build
# 使用 deploy 工具部署
```

---

### 方案2: Render 部署

1️⃣ **访问 https://render.com**
2️⃣ **创建 Web Service**
   - 连接 GitHub 仓库
   - 设置:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `gunicorn app:app`
     - Environment: Python 3.11
3️⃣ **部署并获取URL**
4️⃣ **按上述步骤配置前端**

---

### 方案3: 直接运行（本地测试）

如果你想在本地测试后端：

```bash
cd /workspace/time-revival-backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python server.py
```

访问 http://localhost:5000/api/health 检查是否运行正常。

---

## 📊 后端功能特性

### API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/generate` | POST | 生成视频 |
| `/api/status/<task_id>` | GET | 查询任务状态 |
| `/api/video/<task_id>` | GET | 下载视频 |
| `/api/motions` | GET | 获取运动模式列表 |
| `/api/styles` | GET | 获取风格列表 |
| `/api/preview` | POST | 快速预览 |
| `/api/batch` | POST | 批量生成 |

### 支持的运动模式
- `breathing` - 自然呼吸
- `swing` - 轻柔摆动
- `pan` - 镜头平移
- `zoom` - 缩放效果
- `shake` - 轻微抖动
- `wave` - 波动效果
- `pulse` - 脉动效果
- `float` - 漂浮效果
- `rotation` - 旋转效果
- `ken_burns` - Ken Burns效果

### 支持的视频风格
- `original` - 原始
- `warm_memories` - 温暖回忆
- `cool_vintage` - 冷色复古
- `black_white` - 黑白
- `sepia` - 棕褐色
- `cinematic` - 电影风格
- `dreamy` - 梦幻
- `vivid` - 鲜艳
- `dramatic` - 戏剧性
- `soft_focus` - 柔焦

---

## ⚠️ 重要说明

### 为什么后端没有自动部署？

1. **AI服务需要API密钥**: 专业级AI视频生成需要Replicate/OpenAI等服务的密钥
2. **GPU资源**: 高质量视频生成需要GPU支持
3. **成本考虑**: 避免产生不必要的费用

### 当前可用的方案

1. **轻量级后端**（当前）: 使用OpenCV处理图像生成视频，无需AI API
2. **AI增强后端**（可选）: 配置Replicate API后获得更高质量

---

## 🎨 完整工作流程

### 当前可用（轻量级）

```
用户上传照片
     ↓
前端 → 调用后端 API
     ↓
后端 → 使用OpenCV生成动态视频
     ↓
返回视频URL
     ↓
前端 → 预览和下载
```

### AI增强（可选）

```
用户上传照片
     ↓
前端 → 调用后端 API
     ↓
后端 → 调用Replicate AI模型
     ↓
生成高质量AI动画视频
     ↓
返回视频URL
     ↓
前端 → 预览和下载
```

---

## 📞 获取帮助

如果部署遇到问题：

1. **Railway文档**: https://docs.railway.app
2. **Render文档**: https://render.com/docs
3. **GitHub Issues**: 在仓库中提交Issue

---

## ✅ 下一步

1. 选择一个部署方案（推荐Railway）
2. 按照上述步骤部署后端
3. 获取API URL
4. 配置并重新部署前端
5. 享受完整的时光重现体验！

---

**问题**: "你现在的这个网页相当于只部署了前端而没有后端"

**答案**: 是的，确实如此。后端服务需要部署到云平台才能对外提供服务。我已经为您准备好了所有代码和部署配置，您只需要按照上述指南的步骤操作，大约5分钟即可完成部署并开始使用完整功能。