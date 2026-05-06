---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3046022100f6ca9d12a425dd8ee743f961861493b4f5f4f443a4b8c5bf3757a28c7d011d2402210082009bcea3cb2c4b479faf84d04bf7d387f1a67d8f326266da09978f8cc45403
    ReservedCode2: 3046022100a8728ffcf14b3bc171808b6070f656a52038ac12f223e03ff488f1781d5310ad022100dd89aed0ce6d043ca3747492086a6e9c4c824ae69ff091952a8406a839415aa9
---

# 🚀 Railway 部署完整指南 - 图文教程

## 📋 前置条件

- GitHub 账号：https://github.com
- Railway 账号：https://railway.app（使用GitHub登录）

---

## 第一步：初始化Git仓库并推送到GitHub

### 1.1 在后端目录初始化Git

打开终端，执行以下命令：

```bash
cd /workspace/time-revival-backend

# 初始化Git仓库
git init

# 添加所有文件（排除临时文件）
git add .

# 提交代码
git commit -m "Initial commit: Time Revival Backend"

# 创建主分支
git branch -M main
```

### 1.2 创建GitHub仓库

1. 打开浏览器访问：https://github.com
2. 点击右上角 **"+"** 按钮
3. 选择 **"New repository"**
4. 填写仓库信息：
   - **Repository name**: `time-revival-backend`
   - **Description**: `时光重现 - AI照片视频生成后端服务`
   - **选择 Private**（私有仓库）
   - **不要**勾选 "Add a README file"（我们已经有了）
5. 点击 **"Create repository"**

### 1.3 推送代码到GitHub

在创建仓库后，GitHub会显示仓库地址，复制它并执行：

```bash
cd /workspace/time-revival-backend

# 添加远程仓库（将 YOUR_USERNAME 替换为你的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/time-revival-backend.git

# 推送代码
git push -u origin main
```

⚠️ **注意**：如果遇到认证问题，可能需要使用Personal Access Token作为密码。

---

## 第二步：部署到Railway

### 2.1 登录Railway

1. 打开浏览器访问：https://railway.app
2. 点击 **"Login with GitHub"** 按钮
3. 授权 Railway 访问你的 GitHub 仓库

### 2.2 创建新项目

1. 在 Railway 控制台，点击 **"New Project"**
2. 选择 **"Deploy from GitHub repo"**
   ![选择 Deploy from GitHub repo](https://docs.railway.app/_next/static/media/new-project-github.ed36f5a.png)

### 2.3 选择仓库

1. 在仓库列表中找到 `YOUR_USERNAME/time-revival-backend`
2. 点击它以选中
3. Railway 会自动检测这是一个 Python/Flask 应用
4. 点击 **"Deploy Now"** 开始部署
   ![点击 Deploy Now](https://docs.railway.app/_next/static/media/deploy-now.0c4b5de.png)

### 2.4 等待部署完成

部署过程通常需要 **2-5分钟**，你会看到：
- 实时构建日志
- 进度条显示
- 状态更新

当看到 **"Deployed"** 绿色标记时，表示部署成功！

### 2.5 获取API URL

部署完成后，Railway会提供一个公共URL，格式类似：
```
https://time-revival-backend-production.up.railway.app
```

这就是你的后端API地址！

---

## 第三步：验证后端部署

### 3.1 健康检查

在浏览器中访问：
```
https://你的后端URL/api/health
```

应该看到类似这样的响应：
```json
{
  "status": "healthy",
  "service": "Time Revival Backend",
  "version": "2.0.0"
}
```

### 3.2 查看API文档

访问：
```
https://你的后端URL/
```

应该看到API文档页面。

---

## 第四步：配置前端连接后端

### 4.1 创建前端环境变量文件

在后端部署成功并获得URL后，在前端项目创建文件：

**创建文件：** `time-revival/.env`

```env
VITE_API_URL=https://你的后端URL
```

### 4.2 重新构建前端

```bash
cd time-revival

# 重新构建
pnpm build

# 重新部署（使用deploy工具）
```

### 4.3 测试完整功能

1. 访问前端应用
2. 选择 **"AI云端生成"** 模式
3. 上传照片
4. 生成视频

---

## 🎯 快速检查清单

- [ ] GitHub 账号已创建
- [ ] Railway 账号已创建（使用GitHub登录）
- [ ] Git 仓库已初始化
- [ ] 代码已推送到 GitHub
- [ ] Railway 项目已创建
- [ ] 部署已完成
- [ ] 获取到 API URL
- [ ] 前端已配置并重新部署

---

## ⚠️ 常见问题解决

### 问题1：Push 到 GitHub 失败

**错误信息**：`Permission denied (publickey)` 或 `Authentication failed`

**解决方法**：
1. 访问 https://github.com/settings/tokens
2. 创建 Personal Access Token（Classic）
3. 选择 `repo` 权限
4. 复制 token
5. 当 GitHub 要求密码时，粘贴这个 token（不是密码）

```bash
git push -u origin main
# Username: YOUR_USERNAME
# Password: 粘贴 Personal Access Token
```

### 问题2：Railway 部署失败

**检查事项**：
1. ✅ requirements.txt 文件存在
2. ✅ Dockerfile 语法正确
3. ✅ 所有依赖都能正常安装

**查看日志**：
在 Railway 控制台，点击部署记录，查看详细错误日志。

### 问题3：API 调用失败

**检查事项**：
1. ✅ 后端服务是否启动？
2. ✅ API URL 是否正确？
3. ✅ CORS 配置是否正确？

**测试方法**：
```bash
# 在终端测试
curl https://你的后端URL/api/health
```

### 问题4：找不到仓库

**解决方法**：
1. 确认 Railway 已授权访问该仓库
2. 在 Railway 控制台：Settings → Connected Accounts → 检查 GitHub 权限
3. 刷新页面

---

## 📞 获取帮助

如果遇到问题：

1. **Railway 文档**: https://docs.railway.app
2. **GitHub 帮助**: https://help.github.com
3. **提交Issue**: 在仓库中创建Issue描述问题

---

## ✨ 部署成功后的下一步

恭喜！如果一切顺利，你已经完成了：

1. ✅ 后端代码已推送到GitHub
2. ✅ 后端服务已部署到Railway
3. ✅ 获取到API URL
4. ⏳ 前端需要重新配置

现在需要：
1. 复制Railway提供的API URL
2. 更新前端 `.env` 文件
3. 重新构建并部署前端

然后就可以享受完整功能了！

---

**有问题随时问我！** 🚀