<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  question: { type: String, required: true },
  options: { type: Array, required: true },
  answer: { type: Number, required: true },
  explanation: { type: String, default: '' },
})

const selected = ref(null)
const revealed = ref(false)

const isCorrect = computed(() => selected.value === props.answer)

function select(index) {
  if (revealed.value) return
  selected.value = index
}

function reveal() {
  revealed.value = true
}

function reset() {
  selected.value = null
  revealed.value = false
}
</script>

<template>
  <div class="quiz-question">
    <p class="quiz-prompt">{{ question }}</p>
    <ul class="quiz-options">
      <li
        v-for="(opt, i) in options"
        :key="i"
        class="quiz-option"
        :class="{
          selected: selected === i && !revealed,
          correct: revealed && i === answer,
          wrong: revealed && selected === i && i !== answer,
        }"
        @click="select(i)"
      >
        <span class="quiz-label">{{ String.fromCharCode(65 + i) }}.</span>
        {{ opt }}
      </li>
    </ul>
    <div class="quiz-actions">
      <button v-if="!revealed" class="quiz-btn" :disabled="selected === null" @click="reveal">
        確認答案
      </button>
      <button v-else class="quiz-btn reset" @click="reset">重新作答</button>
    </div>
    <div v-if="revealed" class="quiz-result" :class="{ correct: isCorrect, wrong: !isCorrect }">
      <span v-if="isCorrect">✅ 正確！</span>
      <span v-else>❌ 錯誤，正確答案是 <strong>{{ String.fromCharCode(65 + answer) }}</strong></span>
      <p v-if="explanation" class="quiz-explanation">💡 {{ explanation }}</p>
    </div>
  </div>
</template>

<style scoped>
.quiz-question {
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  padding: 20px;
  margin: 16px 0;
  background: var(--vp-c-bg-soft);
}
.quiz-prompt {
  font-weight: 600;
  font-size: 1.05em;
  margin-bottom: 12px;
}
.quiz-options {
  list-style: none;
  padding: 0;
  margin: 0;
}
.quiz-option {
  padding: 10px 14px;
  margin: 6px 0;
  border: 2px solid var(--vp-c-divider);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}
.quiz-option:hover:not(.correct):not(.wrong) {
  border-color: var(--vp-c-brand-1);
  background: var(--vp-c-brand-soft);
}
.quiz-option.selected {
  border-color: var(--vp-c-brand-1);
  background: var(--vp-c-brand-soft);
}
.quiz-option.correct {
  border-color: var(--vp-c-green-1);
  background: var(--vp-c-green-soft);
  cursor: default;
}
.quiz-option.wrong {
  border-color: var(--vp-c-red-1);
  background: var(--vp-c-red-soft);
  cursor: default;
}
.quiz-label {
  font-weight: 700;
  margin-right: 6px;
}
.quiz-actions {
  margin-top: 12px;
}
.quiz-btn {
  padding: 8px 20px;
  border: none;
  border-radius: 6px;
  background: var(--vp-c-brand-1);
  color: var(--vp-c-white);
  font-size: 0.95em;
  cursor: pointer;
  transition: opacity 0.2s;
}
.quiz-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.quiz-btn:hover:not(:disabled) {
  opacity: 0.85;
}
.quiz-btn.reset {
  background: var(--vp-c-gray-1);
}
.quiz-result {
  margin-top: 14px;
  padding: 12px 16px;
  border-radius: 6px;
  font-weight: 500;
}
.quiz-result.correct {
  background: var(--vp-c-green-soft);
  border: 1px solid var(--vp-c-green-1);
}
.quiz-result.wrong {
  background: var(--vp-c-red-soft);
  border: 1px solid var(--vp-c-red-1);
}
.quiz-explanation {
  margin-top: 8px;
  font-weight: 400;
  font-size: 0.93em;
  line-height: 1.6;
}
</style>
