<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="mermaid-zoom-overlay"
      @click.self="close"
      @wheel.prevent="onWheel"
    >
      <button class="mermaid-zoom-close" @click="close" aria-label="關閉">&times;</button>
      <div class="mermaid-zoom-hint">滾輪縮放 · 拖曳移動</div>
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

const contentStyle = computed(() => ({
  transform: `translate(${translateX.value}px, ${translateY.value}px) scale(${scale.value})`,
  transformOrigin: 'center center',
  cursor: dragging.value ? 'grabbing' : 'grab',
}))

function open(svgHtml) {
  // Content comes from same-page mermaid-rendered SVGs (already sanitized by the plugin)
  svgContent.value = svgHtml
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
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
}

.mermaid-zoom-close {
  position: fixed;
  top: 16px;
  right: 16px;
  z-index: 10001;
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  font-size: 28px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.mermaid-zoom-close:hover {
  background: rgba(255, 255, 255, 0.35);
}

.mermaid-zoom-hint {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10001;
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
  pointer-events: none;
  user-select: none;
}

.mermaid-zoom-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.mermaid-zoom-content {
  transition: transform 0.1s ease-out;
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.mermaid-zoom-content :deep(svg) {
  max-width: 100%;
  height: auto;
}
</style>
