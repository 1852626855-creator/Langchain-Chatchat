<template>
  <div class="chat-container">
    <el-container class="chat-layout">
      <el-header class="chat-header">
        <div class="header-left">
          <span class="header-icon">💬</span>
          <span class="header-title">langchain-ai助手</span>
        </div>
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              <span>{{ username }}</span>
              <span class="dropdown-icon">▼</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="openHistoryDialog">
                  历史记录
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  退出
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="chat-main">
        <!-- tool按钮区域 -->
        <div class="tools-demo">
          <div class="tool-buttons">
            <el-button 
              type="primary" 
              size="small" 
              @click="sendToolMessage('现在几点？')">
              🕐 时间
            </el-button>
            <el-button 
              type="success" 
              size="small" 
              @click="sendToolMessage('今天几号？')">
              📅 日期
            </el-button>
            <el-button 
              type="warning" 
              size="small" 
              @click="sendToolMessage('今天星期几？')">
              📆 星期
            </el-button>
            <el-button 
              type="info" 
              size="small" 
              @click="showKnowledgeBaseDialog">
              📚 知识库
            </el-button>
            <el-button
              type="default"
              size="small"
              @click="openHistoryDialog">
              🕘 历史
            </el-button>
            <el-switch
              v-model="useKnowledgeBase"
              active-text="RAG问答"
              inactive-text="普通问答"
              size="small" />
          </div>
        </div>

        <!-- 知识库上传对话框 -->
        <el-dialog
          title="知识库管理"
          v-model="kbDialogVisible"
          width="600px">
          <div class="kb-upload-section">
            <h4>上传文档</h4>
            <div class="kb-create-row">
              <el-input
                v-model="newKbName"
                size="small"
                placeholder="先创建知识库，例如 course_kb"
                style="max-width: 280px"
              />
              <el-button size="small" type="primary" @click="createKnowledgeBase">创建知识库</el-button>
            </div>
            <el-upload
              ref="upload"
              :action="uploadAction"
              name="files"
              :headers="{'Authorization': 'Bearer ' + token}"
              :data="{ knowledge_base_name: selectedKb, override: true, to_vector_store: true }"
              :on-success="handleUploadSuccess"
              :on-error="handleUploadError"
              :before-upload="beforeUpload"
              :auto-upload="false"
              :file-list="fileList"
              accept=".pdf,.txt,.docx,.doc">
              <el-button size="small" type="primary">选择文件</el-button>
              <div slot="tip" class="el-upload__tip">
                支持 PDF、TXT、DOCX 格式
              </div>
            </el-upload>
            <el-button style="margin-top: 10px" size="small" type="success" @click="submitUpload">
              上传到知识库
            </el-button>
          </div>

          <el-divider></el-divider>

          <div class="kb-documents-section">
            <h4>知识库列表</h4>
            <el-select v-model="selectedKb" placeholder="选择知识库" size="small" @change="handleKbChange">
              <el-option
                v-for="kb in knowledgeBases"
                :key="kb"
                :label="kb"
                :value="kb"
              />
            </el-select>
            <el-button size="small" style="margin-left: 10px" @click="loadKnowledgeBases">刷新列表</el-button>
            <h4 style="margin-top: 16px">已上传文档</h4>
            <div v-if="documents.length === 0" class="no-documents">
              暂无文档
            </div>
            <el-table
              v-else
              :data="documents"
              style="width: 100%; margin-top: 10px"
              size="small">
              <el-table-column label="文件名">
                <template slot-scope="scope">
                  <span :class="{ 'new-upload-file': isHighlightedFile(scope.row.file_name) }">
                    {{ scope.row.file_name }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100">
                <template slot-scope="scope">
                  <el-button 
                    size="mini" 
                    type="danger" 
                    @click="deleteDocument(scope.row.file_name)">
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-dialog>

        <el-dialog
          title="历史记录"
          v-model="historyDialogVisible"
          width="720px">
          <div v-if="historyRecords.length === 0" class="no-documents">暂无历史记录</div>
          <el-timeline v-else>
            <el-timeline-item
              v-for="item in historyRecords"
              :key="item.id"
              :timestamp="formatDateTime(item.created_at)"
              :type="item.role === 'user' ? 'primary' : 'success'">
              <div class="history-role">{{ item.role === 'user' ? '用户' : 'AI' }}</div>
              <div class="history-content">{{ item.content }}</div>
            </el-timeline-item>
          </el-timeline>
        </el-dialog>

        <el-scrollbar ref="scrollBar" class="message-scroll">
          <div class="message-list" ref="messageList">
            <div class="welcome-message">
              <div class="welcome-icon">🤖</div>
              <p class="welcome-text">你好！我是 langchain-ai助手</p>
              <p class="welcome-hint">点击上方按钮测试 Tool 功能，或直接输入问题</p>
            </div>

            <div
              v-for="(msg, index) in messages"
              :key="index"
              :class="['message-item', msg.role]"
            >
              <div class="message-avatar">{{ msg.role === 'user' ? username.charAt(0).toUpperCase() : 'AI' }}</div>
              <div class="message-content">
                <div class="message-bubble">
                  <p>{{ msg.content }}</p>
                </div>
                <span class="message-time">{{ msg.time }}</span>
              </div>
            </div>

            <div v-if="isLoading" class="loading-message">
              <el-skeleton :loading="true" animated />
            </div>
          </div>
        </el-scrollbar>
      </el-main>

      <el-footer class="chat-footer">
        <div class="input-area">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="2"
            placeholder="输入消息..."
            class="message-input"
            @keyup.enter.exact="handleSend"
          />
          <el-button
            type="primary"
            :loading="isSending"
            :disabled="!inputMessage.trim() || isLoading"
            class="send-btn"
            @click="handleSend"
          >
            发送
          </el-button>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const username = ref('')
const inputMessage = ref('')
const messages = ref([])
const isLoading = ref(false)
const isSending = ref(false)
const scrollBar = ref(null)
const token = ref('')
const kbDialogVisible = ref(false)
const fileList = ref([])
const documents = ref([])
const knowledgeBases = ref([])
const selectedKb = ref('')
const newKbName = ref('')
const upload = ref(null)
const highlightedFiles = ref([])
const useKnowledgeBase = ref(false)
const historyDialogVisible = ref(false)
const historyRecords = ref([])

const API_BASE = import.meta.env.DEV ? '/api' : 'http://localhost:7861'
const uploadAction = computed(() => `${API_BASE}/knowledge_base/upload_docs`)

function formatTime(date) {
  const d = new Date(date)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

function sendToolMessage(message) {
  inputMessage.value = message
  handleSend(true)
}

function buildChatHistory() {
  return messages.value.slice(0, -1).map(msg => ({
    role: msg.role,
    content: msg.content
  }))
}

async function parseSSEResponse(response) {
  const text = await response.text()
  let lastData = null
  for (const line of text.split('\n')) {
    if (line.startsWith('data: ')) {
      try {
        lastData = JSON.parse(line.slice(6))
      } catch (e) {
        // ignore malformed chunks
      }
    }
  }
  return lastData
}

function formatDateTime(date) {
  const d = new Date(date)
  if (Number.isNaN(d.getTime())) return String(date)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:${String(d.getSeconds()).padStart(2, '0')}`
}

async function requestNormalChat(chatToken, message) {
  const response = await fetch(`${API_BASE}/chat/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${chatToken}`
    },
    body: JSON.stringify({
      query: message,
      stream: false
    })
  })
  if (!response.ok) {
    const errData = await response.json().catch(() => ({}))
    throw new Error(errData.detail || `HTTP ${response.status}`)
  }
  const data = await parseSSEResponse(response)
  return data?.text || ''
}

async function requestKnowledgeBaseChat(chatToken, message) {
  async function fetchKbFiles(kbName) {
    const response = await fetch(
      `${API_BASE}/knowledge_base/list_files?knowledge_base_name=${encodeURIComponent(kbName)}`,
      { headers: { 'Authorization': `Bearer ${chatToken}` } }
    )
    const data = await response.json()
    return data.code === 200 ? (data.data || []) : []
  }

  if (!selectedKb.value) {
    await loadKnowledgeBases()
  }
  if (!selectedKb.value) {
    throw new Error('请先创建并选择知识库')
  }

  let currentKb = selectedKb.value
  let currentFiles = await fetchKbFiles(currentKb)
  if (currentFiles.length === 0) {
    for (const kbName of knowledgeBases.value) {
      const files = await fetchKbFiles(kbName)
      if (files.length > 0) {
        currentKb = kbName
        currentFiles = files
        selectedKb.value = kbName
        localStorage.setItem('selected_kb_name', kbName)
        documents.value = files.map(name => ({ file_name: name }))
        ElMessage.warning(`当前知识库无文档，已自动切换到 ${kbName}`)
        break
      }
    }
  }
  if (currentFiles.length === 0) {
    throw new Error('当前所有知识库都没有文档，请先上传文档')
  }

  const searchResponse = await fetch(`${API_BASE}/knowledge_base/search_docs`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${chatToken}`
    },
    body: JSON.stringify({
      query: message,
      knowledge_base_name: currentKb,
      top_k: 5,
      score_threshold: 1
    })
  })
  const searchHits = searchResponse.ok ? (await searchResponse.json()) : []

  const response = await fetch(`${API_BASE}/chat/knowledge_base_chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${chatToken}`
    },
    body: JSON.stringify({
      query: message,
      knowledge_base_name: currentKb,
      top_k: 5,
      score_threshold: 1,
      stream: false
    })
  })
  if (!response.ok) {
    const errData = await response.json().catch(() => ({}))
    throw new Error(errData.detail || `HTTP ${response.status}`)
  }
  const data = await parseSSEResponse(response)
  let answer = data?.text || data?.answer || ''
  const docs = Array.isArray(data?.docs) ? data.docs : []
  const docsHasPlaceholder = docs.some(d => String(d).includes('未找到相关文档'))

  if ((!answer || docsHasPlaceholder) && Array.isArray(searchHits) && searchHits.length > 0) {
    const context = searchHits
      .slice(0, 3)
      .map((item, idx) => `资料${idx + 1}: ${(item?.page_content || '').slice(0, 500)}`)
      .join('\n\n')
    const rewritePrompt = `请严格根据给定资料回答问题，不要编造。如果资料不足请明确说明。\n\n${context}\n\n问题：${message}`
    answer = await requestNormalChat(chatToken, rewritePrompt)
    const sourceLines = searchHits.slice(0, 3).map((item, idx) => {
      const source = item?.metadata?.source || `doc_${idx + 1}`
      const snippet = (item?.page_content || '').slice(0, 140)
      return `出处[${idx + 1}] ${source}\n${snippet}...`
    })
    return `${answer || '（模型未生成答案，展示检索结果）'}\n\n--- 引用来源 ---\n${sourceLines.join('\n\n')}`
  }

  if (docs.length > 0) {
    return `${answer || '（模型未生成答案，展示检索结果）'}\n\n--- 引用来源 ---\n${docs.join('\n')}`
  }
  return answer
}

