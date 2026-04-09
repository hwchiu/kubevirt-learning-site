<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { useRoute, useData } from 'vitepress'
import { marked } from 'marked'

const route = useRoute()
const { isDark } = useData()

const isDev = import.meta.env.DEV

// UI state — overlay vs minimized bubble
const isOpen = ref(false)
const question = ref('')
const messages = ref([])
const isLoading = ref(false)
const elapsedSeconds = ref(0)
let elapsedTimer = null
const messagesContainer = ref(null)
const textareaRef = ref(null)

// Configure marked
marked.setOptions({ breaks: true, gfm: true })

// Auto-detect project from the first path segment — no hardcoded list needed
const currentProject = computed(() => {
  const parts = route.path.replace(/^\//, '').split('/')
  const segment = parts[0]
  // Ignore VitePress built-in routes and the top-level index
  if (!segment || segment === 'index' || segment.endsWith('.html')) return null
  return segment
})

const projectLabel = computed(() => {
  const project = currentProject.value
  if (!project) return '全域'
  // Convert kebab-case to title case, e.g. "node-maintenance-operator" → "Node Maintenance Operator"
  return project.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
})

function renderMarkdown(text) {
  if (!text) return ''
  return marked.parse(normalizeAssistantMarkdown(text))
}

function normalizeAssistantMarkdown(text) {
  return text.replace(/```(?:mermaid|marmaid)([\t ]*\r?\n)/gi, '```text$1')
}

async function scrollToBottom() {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

function openOverlay() {
  isOpen.value = true
  nextTick(() => textareaRef.value?.focus())
}

function minimize() {
  isOpen.value = false
}

// Keyboard: Escape to minimize
function onKeydown(e) {
  if (e.key === 'Escape' && isOpen.value) minimize()
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))

async function sendMessage() {
  const q = question.value.trim()
  if (!q || isLoading.value) return

  messages.value.push({ role: 'user', content: q })
  question.value = ''
  isLoading.value = true
  await scrollToBottom()

  const thinkingMsg = { role: 'assistant', content: '🔍 正在分析原始碼... (0s)', isLoading: true }
  messages.value.push(thinkingMsg)
  elapsedSeconds.value = 0
  elapsedTimer = setInterval(() => {
    elapsedSeconds.value++
    thinkingMsg.content = `🔍 正在分析原始碼... (${elapsedSeconds.value}s)`
    messages.value = [...messages.value]
  }, 1000)
  await scrollToBottom()

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project: currentProject.value, question: q }),
    })

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.result) {
              const idx = messages.value.indexOf(thinkingMsg)
              if (idx !== -1) messages.value.splice(idx, 1)
              messages.value.push({ role: 'assistant', content: data.result })
            } else if (data.error) {
              const idx = messages.value.indexOf(thinkingMsg)
              if (idx !== -1) messages.value.splice(idx, 1)
              messages.value.push({ role: 'assistant', content: `❌ 錯誤：${data.error}`, isError: true })
            }
          } catch {}
        }
      }
      await scrollToBottom()
    }
  } catch (err) {
    clearInterval(elapsedTimer)
    const idx = messages.value.indexOf(thinkingMsg)
    if (idx !== -1) messages.value.splice(idx, 1)
    messages.value.push({ role: 'assistant', content: `❌ 連線失敗：${err.message}`, isError: true })
  } finally {
    clearInterval(elapsedTimer)
    isLoading.value = false
    await scrollToBottom()
  }
}

function clearChat() {
  if (confirm('清除所有對話紀錄？')) messages.value = []
}

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

function quickAsk(q) {
  question.value = q
  sendMessage()
}
</script>

