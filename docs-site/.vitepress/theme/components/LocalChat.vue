<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { useRoute, useData } from 'vitepress'
import { marked } from 'marked'

const route = useRoute()
const { isDark } = useData()

const isDev = import.meta.env.DEV
const hourMinuteFormatter = new Intl.DateTimeFormat('zh-TW', {
  hour: '2-digit',
  minute: '2-digit',
})
const MAX_TEXTAREA_HEIGHT = 180

const quickPrompts = [
  {
    icon: '🏗️',
    title: '核心架構',
    description: '快速理解模組分工與責任邊界',
    question: '這個專案的核心架構是什麼？',
  },
  {
    icon: '⚙️',
    title: 'Controller 列表',
    description: '整理主要控制器與各自職責',
    question: '主要的 Controller 有哪些，各自的職責是什麼？',
  },
  {
    icon: '📋',
    title: 'CRD 欄位',
    description: '聚焦資源模型與關鍵 schema',
    question: 'CRD 的主要欄位有哪些？',
  },
  {
    icon: '🔄',
    title: '資料流',
    description: '追蹤事件、同步與資料流向',
    question: '這個專案的資料流是怎麼運作的？',
  },
]

const featurePills = [
  '原始碼導向',
  '文件交叉比對',
  '檔案路徑引用',
  '適合追問實作細節',
]

// UI state — overlay vs minimized bubble
const isOpen = ref(false)
const question = ref('')
const messages = ref([])
const isLoading = ref(false)
const elapsedSeconds = ref(0)
let elapsedTimer = null
let messageCounter = 0
const messagesContainer = ref(null)
const textareaRef = ref(null)

// Configure marked
marked.setOptions({ breaks: true, gfm: true })

// Auto-detect project from the first path segment — no hardcoded list needed
const currentProject = computed(() => {
  const parts = route.path.replace(/^\//, '').split('/')
  const segment = parts[0]
  if (!segment || segment === 'index' || segment.endsWith('.html')) return null
  return segment
})

const projectLabel = computed(() => {
  const project = currentProject.value
  if (!project) return 'KubeVirt Learning Site'
  return project.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
})

const hasMessages = computed(() => messages.value.length > 0)
const assistantReplyCount = computed(() => messages.value.filter(msg => msg.role === 'assistant' && !msg.isLoading && !msg.isError).length)
const userMessageCount = computed(() => messages.value.filter(msg => msg.role === 'user').length)
const inputLength = computed(() => question.value.trim().length)

function createMessage(role, content, extra = {}) {
  return {
    id: globalThis.crypto?.randomUUID?.() ?? `${role}-${Date.now()}-${++messageCounter}-${Math.random().toString(36).slice(2, 8)}`,
    role,
    content,
    createdAt: new Date(),
    ...extra,
  }
}

function renderMarkdown(text) {
  if (!text) return ''
  return marked.parse(normalizeAssistantMarkdown(text))
}

function normalizeAssistantMarkdown(text) {
  // Render Mermaid fences as plain text blocks because the chat bubble only supports Markdown HTML.
  return text.replace(/```mermaid(\s*\r?\n)/gi, '```text$1')
}

function formatTime(date) {
  if (!date) return ''
  const parsedDate = new Date(date)
  if (Number.isNaN(parsedDate.getTime())) return ''
  return hourMinuteFormatter.format(parsedDate)
}

async function scrollToBottom() {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

function autoResizeTextarea() {
  if (!textareaRef.value) return
  textareaRef.value.style.height = 'auto'
  textareaRef.value.style.height = `${Math.min(textareaRef.value.scrollHeight, MAX_TEXTAREA_HEIGHT)}px`
}

function openOverlay() {
  isOpen.value = true
  nextTick(() => {
    textareaRef.value?.focus()
    autoResizeTextarea()
  })
}

function minimize() {
  isOpen.value = false
}

function onKeydown(e) {
  if (e.key === 'Escape' && isOpen.value) minimize()
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
  autoResizeTextarea()
})

onUnmounted(() => window.removeEventListener('keydown', onKeydown))

async function sendMessage() {
  const q = question.value.trim()
  if (!q || isLoading.value) return

  messages.value.push(createMessage('user', q))
  question.value = ''
  isLoading.value = true
  await nextTick()
  autoResizeTextarea()
  await scrollToBottom()

  const thinkingMsg = createMessage('assistant', '正在分析原始碼與文件脈絡...', {
    isLoading: true,
  })
  messages.value.push(thinkingMsg)
  elapsedSeconds.value = 0
  elapsedTimer = setInterval(() => {
    elapsedSeconds.value++
    thinkingMsg.content = `正在分析原始碼與文件脈絡... ${elapsedSeconds.value}s`
    messages.value = [...messages.value]
  }, 1000)
  await scrollToBottom()

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project: currentProject.value, question: q }),
    })

    if (!response.ok) {
      throw new Error(`請求失敗 (${response.status})`)
    }

    if (!response.body) {
      throw new Error('無法讀取串流回應')
    }

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
              messages.value.push(createMessage('assistant', data.result))
            } else if (data.error) {
              const idx = messages.value.indexOf(thinkingMsg)
              if (idx !== -1) messages.value.splice(idx, 1)
              messages.value.push(createMessage('assistant', `❌ 錯誤：${data.error}`, { isError: true }))
            }
          } catch (err) {
            console.debug('Failed to parse SSE payload as JSON - Line:', line, 'Error:', err?.message ?? err)
          }
        }
      }
      await scrollToBottom()
    }
  } catch (err) {
    clearInterval(elapsedTimer)
    const idx = messages.value.indexOf(thinkingMsg)
    if (idx !== -1) messages.value.splice(idx, 1)
    messages.value.push(createMessage('assistant', `❌ 連線失敗：${err.message}`, { isError: true }))
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
  nextTick(() => {
    autoResizeTextarea()
    sendMessage()
  })
}
</script>

