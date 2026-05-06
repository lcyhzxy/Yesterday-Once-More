---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3046022100b9e487cbad773253fa9d65336dc86babd389acf77af2d707162a79472059be7b022100cc86411aaf7d4a6db79e228689ae96eff3a7865f458d419d04b7e470f5c21fc6
    ReservedCode2: 304502207e0a6c86f6c69bd1c62b67e4cecb6556b298728440399ca6989cdeb265159a460221008d0941e93d6cdd273adce557b0d86bbee34234e859ffebafc2f8ba7190b15f98
---

# 时光重现 - AI照片视频生成系统

## 项目简介

这是一个完整的AI照片视频生成系统，专门设计用于帮助用户将静态照片转化为动态视频，特别适合希望重温珍贵回忆的用户群体。

## 系统架构

```
┌─────────────┐
│   前端      │   React + TypeScript
│   (Web)     │   用户界面和交互
└──────┬──────┘
       │
       │ HTTP REST API
       ↓
┌─────────────┐
│   后端      │   Python Flask
│   API       │   业务逻辑处理
└──────┬──────┘
       │
       │ AI Model API
       ↓
┌─────────────┐
│   AI服务    │   Replicate / 阿里云 / 腾讯云
│   提供商    │   专业AI视频生成模型
└─────────────┘
```

## 技术栈

### 前端
- React 18 + TypeScript
- Vite
- Tailwind CSS
- Lucide React图标库

### 后端
- Python 3.11
- Flask 3.0
- Replicate API (AI视频生成)
- Pillow (图片处理)
- Gunicorn (生产服务器)

## 快速开始

### 方式一：Docker部署（推荐）

1. 克隆项目并进入后端目录
```bash
cd time-revival-backend
```

2. 创建环境变量文件
```bash
cp .env.example .env
```

3. 编辑.env文件，添加你的API密钥
```env
REPLICATE_API_TOKEN=your_replicate_api_token_here
```

4. 启动服务
```bash
docker-compose up -d
```

5. 访问应用
- 前端：http://localhost
- 后端API：http://localhost:5000

### 方式二：手动部署

#### 后端设置

1. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 设置环境变量
```bash
export REPLICATE_API_TOKEN=your_token_here  # Linux/Mac
set REPLICATE_API_TOKEN=your_token_here    # Windows
```

4. 运行后端
```bash
python app.py
# 或用于生产环境
gunicorn -b 0.0.0.0:5000 -w 2 --timeout 300 app:app
```

#### 前端设置

1. 进入前端目录
```bash
cd time-revival
```

2. 安装依赖
```bash
pnpm install
```

3. 运行开发服务器
```bash
pnpm dev
```

## 获取API密钥

### Replicate API
1. 访问 https://replicate.com
2. 注册账户
3. 在Dashboard中获取API Token
4. Replicate提供免费额度，可以生成多个视频

### 替代AI服务
如果需要更高质量的结果，可以考虑：

1. **阿里云视频生成API**
   - 访问 https://help.aliyun.com/document_detail
   - 注册阿里云账户
   - 开通视觉智能服务

2. **腾讯混元视频**
   - 访问 https://cloud.tencent.com
   - 使用腾讯云服务

3. **Runway API**
   - 访问 https://runwayml.com
   - 提供专业的视频生成API

## API文档

### 基础信息
- 基础URL: `http://localhost:5000/api`
- 认证方式: API Token (通过环境变量配置)

### 端点

#### 1. 健康检查
```
GET /api/health
```

响应:
```json
{
  "status": "healthy",
  "service": "时光重现 AI视频生成服务",
  "version": "2.0.0",
  "replicate_configured": true
}
```

#### 2. 生成视频
```
POST /api/generate
Content-Type: multipart/form-data

参数:
- image: 图片文件 (必需)
- motion_mode: 运动模式 (可选, 默认: breathing)
- duration: 时长，秒 (可选, 默认: 5)
- style: 风格 (可选, 默认: natural)

运动模式选项:
- breathing: 自然呼吸
- gentle-sway: 轻柔摆动
- smile: 微笑重现
- memory-flow: 回忆流转

风格选项:
- natural: 自然真实
- warm-memory: 温暖回忆
- black-white: 黑白时光
- soft-light: 柔和光影
```

响应:
```json
{
  "success": true,
  "video_url": "https://replicate.com/api/output/video.mp4",
  "model": "Zeroscope v2"
}
```

#### 3. 高级生成
```
POST /api/advanced-generate
Content-Type: application/json

参数:
{
  "image_base64": "base64编码的图片",
  "motion_mode": "breathing",
  "duration": 5,
  "style": "natural",
  "quality": "high",
  "custom_prompt": "自定义提示词（可选）"
}
```

#### 4. 查询模型
```
GET /api/models
```

响应:
```json
{
  "models": [
    {
      "id": "zeroscope-v2",
      "name": "Zeroscope v2",
      "description": "高质量视频生成模型",
      "supports_duration": [3, 5, 10],
      "max_resolution": "1024x1024"
    }
  ]
}
```

## 前端集成

前端代码会自动调用后端API。确保：

1. 后端服务正在运行在 http://localhost:5000
2. 前端的API配置指向正确的后端地址
3. CORS配置允许跨域请求

## 配置说明

### 环境变量

| 变量名 | 必需 | 说明 |
|--------|------|------|
| REPLICATE_API_TOKEN | 是 | Replicate API密钥 |
| FLASK_ENV | 否 | 运行环境 (development/production) |
| MAX_CONTENT_LENGTH | 否 | 最大上传文件大小（字节）|

### 性能优化

1. **GPU加速**: AI模型在GPU上运行更快
2. **并发处理**: 可以启动多个worker处理请求
3. **缓存**: 可以添加Redis缓存常见请求

## 故障排查

### 常见问题

1. **API Token无效**
   - 检查环境变量是否正确设置
   - 确认Token未过期

2. **上传失败**
   - 检查文件大小是否超过限制
   - 确认文件格式正确

3. **视频生成慢**
   - GPU比CPU快很多
   - 减小图片尺寸
   - 使用较短的时长

4. **CORS错误**
   - 确认后端CORS配置正确
   - 检查前端API地址配置

## 部署到生产环境

### 使用Docker Compose
```bash
# 构建并启动
docker-compose -f docker-compose.prod.yml up -d

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 停止服务
docker-compose -f docker-compose.prod.yml down
```

### 云平台部署

#### AWS
1. 使用EC2实例
2. 配置安全组允许HTTP流量
3. 使用ECR存储Docker镜像

#### Google Cloud
1. 使用Cloud Run
2. 配置Artifact Registry
3. 设置环境变量

#### 阿里云
1. 使用ECS或函数计算
2. 配置容器镜像服务
3. 设置VPC和网络

## 许可协议

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请联系开发团队。

---

**让科技守护珍贵回忆 - 时光重现**