async function requestAgentChat(chatToken, message) {
  const response = await fetch(`${API_BASE}/chat/agent_chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${chatToken}`
    },
    body: JSON.stringify({
      query: message,
      history: buildChatHistory(),
      stream: false
    })
  })
  if (!response.ok) {
    const errData = await response.json().catch(() => ({}))
    throw new Error(errData.detail || `HTTP ${response.status}`)
  }
  const data = await parseSSEResponse(response)
  return data?.final_answer || data?.answer || ''
}

async function handleSend(useAgent = false) {
  const shouldUseAgent = useAgent === true
  const message = inputMessage.value.trim()
  if (!message) return
  
  isSending.value = true
  messages.value.push({
    role: 'user',
    content: message,
    time: formatTime(new Date())
  })
  inputMessage.value = ''
  await nextTick()
  scrollToBottom()
  
  isLoading.value = true
  isSending.value = false
  
  try {
    const chatToken = localStorage.getItem('chat_token')
    let answer = ''
    if (useKnowledgeBase.value && !shouldUseAgent) {
      answer = await requestKnowledgeBaseChat(chatToken, message)
      if (!answer) {
        answer = await requestNormalChat(chatToken, message)
      }
    } else if (shouldUseAgent) {
      answer = await requestAgentChat(chatToken, message)
      // Agent unavailable (e.g. 502) fallback to normal chat.
      if (!answer || answer.includes('工具状态: 调用失败')) {
        answer = await requestNormalChat(chatToken, message)
      }
    } else {
      answer = await requestNormalChat(chatToken, message)
    }
    if (!answer) answer = '未收到回复'

    messages.value.push({
      role: 'assistant',
      content: answer,
      time: formatTime(new Date())
    })
  } catch (error) {
    messages.value.push({
      role: 'assistant',
      content: '网络错误: ' + error.message,
      time: formatTime(new Date())
    })
    console.error('Chat error:', error)
  } finally {
    isLoading.value = false
    await nextTick()
    scrollToBottom()
  }
}

