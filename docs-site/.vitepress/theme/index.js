import DefaultTheme from 'vitepress/theme'
import LocalChat from './components/LocalChat.vue'
import MermaidZoom from './components/MermaidZoom.vue'
import QuizQuestion from './components/QuizQuestion.vue'
import { h } from 'vue'

export default {
  extends: DefaultTheme,
  Layout() {
    return h(DefaultTheme.Layout, null, {
      'layout-bottom': () => [h(LocalChat), h(MermaidZoom)],
    })
  },
  enhanceApp({ app }) {
    app.component('QuizQuestion', QuizQuestion)
  },
}