<template>
  <div v-if="isDev">
    <button
      v-if="!isOpen"
      class="chat-bubble"
      :class="{ 'has-messages': hasMessages }"
      @click="openOverlay"
      title="開啟 AI 原始碼助手"
    >
      <span class="bubble-icon">🤖</span>
      <span class="bubble-glow"></span>
      <span v-if="assistantReplyCount > 0" class="bubble-badge">
        {{ assistantReplyCount }}
      </span>
    </button>

    <Teleport to="body">
      <Transition name="chat-fade">
        <div v-if="isOpen" class="chat-overlay" :class="{ dark: isDark }">
          <div class="overlay-backdrop" @click="minimize"></div>

          <section class="chat-shell">
            <div class="shell-noise"></div>

            <div class="overlay-header">
              <div class="header-left">
                <div class="assistant-orb">
                  <span>🤖</span>
                </div>
                <div class="header-copy">
                  <p class="header-eyebrow">AI 原始碼助手</p>
                  <div class="header-main">
                    <span class="header-title">原始碼助手</span>
                    <span class="project-badge">{{ projectLabel }}</span>
                  </div>
                  <p class="header-subtitle">
                    <span class="status-dot"></span>
                    可追問架構、Controller、資料流與 CRD 細節
                  </p>
                </div>
              </div>

              <div class="header-right">
                <div class="header-stats">
                  <div class="stat-chip">
                    <strong>{{ assistantReplyCount }}</strong>
                    <span>回覆</span>
                  </div>
                  <div class="stat-chip">
                    <strong>{{ userMessageCount }}</strong>
                    <span>提問</span>
                  </div>
                </div>
                <span class="header-hint">ESC 最小化</span>
                <button class="header-btn" @click="clearChat" title="清除對話">🗑️</button>
                <button class="header-btn minimize-btn" @click="minimize" title="最小化">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M2 8h12v1H2z"/>
                  </svg>
                </button>
              </div>
            </div>

            <div ref="messagesContainer" class="overlay-messages" :class="{ empty: !hasMessages }">
              <div v-if="!hasMessages" class="empty-state">
                <div class="empty-hero">
                  <div class="hero-badge">情境式原始碼分析</div>
                  <h2>把文件與原始碼一起問到底</h2>
                  <p>
                    從 <strong class="project-emphasis">{{ projectLabel }}</strong> 的原始碼、分析文件與資料流脈絡中整理答案，
                    適合拿來快速建立心智模型，或一路追問到實作細節。
                  </p>
                  <div class="feature-pills">
                    <span v-for="item in featurePills" :key="item">{{ item }}</span>
                  </div>
                </div>

                <div class="suggestions-grid">
                  <button
                    v-for="prompt in quickPrompts"
                    :key="prompt.title"
                    class="suggestion-card"
                    @click="quickAsk(prompt.question)"
                  >
                    <span class="suggestion-icon">{{ prompt.icon }}</span>
                    <span class="suggestion-title">{{ prompt.title }}</span>
                    <span class="suggestion-desc">{{ prompt.description }}</span>
                  </button>
                </div>
              </div>

              <template v-else>
                <div class="conversation-banner">
                  <span class="conversation-pill">基於原始碼的回答</span>
                  <p>建議持續追問「在哪個檔案」、「資料怎麼流動」或「Controller 如何協作」。</p>
                </div>

                <div v-for="msg in messages" :key="msg.id" class="message-row" :class="msg.role">
                  <div class="message-avatar">
                    <span>{{ msg.role === 'user' ? '你' : 'AI' }}</span>
                  </div>

                  <div class="message-stack">
                    <div class="message-meta">
                      <span class="message-author">{{ msg.role === 'user' ? '你' : '原始碼助手' }}</span>
                      <span class="message-time">{{ formatTime(msg.createdAt) }}</span>
                    </div>

                    <div class="message-bubble" :class="{ loading: msg.isLoading, error: msg.isError }">
                      <div v-if="msg.isLoading" class="loading-state" role="status" aria-live="polite">
                        <span class="loading-dots" aria-hidden="true">
                          <span></span>
                          <span></span>
                          <span></span>
                        </span>
                        <span>{{ msg.content }}</span>
                      </div>
                      <div v-else-if="msg.role === 'assistant'" v-html="renderMarkdown(msg.content)"></div>
                      <div v-else>{{ msg.content }}</div>
                    </div>
                  </div>
                </div>
              </template>
            </div>

            <div class="overlay-input">
              <div class="composer-shell">
                <div class="composer-top">
                  <div class="composer-hints">
                    <span class="composer-chip">Enter 送出</span>
                    <span class="composer-chip subtle">Shift + Enter 換行</span>
                  </div>
                  <span class="composer-count">{{ inputLength }} 字</span>
                </div>

                <div class="input-wrapper">
                  <textarea
                    ref="textareaRef"
                    v-model="question"
                    @input="autoResizeTextarea"
                    @keydown="handleKeydown"
                    :disabled="isLoading"
                    placeholder="試著詢問：這個專案的 reconciliation 流程是怎麼串起來的？"
                    rows="1"
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
                  <span class="status-dot small"></span>
                  本地模式 — claude CLI 直接讀取原始碼
                </div>
              </div>
            </div>
          </section>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.chat-fade-enter-active,