async function loadHistory() {
  const chatToken = localStorage.getItem('chat_token')
  try {
    const response = await fetch(`${API_BASE}/auth/history?token=${chatToken}`)
    if (response.ok) {
      const data = await response.json()
      messages.value = data.history.map(item => ({
        role: item.role,
        content: item.content,
        time: formatTime(item.created_at)
      }))
      await nextTick()
      scrollToBottom()
      ElMessage.success(`已加载 ${data.count} 条记录`)
    } else {
      ElMessage.error('加载失败')
    }
  } catch (error) {
    ElMessage.error('加载失败')
    console.error('Load history error:', error)
  }
}

async function fetchHistory() {
  const chatToken = localStorage.getItem('chat_token')
  if (!chatToken) {
    throw new Error('未登录或 token 丢失，请重新登录')
  }
  const response = await fetch(`${API_BASE}/auth/history?token=${chatToken}`)
  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem('chat_token')
      localStorage.removeItem('chat_username')
      throw new Error('登录已过期，请重新登录')
    }
    const response2 = await fetch(`${API_BASE}/auth/history`, {
      headers: { 'Authorization': `Bearer ${chatToken}` }
    })
    if (!response2.ok) {
      if (response2.status === 401) {
        localStorage.removeItem('chat_token')
        localStorage.removeItem('chat_username')
        throw new Error('登录已过期，请重新登录')
      }
      throw new Error('加载历史失败，请重新登录')
    }
    return response2.json()
  }
  return response.json()
}

