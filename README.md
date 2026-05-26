---
title: Langchain-Chatchat - RAG 知识库问答系统
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.30.0
app_file: webui.py
pinned: false
---

# 🤖 Langchain-Chatchat 知识库问答系统

基于 `LangChain` 的 RAG（检索增强生成）问答系统，支持用户认证、知识库管理、Agent 工具调用、对话历史持久化和 LangServe 标准服务部署。

> 建议：如果你要做课程展示，可在本节下方插入项目主页截图、登录页截图、聊天页截图。

---

## 🔒 开源项目标注声明

本项目基于开源项目二次开发：


| 项目信息   | 详情                                                                         |
| ------ | -------------------------------------------------------------------------- |
| 原始项目   | [Langchain-Chatchat](https://github.com/chatchat-space/Langchain-Chatchat) |
| 原始许可证  | Apache License 2.0                                                         |
| 二次开发团队 | 第 X 组                                                                      |


本仓库在原项目基础上新增/强化了以下能力：

- ✅ 用户认证模块（注册、登录、Token 校验）
- ✅ 独立 Vue 3 前端应用（前后端分离）
- ✅ 对话历史持久化（SQLite）
- ✅ Agent 工具调用能力（搜索、计算、日期、论文检索等）
- ✅ 知识库管理界面（创建、上传、查看、删除）
- ✅ LangServe 部署（Playground / Invoke / Stream）

---

## ✅ 作业要求符合性


| 序号  | 作业要求                            | 状态  | 说明                                           |
| --- | ------------------------------- | --- | -------------------------------------------- |
| 1   | 基于 LangChain 框架开发               | ✅   | 使用 `langchain==0.0.354`                      |
| 2   | LLM 调用、Prompt、Chain、Memory、Tool | ✅   | 核心能力均已实现                                     |
| 3   | 前后端分离架构，后端支持 LangServe 部署       | ✅   | `add_routes` 已部署，支持 Playground/Invoke/Stream |
| 4   | 前端注册、登录、数据查询                    | ✅   | Vue 前端接入认证、聊天、历史、知识库接口                       |
| 5   | GitHub 上传及云端部署                  | ✅   | 已具备部署能力，按实际仓库远程地址执行推送                        |
| 6   | 开源项目出处标注                        | ✅   | 已在本 README 标注                                |
| 7   | 内容符合法律法规                        | ✅   | 默认合规                                         |


---

## 🎯 功能特性

### 核心能力

- 智能问答：支持通用 LLM 对话
- RAG 文档问答：基于知识库检索结果生成回答
- 多工具 Agent：支持搜索、计算、日期、论文检索等
- 对话历史：按用户持久化存储并可回看

### 用户侧能力

- 注册/登录与 Token 会话
- 知识库创建、文档上传、文档删除
- 普通问答与 RAG 问答一键切换

### 文档格式支持

- `PDF`
- `TXT`
- `DOCX`

---

## 🛠️ 技术栈


| 分类       | 技术           | 版本      | 说明                   |
| -------- | ------------ | ------- | -------------------- |
| 后端框架     | FastAPI      | 0.136.3 | API 网关与业务接口          |
| LLM 应用框架 | LangChain    | 0.0.354 | Chain/Memory/Tool 编排 |
| 服务部署     | LangServe    | 0.0.52  | 标准化链路服务              |
| 向量检索     | FAISS        | 1.7.4   | 知识库向量检索              |
| 模型服务     | 智谱 AI        | glm-4   | 默认在线模型               |
| 前端框架     | Vue 3        | 3.x     | 前端页面与交互              |
| UI 组件    | Element Plus | 2.x     | 前端组件库                |
| 数据库      | SQLite       | -       | 用户与历史记录存储            |
| 部署       | Docker       | -       | 容器化部署                |


---

## 🏗️ 系统架构

```text
前端层 (Vue 3)
  ├─ Login.vue      用户登录/注册
  └─ Chat.vue       对话、工具调用、知识库管理、历史查看
           │
           ▼
业务 API 层 (FastAPI, :7861)
  ├─ /auth/*                  用户认证与历史
  ├─ /chat/*                  普通对话/RAG对话/Agent对话
  └─ /knowledge_base/*        知识库与文档管理
           │
           ▼
能力层
  ├─ LangChain Chain / Memory / Tools
  ├─ FAISS 向量库
  └─ LangServe (:8000, /chat/playground /chat/invoke /chat/stream)
```

---

## 📁 项目结构

```text
Langchain-Chatchat/
├── server/
│   ├── api.py                        # 主 API 入口（7861）
│   ├── user_auth.py                  # 用户认证与历史
│   ├── chat/
│   │   ├── chat.py                   # 普通对话
│   │   ├── knowledge_base_chat.py    # RAG 对话
│   │   └── agent_chat.py             # Agent 对话
│   ├── agent/tools/                  # 工具集合
│   ├── memory/
│   ├── knowledge_base/
│   └── db/
├── frontend_vue/
│   ├── src/views/Login.vue
│   ├── src/views/Chat.vue
│   └── vite.config.js
├── configs/
├── langserve_chain.py                # LangServe 服务（8000）
├── start_server.py                   # 后端一键拉起脚本（推荐）
├── startup.py                        # 原项目多进程启动脚本
├── requirements.txt
└── README.md
```

---

## 🚀 快速开始

### 1) 环境要求

- Python 3.10+
- Node.js 18+（前端）
- 建议使用 Conda 或 venv

### 2) 克隆项目

```bash
git clone https://github.com/zoeya11/Langchain-Chatchat.git
cd Langchain-Chatchat
```

### 3) 安装依赖

```bash
pip install -r requirements.txt
pip install -r requirements_api.txt
```

前端依赖：

```bash
cd frontend_vue
npm install
cd ..
```

### 4) 配置模型 API Key

```bash
python copy_config_example.py
```

然后编辑 `configs/model_config.py`，为 `zhipu-api` 配置 `api_key`，或设置环境变量：

```bash
set ZHIPU_API_KEY=your-api-key
```

### 5) 启动服务

方式 A（推荐，自动启动主 API + LangServe）：

```bash
python start_server.py
```

方式 B（手动分开启动）：

```bash
python startup.py --all-api
python langserve_chain.py
```

方式 C（仅主 API）：

```bash
python server/api.py
```

### 6) 启动前端

```bash
cd frontend_vue
npm run dev
```

访问地址：

- 前端：[http://localhost:5173](http://localhost:5173)
- 主 API 文档：[http://localhost:7861/docs](http://localhost:7861/docs)
- LangServe 文档：[http://localhost:8000/docs](http://localhost:8000/docs)
- LangServe Playground：[http://localhost:8000/chat/playground](http://localhost:8000/chat/playground)

---

## 🎬 核心功能演示建议

建议按以下顺序演示（便于答辩）：

1. 用户注册/登录
2. 普通对话（`/chat/chat`）
3. Agent 工具调用（时间、计算、论文检索）
4. 新建知识库 + 上传文档
5. RAG 问答（`/chat/knowledge_base_chat`）并展示引用来源
6. 查看历史记录（`/auth/history`）

---

## 🔌 主要 API 接口

### 认证接口


| 接口               | 方法   | 说明       |
| ---------------- | ---- | -------- |
| `/auth/register` | POST | 用户注册     |
| `/auth/login`    | POST | 用户登录     |
| `/auth/verify`   | GET  | 校验 token |
| `/auth/history`  | GET  | 获取历史记录   |


### 对话接口


| 接口                          | 方法   | 说明         |
| --------------------------- | ---- | ---------- |
| `/chat/chat`                | POST | 普通 LLM 对话  |
| `/chat/knowledge_base_chat` | POST | 知识库 RAG 对话 |
| `/chat/agent_chat`          | POST | Agent 工具对话 |


### 知识库接口（常用）


| 接口                                      | 方法   | 说明        |
| --------------------------------------- | ---- | --------- |
| `/knowledge_base/list_knowledge_bases`  | GET  | 获取知识库列表   |
| `/knowledge_base/create_knowledge_base` | POST | 创建知识库     |
| `/knowledge_base/list_files`            | GET  | 获取知识库文件列表 |
| `/knowledge_base/upload_docs`           | POST | 上传并向量化文档  |
| `/knowledge_base/search_docs`           | POST | 检索文档片段    |
| `/knowledge_base/delete_docs`           | POST | 删除文档      |


---

## 📊 调用示例

### LangServe 同步调用

```bash
curl -X POST http://localhost:8000/chat/invoke ^
  -H "Content-Type: application/json" ^
  -d "{\"input\": \"你好，介绍一下你自己\"}"
```

### 主 API 登录

```bash
curl -X POST http://localhost:7861/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\": \"test\", \"password\": \"123456\"}"
```

### 主 API 知识库问答

```bash
curl -X POST http://localhost:7861/chat/knowledge_base_chat ^
  -H "Content-Type: application/json" ^
  -d "{\"query\": \"大模型推理优化策略有哪些？\", \"knowledge_base_name\": \"samples\"}"
```

---

## ⚠️ 已知限制与改进方向


| 项目     | 当前情况        | 说明                              | 改进方向          |
| ------ | ----------- | ------------------------------- | ------------- |
| 工具外部依赖 | ⚠️ 部分依赖外部服务 | 某些 Tool 受第三方可用性影响               | 增加本地替代与超时重试   |
| 流式前端体验 | ⚠️ 可优化      | LangServe 支持 stream，前端可继续增强增量渲染 | 完整 SSE 流式渲染   |
| 默认模型配置 | ⚠️ 在线模型为主   | 默认示例使用智谱 API                    | 增加本地模型与路由策略   |
| 认证机制   | ⚠️ 课程版可用    | 当前为服务端 session token（非 JWT）     | 引入标准 JWT/刷新机制 |


---

## ☁️ 部署说明

### Docker（推荐）

```bash
docker build -t chatchat .
docker run -d --name chatchat -p 7861:7861 -p 8000:8000 -e ZHIPU_API_KEY=your-api-key chatchat
```

### 云服务器

1. 准备 Linux 服务器（建议 2C4G+）
2. 安装 Docker / Docker Compose
3. 拉取代码并配置环境变量
4. 启动服务并验证端口连通性

---

## 💡 常见问题

### Q1: 启动提示 API Key 未配置？

检查 `configs/model_config.py` 的 `zhipu-api.api_key` 或设置 `ZHIPU_API_KEY` 环境变量。

### Q2: 前端无法连接后端？

1. 确认 `7861` 与 `8000` 已成功启动
2. 确认前端在 `frontend_vue` 目录启动
3. 检查代理配置和防火墙

### Q3: 知识库上传失败？

1. 检查文件格式（PDF/TXT/DOCX）
2. 检查日志中的报错信息
3. 先测试小文件，确认向量化链路正常

---

## 🙏 致谢与参考


| 项目                 | 链接                                                                                                           | 说明       |
| ------------------ | ------------------------------------------------------------------------------------------------------------ | -------- |
| Langchain-Chatchat | [https://github.com/chatchat-space/Langchain-Chatchat](https://github.com/chatchat-space/Langchain-Chatchat) | 原始项目     |
| LangChain          | [https://github.com/langchain-ai/langchain](https://github.com/langchain-ai/langchain)                       | LLM 应用框架 |
| LangServe          | [https://github.com/langchain-ai/langserve](https://github.com/langchain-ai/langserve)                       | 链路服务部署   |
| FastAPI            | [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)                                               | 后端 API   |
| Vue.js             | [https://vuejs.org/](https://vuejs.org/)                                                                     | 前端框架     |
| FAISS              | [https://github.com/facebookresearch/faiss](https://github.com/facebookresearch/faiss)                       | 向量检索     |


---

## 👥 开发团队

**第 12 组**


| 成员   | 负责模块         |
| ---- | ------------ |
| 成员 1 | 后端 API 与服务集成 |
| 成员 2 | Vue 前端开发     |
| 成员 3 | 工具链与测试       |
| 成员 4 | 文档与演示        |


---

## 📜 许可证

本项目用于课程学习与研究实践。原始项目遵循 Apache License 2.0，请在分发和二次开发时遵守对应条款。

---

*项目版本：v0.2.10*  
*最后更新：2026年5月*