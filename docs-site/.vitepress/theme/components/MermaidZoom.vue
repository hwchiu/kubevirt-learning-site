<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="mermaid-zoom-overlay"
      :class="{ 'mermaid-zoom-dark': isDark }"
      @click.self="close"
      @wheel.prevent="onWheel"
    >
      <!-- Toolbar: zoom controls + close -->
      <div class="mermaid-zoom-toolbar">
        <button class="mermaid-zoom-btn" @click="zoomIn" aria-label="放大" title="放大">＋</button>
        <span class="mermaid-zoom-level">{{ zoomPercent }}%</span>
        <button class="mermaid-zoom-btn" @click="zoomOut" aria-label="縮小" title="縮小">－</button>
        <button class="mermaid-zoom-btn" @click="resetView" aria-label="重置" title="重置檢視">⟳</button>
        <div class="mermaid-zoom-separator" />
        <button class="mermaid-zoom-btn mermaid-zoom-btn-close" @click="close" aria-label="關閉" title="關閉">&times;</button>
      </div>
      <div class="mermaid-zoom-hint">滾輪縮放 · 拖曳移動 · 按鈕放大縮小</div>
      <div
        ref="container"
        class="mermaid-zoom-container"
        @mousedown.prevent="startDrag"
        @touchstart.prevent="onTouchStart"
      >
        <div
          class="mermaid-zoom-content"
          :style="contentStyle"
          v-html="svgContent"
        />
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useData } from 'vitepress'

const { isDark } = useData()

const visible = ref(false)
const svgContent = ref('')
const scale = ref(1)
const translateX = ref(0)
const translateY = ref(0)

// Drag state
const dragging = ref(false)
const dragStartX = ref(0)
const dragStartY = ref(0)
const dragStartTX = ref(0)
const dragStartTY = ref(0)

const MIN_SCALE = 0.2
const MAX_SCALE = 5
const ZOOM_STEP = 0.25

const zoomPercent = computed(() => Math.round(scale.value * 100))

const contentStyle = computed(() => ({
  transform: `translate(${translateX.value}px, ${translateY.value}px) scale(${scale.value})`,
  transformOrigin: 'center center',
  cursor: dragging.value ? 'grabbing' : 'grab',
}))

function zoomIn() {
  scale.value = Math.min(MAX_SCALE, scale.value + ZOOM_STEP)
}

function zoomOut() {
  scale.value = Math.max(MIN_SCALE, scale.value - ZOOM_STEP)
}

function resetView() {
  scale.value = 1
  translateX.value = 0
  translateY.value = 0
}

/**
 * Fix SVG dimensions so it renders correctly in the zoom overlay.
 * Mermaid SVGs use width="100%" which collapses to 0px inside a flex container.
 * We extract the viewBox dimensions and set explicit pixel sizes instead.
 */
function processSvgHtml(svgHtml) {
  const temp = document.createElement('div')
  temp.innerHTML = svgHtml
  const svg = temp.querySelector('svg')
  if (!svg) return svgHtml

  const viewBox = svg.getAttribute('viewBox')
  if (viewBox) {
    const parts = viewBox.trim().split(/[\s,]+/)
    const vbWidth = parseFloat(parts[2])
    const vbHeight = parseFloat(parts[3])
    if (vbWidth > 0 && vbHeight > 0) {
      svg.removeAttribute('width')
      svg.removeAttribute('height')
      svg.style.width = vbWidth + 'px'
      svg.style.height = vbHeight + 'px'
      svg.style.maxWidth = 'calc(100vw - 32px)'
      svg.style.maxHeight = 'calc(100vh - 116px)' /* 48px toolbar + 36px hint + 32px padding */
    }
  }

  return temp.innerHTML
}

function open(svgHtml) {
  // Content comes from same-page mermaid-rendered SVGs (already sanitized by the plugin)
  svgContent.value = processSvgHtml(svgHtml)
  scale.value = 1
  translateX.value = 0
  translateY.value = 0
  visible.value = true
  document.body.style.overflow = 'hidden'
}

function close() {
  visible.value = false
  svgContent.value = ''
  document.body.style.overflow = ''
}

