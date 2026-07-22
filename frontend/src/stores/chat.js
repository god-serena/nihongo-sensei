import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useChatStore = defineStore('chat', () => {
  const messages = ref([])          // { role: 'user'|'assistant', content: string }
  const partialResponse = ref('')   // accumulates streaming tokens during live TTS
  const wsStatus = ref('closed')    // 'closed' | 'connecting' | 'open' | 'error'

  function appendToken(token) {
    partialResponse.value += token
  }

  function commitResponse() {
    if (partialResponse.value) {
      messages.value.push({ role: 'assistant', content: partialResponse.value })
      partialResponse.value = ''
    }
  }

  function addUserMessage(text) {
    messages.value.push({ role: 'user', content: text })
  }

  return { messages, partialResponse, wsStatus, appendToken, commitResponse, addUserMessage }
})
