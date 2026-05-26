# 🚀 快速启动指南

## 步骤 1：激活 Conda 环境

```bash
conda activate chatchat
```

## 步骤 2：安装缺失的依赖

```bash
cd c:\Users\YeeCham\Desktop\chatchat\Langchain-Chatchat

# 安装 langserve（重要！）
pip install langserve

# 验证安装
pip list | grep langserve
```

## 步骤 3：启动后端服务（新终端窗口）

### 方式 A：直接运行（推荐）

```bash
cd c:\Users\YeeCham\Desktop\chatchat\Langchain-Chatchat
python server/api.py --port 7861
```

### 方式 B：使用启动脚本

```bash
cd c:\Users\YeeCham\Desktop\chatchat\Langchain-Chatchat
python run_backend.py
```

**等待输出类似信息：**
```
INFO:     Uvicorn running on http://0.0.0.0:7861
```

✅ 访问 http://localhost:7861/docs 验证后端

## 步骤 4：启动前端服务（另一个新终端窗口）

```bash
cd c:\Users\YeeCham\Desktop\chatchat\Langchain-Chatchat\frontend_vue
npm run dev
```

**等待输出类似信息：**
```
Local:        http://localhost:5173/
```

✅ 访问 http://localhost:5173 即可使用前端

## 🎯 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端应用 | http://localhost:5173 | Vue 3 应用入口 |
| 后端 API 文档 | http://localhost:7861/docs | Swagger 交互文档 |
| 后端 API | http://localhost:7861 | API 基础地址 |

## ⚠️ 常见问题

### 问题 1：后端启动失败 "Address already in use"

```bash
# 查找占用 7861 端口的进程
netstat -ano | findstr :7861

# 杀死进程（替换 PID）
taskkill /PID <PID> /F
```

### 问题 2：前端无法连接后端

✅ 确保后端服务已启动（检查 http://localhost:7861/docs）
✅ 检查前端代码中的 API 地址是否正确
✅ 检查防火墙设置

### 问题 3：npm 找不到命令

```bash
# 重新安装 Node.js 和 npm
# 从 https://nodejs.org/ 下载安装
node --version
npm --version
```

## 🧪 功能测试

### 1. 测试用户注册
- 访问 http://localhost:5173
- 切换到"注册"标签
- 输入用户名和密码
- 点击注册按钮

### 2. 测试登录
- 使用刚才注册的用户名和密码
- 点击登录

### 3. 测试对话
- 点击"时间"、"日期"等按钮测试 Tool 功能
- 在输入框输入问题进行对话

### 4. 测试知识库
- 点击"📚 知识库"按钮
- 上传 PDF、TXT 或 DOCX 文件
- 查询已上传文档

---

**如有问题，请检查终端日志！** 📋