function onWheel(e) {
  const delta = e.deltaY > 0 ? -0.1 : 0.1
  const newScale = Math.min(MAX_SCALE, Math.max(MIN_SCALE, scale.value + delta))
  scale.value = newScale
}

// Mouse drag
function startDrag(e) {
  dragging.value = true
  dragStartX.value = e.clientX
  dragStartY.value = e.clientY
  dragStartTX.value = translateX.value
  dragStartTY.value = translateY.value
  window.addEventListener('mousemove', onDrag)
  window.addEventListener('mouseup', stopDrag)
}

function onDrag(e) {
  if (!dragging.value) return
  translateX.value = dragStartTX.value + (e.clientX - dragStartX.value)
  translateY.value = dragStartTY.value + (e.clientY - dragStartY.value)
}

function stopDrag() {
  dragging.value = false
  window.removeEventListener('mousemove', onDrag)
  window.removeEventListener('mouseup', stopDrag)
}

// Touch support for mobile drag
function onTouchStart(e) {
  if (e.touches.length === 1) {
    dragging.value = true
    dragStartX.value = e.touches[0].clientX
    dragStartY.value = e.touches[0].clientY
    dragStartTX.value = translateX.value
    dragStartTY.value = translateY.value
    window.addEventListener('touchmove', onTouchMove, { passive: false })
    window.addEventListener('touchend', onTouchEnd)
  }
}

function onTouchMove(e) {
  e.preventDefault()
  if (!dragging.value || e.touches.length !== 1) return
  translateX.value = dragStartTX.value + (e.touches[0].clientX - dragStartX.value)
  translateY.value = dragStartTY.value + (e.touches[0].clientY - dragStartY.value)
}

function onTouchEnd() {
  dragging.value = false
  window.removeEventListener('touchmove', onTouchMove)
  window.removeEventListener('touchend', onTouchEnd)
}

// Keyboard: Escape to close
function onKeydown(e) {
  if (e.key === 'Escape' && visible.value) {
    close()
  }
}

// Attach click listeners to all mermaid diagrams
function attachListeners() {
  document.querySelectorAll('.mermaid').forEach((el) => {
    if (el.dataset.zoomBound) return
    el.dataset.zoomBound = 'true'
    el.style.cursor = 'pointer'
    el.title = '點擊放大檢視'
    el.addEventListener('click', () => {
      open(el.innerHTML)
    })
  })
}

let observer = null

onMounted(() => {
  window.addEventListener('keydown', onKeydown)

  // Initial attach
  nextTick(() => attachListeners())

  // Watch for dynamically rendered mermaid diagrams
  observer = new MutationObserver(() => {
    attachListeners()
  })
  observer.observe(document.body, { childList: true, subtree: true })
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
  if (observer) observer.disconnect()
  document.body.style.overflow = ''
})
</script>

<style scoped>
.mermaid-zoom-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: #1a1a1a;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ── Toolbar ── */
.mermaid-zoom-toolbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10001;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 2px;
  background: #1a1a1a;
  padding: 0 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.mermaid-zoom-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #fff;
  font-size: 20px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
  user-select: none;
}

.mermaid-zoom-btn:hover {
  background: rgba(255, 255, 255, 0.15);
}

.mermaid-zoom-btn:active {
  background: rgba(255, 255, 255, 0.25);
}

.mermaid-zoom-btn-close {
  font-size: 24px;
}

.mermaid-zoom-level {
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
  min-width: 44px;
  text-align: center;
  user-select: none;
  font-variant-numeric: tabular-nums;
}

.mermaid-zoom-separator {
  width: 1px;
  height: 24px;
  background: rgba(255, 255, 255, 0.2);
  margin: 0 4px;
}

/* ── Hint ── */
.mermaid-zoom-hint {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 10001;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1a1a1a;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
  pointer-events: none;
  user-select: none;
}

/* ── Content area — fill the entire viewport ── */
.mermaid-zoom-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: #fff;
  margin: 48px 0 36px 0;
}

.mermaid-zoom-dark .mermaid-zoom-container {
  background: #1b1b1f;
}

.mermaid-zoom-content {
  transition: transform 0.1s ease-out;
  padding: 16px;
}

.mermaid-zoom-content :deep(svg) {
  display: block;
}
</style>
