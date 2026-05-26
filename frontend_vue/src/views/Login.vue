<template>
  <div class="login-container">
    <div class="login-card">
      <div class="logo-section">
        <div class="logo-icon">Chat</div>
        <h1 class="title">LangChain-Chatchat</h1>
        <p class="subtitle">智能对话助手</p>
      </div>

      <el-tabs v-model="activeTab" type="border-card" class="login-tabs">
        <el-tab-pane label="登录" name="login">
          <el-form :model="loginForm" ref="loginFormRef" label-width="80px">
            <el-form-item label="用户名" prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="请输入用户名"
                @keyup.enter="handleLogin"
              />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                @keyup.enter="handleLogin"
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                class="submit-btn"
                :loading="loginLoading"
                @click="handleLogin"
              >
                登录
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="注册" name="register">
          <el-form :model="registerForm" ref="registerFormRef" label-width="80px">
            <el-form-item label="用户名" prop="username">
              <el-input
                v-model="registerForm.username"
                placeholder="请输入用户名"
              />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="请输入密码"
              />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="请再次输入密码"
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                class="submit-btn"
                :loading="registerLoading"
                @click="handleRegister"
              >
                注册
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const activeTab = ref('login')
const loginLoading = ref(false)
const registerLoading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

const API_BASE = import.meta.env.DEV ? '/api' : 'http://localhost:7861'

async function handleLogin() {
  if (!loginForm.username || !loginForm.password) {
    ElMessage.warning('请填写用户名和密码')
    return
  }
  loginLoading.value = true
  try {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: loginForm.username,
        password: loginForm.password
      })
    })
    const data = await response.json()
    if (response.ok) {
      localStorage.setItem('chat_token', data.token)
      localStorage.setItem('chat_username', data.username)
      ElMessage.success('登录成功')
      router.push('/chat')
    } else {
      ElMessage.error(data.detail || '登录失败')
    }
  } catch (error) {
    ElMessage.error('网络错误，请稍后重试')
    console.error('Login error:', error)
  } finally {
    loginLoading.value = false
  }
}

async function handleRegister() {
  if (!registerForm.username || !registerForm.password || !registerForm.confirmPassword) {
    ElMessage.warning('请填写所有字段')
    return
  }
  if (registerForm.password !== registerForm.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  registerLoading.value = true
  try {
    const response = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: registerForm.username,
        password: registerForm.password
      })
    })
    const data = await response.json()
    if (response.ok) {
      localStorage.setItem('chat_token', data.token)
      localStorage.setItem('chat_username', data.username)
      ElMessage.success('注册成功')
      router.push('/chat')
    } else {
      ElMessage.error(data.detail || '注册失败')
    }
  } catch (error) {
    ElMessage.error('网络错误，请稍后重试')
    console.error('Register error:', error)
  } finally {
    registerLoading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  padding: 40px;
  width: 100%;
  max-width: 450px;
}

.logo-section {
  text-align: center;
  margin-bottom: 30px;
}

.logo-icon {
  font-size: 48px;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 16px;
}

.title {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 14px;
  color: #999;
}

.login-tabs {
  margin-top: 20px;
}

.submit-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
}

:deep(.el-tabs__content) {
  padding: 20px 0;
}

:deep(.el-tab-pane) {
  padding-top: 10px;
}
</style>