<template>
  <div v-if="isDev">
    <!-- Floating bubble (minimized state) -->
    <button
      v-if="!isOpen"
      class="chat-bubble"
      :class="{ 'has-messages': messages.length > 0 }"
      @click="openOverlay"
      title="開啟 AI 原始碼助手"
    >
      🤖
      <span v-if="messages.length > 0" class="bubble-badge">
        {{ messages.filter(m => m.role === 'assistant' && !m.isLoading).length }}
      </span>
    </button>

    <!-- Full-screen overlay -->
    <Teleport to="body">
      <div v-if="isOpen" class="chat-overlay" :class="{ dark: isDark }">
        <!-- Header -->
        <div class="overlay-header">
          <div class="header-left">
            <span class="header-icon">🤖</span>
            <span class="header-title">原始碼助手</span>
            <span class="project-badge">{{ projectLabel }}</span>
          </div>
          <div class="header-right">
            <span class="header-hint">ESC 最小化</span>
            <button class="header-btn" @click="clearChat" title="清除對話">🗑️</button>
            <button class="header-btn minimize-btn" @click="minimize" title="最小化">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M2 8h12v1H2z"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Messages area -->
        <div ref="messagesContainer" class="overlay-messages">
          <!-- Empty state -->
          <div v-if="messages.length === 0" class="empty-state">
            <div class="empty-icon">🔬</div>
            <p class="empty-title">詢問任何關於 <strong>{{ projectLabel }}</strong> 的問題</p>
            <p class="empty-sub">AI 會直接讀取原始碼與文件來回答</p>
            <div class="suggestions">
              <button @click="quickAsk('這個專案的核心架構是什麼？')">🏗️ 核心架構</button>
              <button @click="quickAsk('主要的 Controller 有哪些，各自的職責是什麼？')">⚙️ Controller 列表</button>
              <button @click="quickAsk('CRD 的主要欄位有哪些？')">📋 CRD 欄位</button>
              <button @click="quickAsk('這個專案的資料流是怎麼運作的？')">🔄 資料流</button>
            </div>
          </div>

          <!-- Messages -->
          <div v-for="(msg, i) in messages" :key="i" class="message-row" :class="msg.role">
            <div class="message-avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
            <div
              class="message-bubble"
              :class="{ loading: msg.isLoading, error: msg.isError }"
              v-html="msg.role === 'assistant' && !msg.isLoading ? renderMarkdown(msg.content) : msg.content"
            />
          </div>
        </div>

        <!-- Input bar -->
        <div class="overlay-input">
          <div class="input-wrapper">
            <textarea
              ref="textareaRef"
              v-model="question"
              @keydown="handleKeydown"
              :disabled="isLoading"
              placeholder="輸入問題... (Enter 送出，Shift+Enter 換行)"
              rows="2"
            />
            <button
              class="send-btn"
              @click="sendMessage"
              :disabled="isLoading || !question.trim()"
              :title="isLoading ? '分析中...' : '送出'"
            >
              <span v-if="isLoading">⏳</span>
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
              </svg>
            </button>
          </div>
          <div class="input-footer">
            💡 本地模式 — claude CLI 直接讀取原始碼
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
/* ── Floating bubble ── */
.chat-bubble {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1000;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  background: var(--vp-c-brand-1);
  color: white;
  font-size: 26px;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-bubble:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.chat-bubble.has-messages {
  animation: bubble-glow 3s ease-in-out infinite;
}

@keyframes bubble-glow {
  0%, 100% { box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25); }
  50% { box-shadow: 0 4px 20px var(--vp-c-brand-1); }
}

.bubble-badge {
  position: absolute;
  top: -2px;
  right: -2px;
  background: #ef4444;
  color: white;
  font-size: 10px;
  font-weight: 700;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid white;
}

/* ── Full-screen overlay ── */
.chat-overlay {
  position: fixed;
  inset: 0;
  z-index: 9000;
  display: flex;
  flex-direction: column;
  background: var(--vp-c-bg);
  font-family: var(--vp-font-family-base);
}

/* ── Header ── */
.overlay-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 56px;
  min-height: 56px;
  border-bottom: 1px solid var(--vp-c-border);
  background: var(--vp-c-bg-soft);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-icon {
  font-size: 22px;
}

.header-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--vp-c-text-1);
}

.project-badge {
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1);
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  border: 1px solid var(--vp-c-brand-2);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-hint {
  font-size: 12px;
  color: var(--vp-c-text-3);
  margin-right: 4px;
}

.header-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px 8px;
  border-radius: 6px;
  color: var(--vp-c-text-2);
  font-size: 16px;
  display: flex;
  align-items: center;
  transition: background 0.15s, color 0.15s;
}

.header-btn:hover {
  background: var(--vp-c-bg-mute);
  color: var(--vp-c-text-1);
}

.minimize-btn {
  color: var(--vp-c-text-2);
}

/* ── Messages ── */
.overlay-messages {
  flex: 1;
  overflow-y: auto;
  padding: 32px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
}

/* Empty state */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  padding: 48px 0;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 18px;
  color: var(--vp-c-text-1);
  margin-bottom: 8px;
}

.empty-sub {
  font-size: 14px;
  color: var(--vp-c-text-3);
  margin-bottom: 28px;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  max-width: 560px;
}

.suggestions button {
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-border);
  border-radius: 20px;
  padding: 8px 16px;
  font-size: 13px;
  cursor: pointer;
  color: var(--vp-c-text-2);
  transition: all 0.2s;
  font-family: var(--vp-font-family-base);
}

.suggestions button:hover {
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1);
  border-color: var(--vp-c-brand-1);
}

/* Message rows */
.message-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.message-row.user {
  flex-direction: row-reverse;
}

.message-avatar {
  font-size: 22px;
  flex-shrink: 0;
  margin-top: 2px;
}

.message-bubble {
  max-width: 80%;
  padding: 14px 18px;
  border-radius: 12px;
  font-size: 15px;
  line-height: 1.7;
  word-break: break-word;
}

.message-row.user .message-bubble {
  background: var(--vp-c-brand-soft);
  border: 1px solid var(--vp-c-brand-2);
  border-radius: 16px 4px 16px 16px;
}