.chat-fade-leave-active {
  transition: opacity 0.22s ease;
}

.chat-fade-enter-from,
.chat-fade-leave-to {
  opacity: 0;
}

.chat-bubble {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 1000;
  width: 64px;
  height: 64px;
  border: 1px solid rgba(255, 255, 255, 0.28);
  border-radius: 22px;
  background:
    radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.35), transparent 45%),
    linear-gradient(135deg, var(--vp-c-brand-1), #7c3aed);
  color: white;
  cursor: pointer;
  box-shadow: 0 18px 45px rgba(79, 70, 229, 0.38);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: visible;
}

.chat-bubble:hover {
  transform: translateY(-3px) scale(1.03);
  box-shadow: 0 24px 50px rgba(79, 70, 229, 0.45);
}

.chat-bubble.has-messages {
  animation: bubble-float 3s ease-in-out infinite;
}

@keyframes bubble-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

.bubble-icon {
  position: relative;
  z-index: 2;
  font-size: 28px;
}

.bubble-glow {
  position: absolute;
  inset: 10px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.14);
  backdrop-filter: blur(10px);
}

.bubble-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  min-width: 22px;
  height: 22px;
  padding: 0 6px;
  border-radius: 999px;
  background: linear-gradient(135deg, #f97316, #ef4444);
  color: white;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid white;
  box-shadow: 0 10px 20px rgba(239, 68, 68, 0.35);
}