async function openHistoryDialog() {
  historyDialogVisible.value = true
  try {
    const data = await fetchHistory()
    historyRecords.value = data.history || []
  } catch (error) {
    historyRecords.value = []
    const errMsg = error?.message || '历史记录加载失败'
    ElMessage.error(errMsg)
    if (errMsg.includes('重新登录')) {
      historyDialogVisible.value = false
      router.push('/')
    }
  }
}

function handleLogout() {
  localStorage.removeItem('chat_token')
  localStorage.removeItem('chat_username')
  ElMessage.info('已退出')
  router.push('/')
}

function scrollToBottom() {
  if (scrollBar.value) {
    scrollBar.value.setScrollTop(scrollBar.value.scrollHeight)
  }
}

async function showKnowledgeBaseDialog() {
  kbDialogVisible.value = true
  await loadKnowledgeBases()
}

async function loadKnowledgeBases() {
  const chatToken = localStorage.getItem('chat_token')
  try {
    const response = await fetch(`${API_BASE}/knowledge_base/list_knowledge_bases`, {
      headers: { 'Authorization': `Bearer ${chatToken}` }
    })
    const data = await response.json()
    if (data.code === 200) {
      knowledgeBases.value = data.data || []
      const savedKb = localStorage.getItem('selected_kb_name') || ''
      if (knowledgeBases.value.length) {
        if (savedKb && knowledgeBases.value.includes(savedKb)) {
          selectedKb.value = savedKb
        } else if (!selectedKb.value || !knowledgeBases.value.includes(selectedKb.value)) {
          selectedKb.value = knowledgeBases.value[0]
        }
      }
      await loadDocuments()
    } else {
      ElMessage.error(data.msg || '加载知识库失败')
    }
  } catch (error) {
    console.error('Load knowledge bases error:', error)
    ElMessage.error('加载知识库失败')
  }
}

