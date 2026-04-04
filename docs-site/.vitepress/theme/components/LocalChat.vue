<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { useRoute } from 'vitepress'

const route = useRoute()
const isOpen = ref(false)
const isExpanded = ref(false)
const question = ref('')
const messages = ref([])
const isLoading = ref(false)
const messagesContainer = ref(null)

const isDev = import.meta.env.DEV

const currentProject = computed(() => {
  const path = route.path
  const projects = [
    'kubevirt',
    'containerized-data-importer',
    'monitoring',
    'common-instancetypes',
    'node-maintenance-operator',
    'forklift',
  ]
  for (const p of projects) {
    if (path.includes(`/${p}/`) || path.includes(`/${p}`)) return p
  }
  return null
})

const projectLabel = computed(() => {
  const labels = {
    'kubevirt': 'KubeVirt',
    'containerized-data-importer': 'CDI',
    'monitoring': 'Monitoring',
    'common-instancetypes': 'Instancetypes',
    'node-maintenance-operator': 'NMO',
    'forklift': 'Forklift',
  }
  return labels[currentProject.value] || '全域'
})

async function scrollToBottom() {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

async function sendMessage() {
  const q = question.value.trim()
  if (!q || isLoading.value) return

  messages.value.push({ role: 'user', content: q })
  question.value = ''
  isLoading.value = true
  await scrollToBottom()

  const thinkingMsg = { role: 'assistant', content: '🔍 正在分析原始碼...', isLoading: true }
  messages.value.push(thinkingMsg)
  await scrollToBottom()

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        project: currentProject.value,
        question: q,
      }),
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
        if (line.startsWith('event: status')) {
          // update thinking message
          const dataLine = lines[lines.indexOf(line) + 1]
          if (dataLine?.startsWith('data: ')) {
            try {
              const data = JSON.parse(dataLine.slice(6))
              thinkingMsg.content = `🔍 ${data.message}`
            } catch {}
          }
        } else if (line.startsWith('data: ') && !line.includes('"status"')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.result) {
              // Remove thinking message and add real response
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
    const idx = messages.value.indexOf(thinkingMsg)
    if (idx !== -1) messages.value.splice(idx, 1)
    messages.value.push({ role: 'assistant', content: `❌ 連線失敗：${err.message}`, isError: true })
  } finally {
    isLoading.value = false
    await scrollToBottom()
  }
}

function clearChat() {
  messages.value = []
}

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}
</script>

<template>
  <div v-if="isDev" class="local-chat">
    <!-- Toggle Button -->
    <button
      class="chat-toggle"
      :class="{ active: isOpen }"
      @click="isOpen = !isOpen"
      :title="isOpen ? '關閉 AI 助手' : '開啟 AI 助手'"
    >
      <span v-if="!isOpen">🤖</span>
      <span v-else>✕</span>
    </button>

    <!-- Chat Panel -->
    <div v-show="isOpen" class="chat-panel" :class="{ expanded: isExpanded }">
      <div class="chat-header">
        <div class="chat-title">
          <span>🤖 原始碼助手</span>
          <span class="project-badge">{{ projectLabel }}</span>
        </div>
        <div class="chat-actions">
          <button @click="isExpanded = !isExpanded" :title="isExpanded ? '縮小' : '放大'" class="expand-btn">
            {{ isExpanded ? '⊟' : '⊞' }}
          </button>
          <button @click="clearChat" title="清除對話" class="clear-btn">🗑️</button>
        </div>
      </div>

      <div class="chat-hint">
        💡 本地模式 — 使用 claude CLI 即時分析原始碼
      </div>

      <div ref="messagesContainer" class="chat-messages">
        <div v-if="messages.length === 0" class="chat-empty">
          <p>詢問任何關於 <strong>{{ projectLabel }}</strong> 原始碼的問題</p>
          <div class="suggestions">
            <button @click="question = '這個專案的核心架構是什麼？'; sendMessage()">核心架構？</button>
            <button @click="question = '主要的 Controller 有哪些？'; sendMessage()">主要 Controller？</button>
            <button @click="question = 'CRD 有哪些欄位？'; sendMessage()">CRD 欄位？</button>
          </div>
        </div>

        <div
          v-for="(msg, i) in messages"
          :key="i"
          class="chat-message"
          :class="[msg.role, { loading: msg.isLoading, error: msg.isError }]"
        >
          <div class="message-content" v-html="msg.role === 'assistant' && !msg.isLoading ? formatMarkdown(msg.content) : msg.content" />
        </div>
      </div>

      <div class="chat-input">
        <textarea
          v-model="question"
          @keydown="handleKeydown"
          :disabled="isLoading"
          placeholder="輸入問題... (Enter 送出)"
          rows="2"
        />
        <button @click="sendMessage" :disabled="isLoading || !question.trim()" class="send-btn">
          {{ isLoading ? '⏳' : '📤' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  methods: {
    formatMarkdown(text) {
      if (!text) return ''
      return text
        // code blocks
        .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>')
        // inline code
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        // bold
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
        // headers
        .replace(/^### (.+)$/gm, '<h4>$1</h4>')
        .replace(/^## (.+)$/gm, '<h3>$1</h3>')
        // line breaks
        .replace(/\n/g, '<br>')
    }
  }
}
</script>

<style scoped>
.local-chat {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
  font-family: var(--vp-font-family-base);
}

.chat-toggle {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: none;
  background: var(--vp-c-brand-1);
  color: white;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  transition: transform 0.2s, background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-toggle:hover {
  transform: scale(1.1);
}

.chat-toggle.active {
  background: var(--vp-c-gray-2);
  color: var(--vp-c-text-1);
}

.chat-panel {
  position: fixed;
  bottom: 80px;
  right: 20px;
  width: 520px;
  max-height: 70vh;
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-border);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: all 0.3s ease;
}

.chat-panel.expanded {
  width: 75vw;
  max-width: 900px;
  max-height: 85vh;
  bottom: 40px;
  right: 40px;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--vp-c-border);
  background: var(--vp-c-bg-soft);
}

.chat-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 14px;
}

.project-badge {
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
}

.chat-actions {
  display: flex;
  gap: 4px;
}

.chat-actions .expand-btn,
.chat-actions .clear-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  padding: 4px 6px;
  border-radius: 4px;
}