.chat-overlay {
  position: fixed;
  inset: 0;
  z-index: 9000;
  display: flex;
  flex-direction: column;
  font-family: var(--vp-font-family-base);
  background: var(--vp-c-bg);
}

.overlay-backdrop {
  display: none;
}

.chat-shell {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--vp-c-bg);
  overflow: hidden;
}

.chat-overlay.dark .chat-shell {
  background: var(--vp-c-bg);
}

.shell-noise {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-image:
    radial-gradient(circle at 20% 20%, rgba(99, 102, 241, 0.12), transparent 22%),
    radial-gradient(circle at 80% 0%, rgba(59, 130, 246, 0.1), transparent 18%),
    radial-gradient(circle at 50% 100%, rgba(244, 114, 182, 0.08), transparent 20%);
}

.overlay-header {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 22px 24px 20px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.16);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.55), rgba(255, 255, 255, 0.28));
  backdrop-filter: blur(16px);
  flex-shrink: 0;
}

.chat-overlay.dark .overlay-header {
  background: linear-gradient(180deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.35));
}

.header-left,
.header-right {
  display: flex;
  align-items: center;
}

.header-left {
  gap: 16px;
}

.header-right {
  gap: 10px;
}

.assistant-orb {
  width: 52px;
  height: 52px;
  border-radius: 18px;
  background:
    radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.42), transparent 38%),
    linear-gradient(135deg, var(--vp-c-brand-1), #7c3aed);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  box-shadow: 0 14px 28px rgba(79, 70, 229, 0.28);
}

.header-copy {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.header-eyebrow {
  margin: 0;
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--vp-c-text-3);
}

.header-main {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.header-title {
  font-size: 22px;
  font-weight: 800;
  color: var(--vp-c-text-1);
}

.project-badge {
  padding: 5px 12px;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.12);
  border: 1px solid rgba(99, 102, 241, 0.2);
  color: var(--vp-c-brand-1);
  font-size: 12px;
  font-weight: 700;
}

.header-subtitle {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--vp-c-text-2);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 0 6px rgba(34, 197, 94, 0.12);
  flex-shrink: 0;
}

.status-dot.small {
  width: 7px;
  height: 7px;
  box-shadow: 0 0 0 5px rgba(34, 197, 94, 0.1);
}

.header-stats {
  display: flex;
  gap: 10px;
}

.stat-chip {
  min-width: 72px;
  padding: 8px 10px;
  border-radius: 16px;
  background: rgba(148, 163, 184, 0.12);
  border: 1px solid rgba(148, 163, 184, 0.16);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.stat-chip strong {
  font-size: 16px;
  line-height: 1;
  color: var(--vp-c-text-1);
}

.stat-chip span {
  font-size: 11px;
  color: var(--vp-c-text-3);
}

.header-hint {
  font-size: 12px;
  color: var(--vp-c-text-3);
}

.header-btn {
  width: 38px;
  height: 38px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 12px;
  background: rgba(148, 163, 184, 0.1);
  color: var(--vp-c-text-2);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.15s ease, background 0.15s ease, color 0.15s ease;
}

.header-btn:hover {
  transform: translateY(-1px);
  background: rgba(99, 102, 241, 0.12);
  color: var(--vp-c-text-1);
}

.overlay-messages {
  position: relative;
  flex: 1;
  overflow-y: auto;
  padding: 28px 28px 18px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  background:
    linear-gradient(180deg, rgba(99, 102, 241, 0.03), transparent 20%),
    transparent;
}

.overlay-messages.empty {
  justify-content: center;
}

.empty-state {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(0, 0.95fr);
  gap: 22px;
  align-items: stretch;
}

.empty-hero,
.suggestion-card,
.conversation-banner,
.message-bubble,
.composer-shell {
  backdrop-filter: blur(14px);
}

.empty-hero {
  padding: 32px;
  border-radius: 26px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  background:
    radial-gradient(circle at top right, rgba(99, 102, 241, 0.15), transparent 30%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.7), rgba(255, 255, 255, 0.5));
}