async function createKnowledgeBase() {
  const kbName = newKbName.value.trim()
  if (!kbName) {
    ElMessage.warning('请先输入知识库名称')
    return
  }

  const chatToken = localStorage.getItem('chat_token')
  try {
    const response = await fetch(`${API_BASE}/knowledge_base/create_knowledge_base`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${chatToken}`
      },
      body: JSON.stringify({ knowledge_base_name: kbName, embed_model: 'zhipu-api' })
    })
    const data = await response.json()
    if (data.code === 200) {
      ElMessage.success(data.msg || '知识库创建成功')
      newKbName.value = ''
      await loadKnowledgeBases()
      selectedKb.value = kbName
      localStorage.setItem('selected_kb_name', kbName)
      await loadDocuments()
    } else {
      ElMessage.error(data.msg || '知识库创建失败')
    }
  } catch (error) {
    console.error('Create knowledge base error:', error)
    ElMessage.error('知识库创建失败')
  }
}

async function loadDocuments() {
  if (!selectedKb.value) return
  const chatToken = localStorage.getItem('chat_token')
  try {
    const response = await fetch(
      `${API_BASE}/knowledge_base/list_files?knowledge_base_name=${encodeURIComponent(selectedKb.value)}`,
      { headers: { 'Authorization': `Bearer ${chatToken}` } }
    )
    const data = await response.json()
    if (data.code === 200) {
      documents.value = (data.data || []).map(name => ({ file_name: name }))
    } else {
      documents.value = []
      ElMessage.error(data.msg || '加载文档失败')
    }
  } catch (error) {
    console.error('Load documents error:', error)
  }
}

function handleKbChange() {
  localStorage.setItem('selected_kb_name', selectedKb.value || '')
  loadDocuments()
}

function beforeUpload(file) {
  const allowedTypes = ['application/pdf', 'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
  const isAllowed = allowedTypes.includes(file.type) || file.name.endsWith('.txt')
  
  if (!isAllowed) {
    ElMessage.error('Only PDF, TXT, DOCX files are allowed')
  }
  return isAllowed
}

function submitUpload() {
  if (!selectedKb.value) {
    ElMessage.warning('请先创建并选择知识库')
    return
  }
  if (upload.value) {
    upload.value.submit()
  }
}

async function handleUploadSuccess(response) {
  if (response.code === 200) {
    highlightedFiles.value = fileList.value.map(item => item.name)
    const failedFiles = response?.data?.failed_files || {}
    const failedNames = Object.keys(failedFiles)
    if (failedNames.length > 0) {
      ElMessage.warning(`部分文件处理失败：${failedNames.join(', ')}`)
    } else {
      ElMessage.success(response.msg || '上传成功')
    }
    fileList.value = []
    await loadKnowledgeBases()
    await loadDocuments()
    setTimeout(() => {
      highlightedFiles.value = []
    }, 8000)
  } else {
    ElMessage.error(response.msg || '上传失败')
  }
}

function isHighlightedFile(fileName) {
  return highlightedFiles.value.includes(fileName)
}

function handleUploadError(err, file, fileList) {
  ElMessage.error('Upload failed: ' + (err.message || 'Unknown error'))
}

async function deleteDocument(fileName) {
  const chatToken = localStorage.getItem('chat_token')
  try {
    const response = await fetch(`${API_BASE}/knowledge_base/delete_docs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${chatToken}`
      },
      body: JSON.stringify({
        knowledge_base_name: selectedKb.value,
        file_names: [fileName]
      })
    })
    const data = await response.json()
    if (data.code === 200) {
      ElMessage.success('删除成功')
      loadDocuments()
    } else {
      ElMessage.error(data.msg || '删除失败')
    }
  } catch (error) {
    ElMessage.error('删除失败')
    console.error('Delete error:', error)
  }
}

onMounted(() => {
  const storedUsername = localStorage.getItem('chat_username')
  const storedToken = localStorage.getItem('chat_token')

  if (storedUsername) {
    username.value = storedUsername
  }

  if (storedToken) {
    token.value = storedToken
  }

  if (!storedToken) {
    router.push('/')
  }
})
</script>

<style scoped>
.chat-container {
  min-height: 100vh;
  background: #f5f7fa;
}

.chat-layout {
  height: 100vh;
}

.chat-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  font-size: 24px;
  font-weight: bold;
  color: rgba(255, 255, 255, 0.9);
}

.header-title {
  font-size: 18px;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  border-radius: 20px;
  transition: background 0.3s;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.2);
}

.dropdown-icon {
  font-size: 12px;
}

.tools-demo {
  background: white;
  padding: 15px;
  border-radius: 12px;
  margin-bottom: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.tools-demo h4 {
  margin: 0 0 12px 0;
  color: #333;
}

.kb-create-row {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 12px;
}

.new-upload-file {
  color: #67c23a;
  font-weight: 600;
}

.history-role {
  font-weight: 600;
  margin-bottom: 4px;
}

.history-content {
  white-space: pre-wrap;
  line-height: 1.6;
}

.tool-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.chat-main {
  padding: 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.message-scroll {
  flex: 1;
  border-radius: 12px;
}

.message-list {
  padding: 10px;
}

.welcome-message {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.welcome-icon {
  font-size: 48px;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 16px;
}

.welcome-text {
  font-size: 18px;
  color: #333;
  margin-bottom: 8px;
}

.welcome-hint {
  font-size: 14px;
}

.message-item {
  display: flex;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-item.user {
  justify-content: flex-end;
}

.message-item.user .message-content {
  align-items: flex-end;
}

.message-item.user .message-bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e2e8f0;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
  margin: 0 12px;
}

.message-item.user .message-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 16px;
  background: white;
  border: 1px solid #e8e8e8;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  white-space: pre-wrap;
}

.message-bubble p {
  margin: 0;
  line-height: 1.6;
  font-size: 14px;
}

.message-time {
  font-size: 12px;
  color: #999;
  padding: 0 4px;
}

.loading-message {
  padding: 10px 20px;
}

.chat-footer {
  padding: 16px 20px;
  background: white;
  border-top: 1px solid #e8e8e8;
}

.input-area {
  display: flex;
  gap: 12px;
}

.message-input {
  flex: 1;
  border-radius: 12px;
  resize: none;
}

.send-btn {
  border-radius: 12px;
  padding: 0 24px;
  height: 48px;
}

:deep(.el-scrollbar__wrap) {
  overflow-y: auto;
}

:deep(.el-textarea__inner) {
  resize: none;
  border-radius: 12px;
}
</style>
