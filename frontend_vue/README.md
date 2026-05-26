# LangChain-Chatchat Frontend (Vue 3 + Element Plus)

基于 Vue 3 和 Element Plus 构建的现代化前端应用，提供用户认证和智能对话功能。

## 技术栈

- **框架**: Vue 3 (Composition API)
- **UI 组件库**: Element Plus 2.x
- **路由**: Vue Router 4.x
- **构建工具**: Vite 5.x

## 功能特性

- ✅ 用户注册和登录
- ✅ 智能对话聊天
- ✅ 对话历史记录
- ✅ 响应式布局
- ✅ 优雅的 UI 设计

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:5173

### 生产构建

```bash
npm run build
```

构建产物位于 `dist` 目录

### 预览构建结果

```bash
npm run preview
```

## 项目结构

```
src/
├── main.js          # 入口文件
├── App.vue          # 根组件
├── router/
│   └── index.js     # 路由配置
└── views/
    ├── Login.vue    # 登录/注册页面
    └── Chat.vue     # 聊天页面
```

## API 配置

前端通过 Vite 代理访问后端 API：

- 后端地址: http://localhost:7861
- 代理前缀: /api

### API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| /auth/register | POST | 用户注册 |
| /auth/login | POST | 用户登录 |
| /auth/verify | GET | 验证 token |
| /auth/history | GET | 获取对话历史 |
| /chat/chat | POST | 对话接口 |

## 使用说明

1. 访问 http://localhost:5173
2. 注册新账号或使用已有账号登录
3. 登录后进入聊天界面，开始与 AI 对话
4. 点击右上角用户菜单可查看历史记录或退出登录

## 注意事项

- 确保后端服务已启动（python startup.py -a）
- 后端服务端口需为 7861
- Token 自动保存在 localStorage 中