.chat-overlay.dark .empty-hero {
  background:
    radial-gradient(circle at top right, rgba(99, 102, 241, 0.2), transparent 30%),
    linear-gradient(180deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.5));
}

.hero-badge {
  display: inline-flex;
  padding: 6px 11px;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.1);
  color: var(--vp-c-brand-1);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.empty-hero h2 {
  margin: 18px 0 12px;
  font-size: 32px;
  line-height: 1.12;
  color: var(--vp-c-text-1);
}

.empty-hero p {
  margin: 0;
  font-size: 15px;
  line-height: 1.8;
  color: var(--vp-c-text-2);
}

.feature-pills {
  margin-top: 22px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.feature-pills span {
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.12);
  color: var(--vp-c-text-2);
  font-size: 12px;
  border: 1px solid rgba(148, 163, 184, 0.12);
}

.project-emphasis {
  color: var(--vp-c-text-1);
  font-weight: 800;
}

.suggestions-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.suggestion-card {
  padding: 22px 18px;
  border-radius: 22px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.72), rgba(255, 255, 255, 0.48));
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
  text-align: left;
  transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
}

.chat-overlay.dark .suggestion-card {
  background: linear-gradient(180deg, rgba(30, 41, 59, 0.72), rgba(15, 23, 42, 0.56));
}

.suggestion-card:hover {
  transform: translateY(-3px);
  border-color: rgba(99, 102, 241, 0.28);
  box-shadow: 0 18px 36px rgba(79, 70, 229, 0.14);
}

.suggestion-icon {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: rgba(99, 102, 241, 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.suggestion-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--vp-c-text-1);
}

.suggestion-desc {
  font-size: 13px;
  line-height: 1.6;
  color: var(--vp-c-text-2);
}

.conversation-banner {
  padding: 12px 16px;
  border-radius: 18px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  background: rgba(148, 163, 184, 0.08);
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.conversation-banner p {
  margin: 0;
  color: var(--vp-c-text-2);
  font-size: 13px;
}

.conversation-pill {
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.12);
  color: var(--vp-c-brand-1);
  font-size: 12px;
  font-weight: 700;
}

.message-row {
  display: flex;
  gap: 14px;
  align-items: flex-start;
}

.message-row.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 42px;
  height: 42px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: white;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.04em;
  box-shadow: 0 14px 24px rgba(15, 23, 42, 0.15);
}

.message-row.assistant .message-avatar {
  background: linear-gradient(135deg, var(--vp-c-brand-1), #7c3aed);
}

.message-row.user .message-avatar {
  background: linear-gradient(135deg, #0f766e, #14b8a6);
}

.message-stack {
  display: flex;
  flex-direction: column;
  gap: 7px;
  width: min(100%, 760px);
}

.message-row.user .message-stack {
  align-items: flex-end;
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 4px;
  font-size: 12px;
}

.message-row.user .message-meta {
  justify-content: flex-end;
}

.message-author {
  font-weight: 700;
  color: var(--vp-c-text-1);
}

.message-time {
  color: var(--vp-c-text-3);
}

.message-bubble {
  max-width: 100%;
  padding: 16px 18px;
  border-radius: 22px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.74), rgba(255, 255, 255, 0.55));
  color: var(--vp-c-text-1);
  font-size: 15px;
  line-height: 1.75;
  word-break: break-word;
  box-shadow: 0 18px 32px rgba(15, 23, 42, 0.06);
}

.chat-overlay.dark .message-bubble {
  background: linear-gradient(180deg, rgba(30, 41, 59, 0.76), rgba(15, 23, 42, 0.58));
}

.message-row.user .message-bubble {
  background:
    linear-gradient(135deg, rgba(20, 184, 166, 0.18), rgba(13, 148, 136, 0.12)),
    linear-gradient(180deg, rgba(255, 255, 255, 0.78), rgba(255, 255, 255, 0.62));
  border-top-right-radius: 8px;
}