.message-row.assistant .message-bubble {
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-border);
  border-radius: 4px 16px 16px 16px;
}

.message-bubble.loading {
  color: var(--vp-c-text-3);
  animation: pulse 1.5s ease-in-out infinite;
}

.message-bubble.error {
  background: var(--vp-c-danger-soft);
  border-color: var(--vp-c-danger-1);
  color: var(--vp-c-danger-1);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.45; }
}

/* Markdown content inside assistant bubble */
.message-row.assistant .message-bubble :deep(h1),
.message-row.assistant .message-bubble :deep(h2),
.message-row.assistant .message-bubble :deep(h3),
.message-row.assistant .message-bubble :deep(h4) {
  margin: 16px 0 8px;
  font-weight: 700;
  line-height: 1.3;
  color: var(--vp-c-text-1);
}

.message-row.assistant .message-bubble :deep(h1) { font-size: 20px; }
.message-row.assistant .message-bubble :deep(h2) { font-size: 18px; border-bottom: 1px solid var(--vp-c-border); padding-bottom: 4px; }
.message-row.assistant .message-bubble :deep(h3) { font-size: 16px; }
.message-row.assistant .message-bubble :deep(h4) { font-size: 15px; }

.message-row.assistant .message-bubble :deep(p) {
  margin: 8px 0;
}

.message-row.assistant .message-bubble :deep(ul),
.message-row.assistant .message-bubble :deep(ol) {
  margin: 8px 0;
  padding-left: 24px;
}

.message-row.assistant .message-bubble :deep(li) {
  margin: 4px 0;
}

.message-row.assistant .message-bubble :deep(pre) {
  background: var(--vp-c-bg-mute);
  border: 1px solid var(--vp-c-border);
  border-radius: 8px;
  padding: 14px 16px;
  overflow-x: auto;
  margin: 12px 0;
  font-size: 13px;
  line-height: 1.6;
}

.message-row.assistant .message-bubble :deep(code) {
  font-family: var(--vp-font-family-mono);
  font-size: 13px;
  background: var(--vp-c-bg-mute);
  padding: 2px 5px;
  border-radius: 4px;
  color: var(--vp-c-code-color, var(--vp-c-brand-1));
}

.message-row.assistant .message-bubble :deep(pre code) {
  background: none;
  padding: 0;
  color: inherit;
}

.message-row.assistant .message-bubble :deep(blockquote) {
  border-left: 3px solid var(--vp-c-brand-1);
  padding-left: 12px;
  margin: 8px 0;
  color: var(--vp-c-text-2);
  font-style: italic;
}

.message-row.assistant .message-bubble :deep(strong) {
  font-weight: 700;
  color: var(--vp-c-text-1);
}

.message-row.assistant .message-bubble :deep(a) {
  color: var(--vp-c-brand-1);
  text-decoration: underline;
}

.message-row.assistant .message-bubble :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
  font-size: 13px;
}

.message-row.assistant .message-bubble :deep(th),
.message-row.assistant .message-bubble :deep(td) {
  border: 1px solid var(--vp-c-border);
  padding: 8px 12px;
  text-align: left;
}

.message-row.assistant .message-bubble :deep(th) {
  background: var(--vp-c-bg-mute);
  font-weight: 600;
}

/* ── Input bar ── */
.overlay-input {
  flex-shrink: 0;
  border-top: 1px solid var(--vp-c-border);
  background: var(--vp-c-bg-soft);
  padding: 14px 24px 10px;
}

.input-wrapper {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  max-width: 900px;
  margin: 0 auto;
}

.input-wrapper textarea {
  flex: 1;
  border: 1px solid var(--vp-c-border);
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 15px;
  resize: none;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-family: var(--vp-font-family-base);
  outline: none;
  line-height: 1.5;
  transition: border-color 0.2s;
  min-height: 48px;
}

.input-wrapper textarea:focus {
  border-color: var(--vp-c-brand-1);
  box-shadow: 0 0 0 2px var(--vp-c-brand-soft);
}

.input-wrapper textarea:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.send-btn {
  width: 44px;
  height: 44px;
  border: none;
  background: var(--vp-c-brand-1);
  color: white;
  border-radius: 10px;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.2s, transform 0.15s;
  flex-shrink: 0;
}

.send-btn:not(:disabled):hover {
  opacity: 0.85;
  transform: scale(1.05);
}

.send-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
  transform: none;
}

.input-footer {
  text-align: center;
  font-size: 11px;
  color: var(--vp-c-text-3);
  margin-top: 8px;
}

/* ── Mobile ── */
@media (max-width: 768px) {
  .overlay-messages {
    padding: 20px 16px;
  }

  .overlay-input {
    padding: 10px 16px 8px;
  }

  .message-bubble {
    max-width: 90%;
    font-size: 14px;
  }

  .header-hint {
    display: none;
  }
}
</style>