.chat-actions .expand-btn:hover,
.chat-actions .clear-btn:hover {
  background: var(--vp-c-bg-mute);
}

.chat-hint {
  padding: 6px 16px;
  font-size: 11px;
  color: var(--vp-c-text-3);
  background: var(--vp-c-bg-soft);
  border-bottom: 1px solid var(--vp-c-border);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  min-height: 280px;
  max-height: 55vh;
}

.chat-empty {
  text-align: center;
  color: var(--vp-c-text-3);
  padding: 24px 0;
}

.chat-empty p {
  margin-bottom: 16px;
  font-size: 14px;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: center;
}

.suggestions button {
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-border);
  border-radius: 16px;
  padding: 4px 12px;
  font-size: 12px;
  cursor: pointer;
  color: var(--vp-c-text-2);
  transition: all 0.2s;
}

.suggestions button:hover {
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1);
  border-color: var(--vp-c-brand-1);
}

.chat-message {
  margin-bottom: 10px;
  line-height: 1.5;
}

.chat-message.user {
  text-align: right;
}

.chat-message.user .message-content {
  display: inline-block;
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-text-1);
  padding: 10px 14px;
  border-radius: 12px 12px 0 12px;
  max-width: 85%;
  text-align: left;
  font-size: 14px;
  line-height: 1.6;
}

.chat-message.assistant .message-content {
  background: var(--vp-c-bg-soft);
  padding: 12px 16px;
  border-radius: 12px 12px 12px 0;
  font-size: 14px;
  line-height: 1.7;
  max-width: 95%;
  word-break: break-word;
}

.chat-message.assistant .message-content :deep(pre) {
  background: var(--vp-c-bg-mute);
  padding: 8px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 6px 0;
  font-size: 12px;
}

.chat-message.assistant .message-content :deep(code) {
  font-size: 12px;
  background: var(--vp-c-bg-mute);
  padding: 1px 4px;
  border-radius: 3px;
}

.chat-message.assistant .message-content :deep(pre code) {
  background: none;
  padding: 0;
}

.chat-message.loading .message-content {
  color: var(--vp-c-text-3);
  animation: pulse 1.5s infinite;
}

.chat-message.error .message-content {
  background: var(--vp-c-danger-soft);
  color: var(--vp-c-danger-1);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.chat-input {
  display: flex;
  gap: 8px;
  padding: 10px 12px;
  border-top: 1px solid var(--vp-c-border);
  background: var(--vp-c-bg-soft);
}

.chat-input textarea {
  flex: 1;
  border: 1px solid var(--vp-c-border);
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 14px;
  resize: none;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-family: var(--vp-font-family-base);
  outline: none;
}

.chat-input textarea:focus {
  border-color: var(--vp-c-brand-1);
}

.chat-input textarea:disabled {
  opacity: 0.6;
}

.send-btn {
  width: 40px;
  border: none;
  background: var(--vp-c-brand-1);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: opacity 0.2s;
}

.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.send-btn:not(:disabled):hover {
  opacity: 0.9;
}

@media (max-width: 768px) {
  .chat-panel {
    width: calc(100vw - 32px);
    right: 16px;
    bottom: 80px;
    max-height: 75vh;
  }
  .chat-panel.expanded {
    width: calc(100vw - 16px);
    right: 8px;
    bottom: 8px;
    max-height: 92vh;
    max-width: unset;
  }
}
</style>