.chat-overlay.dark .message-row.user .message-bubble {
  background:
    linear-gradient(135deg, rgba(20, 184, 166, 0.18), rgba(13, 148, 136, 0.12)),
    linear-gradient(180deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.62));
}

.message-row.assistant .message-bubble {
  border-top-left-radius: 8px;
}

.message-bubble.loading {
  color: var(--vp-c-text-2);
}

.message-bubble.error {
  background: linear-gradient(180deg, rgba(254, 242, 242, 0.96), rgba(254, 226, 226, 0.9));
  border-color: rgba(239, 68, 68, 0.35);
  color: #b91c1c;
}

.chat-overlay.dark .message-bubble.error {
  background: linear-gradient(180deg, rgba(127, 29, 29, 0.65), rgba(69, 10, 10, 0.58));
  color: #fecaca;
}

.loading-state {
  display: inline-flex;
  align-items: center;
  gap: 12px;
}

.loading-dots {
  display: inline-flex;
  gap: 5px;
}

.loading-dots span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
  opacity: 0.3;
  animation: dot-wave 1s ease-in-out infinite;
}

.loading-dots span:nth-child(2) { animation-delay: 0.12s; }
.loading-dots span:nth-child(3) { animation-delay: 0.24s; }

@keyframes dot-wave {
  0%, 100% { opacity: 0.28; transform: translateY(0); }
  50% { opacity: 1; transform: translateY(-2px); }
}

.message-row.assistant .message-bubble :deep(h1),
.message-row.assistant .message-bubble :deep(h2),
.message-row.assistant .message-bubble :deep(h3),
.message-row.assistant .message-bubble :deep(h4) {
  margin: 18px 0 10px;
  font-weight: 800;
  line-height: 1.32;
  color: var(--vp-c-text-1);
}

.message-row.assistant .message-bubble :deep(h1) { font-size: 22px; }
.message-row.assistant .message-bubble :deep(h2) {
  font-size: 19px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.16);
  padding-bottom: 6px;
}
.message-row.assistant .message-bubble :deep(h3) { font-size: 17px; }
.message-row.assistant .message-bubble :deep(h4) { font-size: 15px; }

.message-row.assistant .message-bubble :deep(p) {
  margin: 8px 0;
}

.message-row.assistant .message-bubble :deep(ul),
.message-row.assistant .message-bubble :deep(ol) {
  margin: 10px 0;
  padding-left: 24px;
}

.message-row.assistant .message-bubble :deep(li) {
  margin: 4px 0;
}

.message-row.assistant .message-bubble :deep(pre) {
  background: rgba(15, 23, 42, 0.94);
  color: #e2e8f0;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 14px;
  padding: 14px 16px;
  overflow-x: auto;
  margin: 14px 0;
  font-size: 13px;
  line-height: 1.7;
}

.message-row.assistant .message-bubble :deep(code) {
  font-family: var(--vp-font-family-mono);
  font-size: 13px;
  background: rgba(99, 102, 241, 0.12);
  padding: 2px 6px;
  border-radius: 6px;
  color: var(--vp-c-brand-1);
}

.message-row.assistant .message-bubble :deep(pre code) {
  background: none;
  padding: 0;
  color: inherit;
}

.message-row.assistant .message-bubble :deep(blockquote) {
  border-left: 3px solid var(--vp-c-brand-1);
  padding-left: 12px;
  margin: 10px 0;
  color: var(--vp-c-text-2);
}

.message-row.assistant .message-bubble :deep(strong) {
  font-weight: 800;
  color: var(--vp-c-text-1);
}

.message-row.assistant .message-bubble :deep(a) {
  color: var(--vp-c-brand-1);
  text-decoration: underline;
}

.message-row.assistant .message-bubble :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 14px 0;
  font-size: 13px;
  overflow: hidden;
}

.message-row.assistant .message-bubble :deep(th),
.message-row.assistant .message-bubble :deep(td) {
  border: 1px solid rgba(148, 163, 184, 0.16);
  padding: 9px 12px;
  text-align: left;
}

.message-row.assistant .message-bubble :deep(th) {
  background: rgba(148, 163, 184, 0.08);
  font-weight: 700;
}

.overlay-input {
  position: relative;
  padding: 16px 20px 20px;
  border-top: 1px solid rgba(148, 163, 184, 0.16);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.6));
  flex-shrink: 0;
}

.chat-overlay.dark .overlay-input {
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.32), rgba(15, 23, 42, 0.62));
}

.composer-shell {
  max-width: 960px;
  margin: 0 auto;
  padding: 14px;
  border-radius: 24px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  background: rgba(255, 255, 255, 0.72);
}

.chat-overlay.dark .composer-shell {
  background: rgba(15, 23, 42, 0.72);
}

.composer-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}

.composer-hints {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.composer-chip {
  padding: 5px 9px;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.12);
  color: var(--vp-c-brand-1);
  font-size: 11px;
  font-weight: 700;
}

.composer-chip.subtle {
  background: rgba(148, 163, 184, 0.12);
  color: var(--vp-c-text-2);
}

.composer-count {
  font-size: 12px;
  color: var(--vp-c-text-3);
}

.input-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.input-wrapper textarea {
  flex: 1;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 18px;
  padding: 14px 16px;
  font-size: 15px;
  resize: none;
  background: rgba(255, 255, 255, 0.74);
  color: var(--vp-c-text-1);
  font-family: var(--vp-font-family-base);
  outline: none;
  line-height: 1.6;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
  min-height: 56px;
  max-height: 180px;
}

.chat-overlay.dark .input-wrapper textarea {
  background: rgba(15, 23, 42, 0.66);
}

.input-wrapper textarea:focus {
  border-color: rgba(99, 102, 241, 0.48);
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.12);
}

.input-wrapper textarea:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.send-btn {
  width: 56px;
  height: 56px;
  border: none;
  border-radius: 18px;
  background: linear-gradient(135deg, var(--vp-c-brand-1), #7c3aed);
  color: white;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.15s ease, box-shadow 0.15s ease, opacity 0.15s ease;
  flex-shrink: 0;
  box-shadow: 0 18px 30px rgba(79, 70, 229, 0.26);
}

.send-btn:not(:disabled):hover {
  transform: translateY(-2px);
  box-shadow: 0 22px 34px rgba(79, 70, 229, 0.32);
}

.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.input-footer {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: var(--vp-c-text-3);
}

@media (max-width: 960px) {
  .chat-overlay {
    padding: 12px;
  }

  .chat-shell {
    width: 100%;
    height: 100%;
  }

  .empty-state {
    grid-template-columns: 1fr;
  }

  .overlay-header {
    padding: 18px;
  }

  .header-right {
    flex-wrap: wrap;
    justify-content: flex-end;
  }

  .header-hint {
    display: none;
  }

  .overlay-messages {
    padding: 22px 18px 16px;
  }
}

@media (max-width: 768px) {
  .chat-bubble {
    right: 16px;
    bottom: 16px;
    width: 58px;
    height: 58px;
    border-radius: 20px;
  }

  .overlay-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-right,
  .header-stats {
    width: 100%;
  }

  .header-right {
    justify-content: space-between;
  }

  .header-stats {
    order: 2;
  }

  .stat-chip {
    flex: 1;
  }

  .empty-hero {
    padding: 24px;
  }

  .empty-hero h2 {
    font-size: 26px;
  }

  .suggestions-grid {
    grid-template-columns: 1fr;
  }

  .message-row,
  .message-row.user {
    flex-direction: column;
  }

  .message-stack,
  .message-row.user .message-stack {
    width: 100%;
    align-items: stretch;
  }

  .message-row.user .message-meta {
    justify-content: flex-start;
  }

  .message-avatar {
    width: 36px;
    height: 36px;
    border-radius: 14px;
  }

  .composer-top,
  .input-wrapper {
    flex-direction: column;
    align-items: stretch;
  }

  .send-btn {
    width: 100%;
    height: 48px;
    border-radius: 14px;
  }
}
</style>
