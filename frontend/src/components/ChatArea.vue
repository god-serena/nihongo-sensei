<template>
  <div class="chat-area flex flex-col h-full bg-gray-900 text-white">
    <!-- Message History -->
    <div ref="messageListRef" class="flex-1 overflow-y-auto p-4 space-y-3">
      <div v-for="(msg, idx) in chatStore.messages" :key="idx"
           :class="['max-w-[80%] rounded-lg px-4 py-2', msg.role === 'user' ? 'bg-indigo-600 ml-auto text-white' : 'bg-gray-700 mr-auto text-white']">
        <div class="text-sm">{{ msg.content }}</div>
      </div>

      <!-- Live partial response while streaming -->
      <div v-if="chatStore.partialResponse" class="max-w-[80%] rounded-lg px-4 py-2 bg-gray-700 mr-auto text-white">
        <div class="text-sm">{{ chatStore.partialResponse }}</div>
      </div>

      <!-- Error messages -->
      <div v-if="errorMessages.length" class="max-w-[80%] rounded-lg px-4 py-2 bg-red-700 mr-auto text-white">
        <div v-for="(err, i) in errorMessages" :key="i" class="text-sm">{{ err }}</div>
      </div>
    </div>

    <!-- Controls Bar -->
    <div class="flex items-center justify-between px-4 py-3 bg-gray-800 border-t border-gray-700">
      <!-- Voice Visualizer (left) -->
      <VoiceVisualizer :active="chatStore.messages.length > 0" class="w-24 h-12" />

      <!-- Push-to-Talk Button (center) -->
      <button
        ref="pttButtonRef"
        @mousedown="onPTTStart"
        @mouseup="onPTTEnd"
        @mouseleave="onPTTEnd"
        @touchstart.prevent="onPTTStart"
        @touchend.prevent="onPTTEnd"
        :class="[
          'px-6 py-2 rounded-full font-bold text-sm transition-colors',
              audioStore.isListening ? 'bg-red-500 hover:bg-red-400' : 'bg-indigo-600 hover:bg-indigo-500'
            ]"
        :disabled="chatStore.wsStatus !== 'open'"
      >
        {{ audioStore.isListening ? '● Releasing...' : 'Push-to-Talk' }}
      </button>

      <!-- Cancel / Interrupt Button (right, shown during TTS playback) -->
      <button
        v-if="audioStore.isSpeaking"
        @click="onCancelClick"
        class="px-4 py-2 rounded-full bg-red-600 hover:bg-red-500 text-white font-bold text-sm transition-colors"
      >
        ⏹ Cancel
      </button>

      <!-- WS status indicator -->
      <span v-if="chatStore.wsStatus !== 'open'" class="text-xs text-gray-400">
        {{ chatStore.wsStatus }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useAudioStore } from '@/stores/audio'
import { createSpeechWebSocket } from '@/services/api'
import VoiceVisualizer from './VoiceVisualizer.vue'

const chatStore = useChatStore()
const audioStore = useAudioStore()

const messageListRef = ref(null)
const pttButtonRef = ref(null)

// Track error messages for display
const errorMessages = ref([])

let ws = null

/**
 * WebSocket lifecycle management.
 */
function initWebSocket() {
  ws = createSpeechWebSocket()

  ws.onopen = () => {
    chatStore.wsStatus = 'open'
  }

  ws.onclose = () => {
    chatStore.wsStatus = 'closed'
  }

  ws.onerror = (e) => {
    chatStore.wsStatus = 'error'
    errorMessages.value.push('WebSocket error — check backend connection.')
  }

  ws.onmessage = async (event) => {
    const msg = JSON.parse(event.data)

    switch (msg.type) {
      case 'transcript':
        // User's spoken words appear as a message in chat
        chatStore.addUserMessage(msg.text)
        break

      case 'token':
        // Streaming LLM token — append to partial response display
        chatStore.appendToken(msg.token)
        await nextTick()
        scrollToBottom()
        break

      case 'audio':
        // Decode base64 audio chunk and play it
        try {
          const binary = atob(msg.data)
          let chunks = []
          for (let i = 0; i < binary.length; i++) {
            chunks.push(binary.charCodeAt(i))
          }
          const audioBlob = new Blob([new Uint8Array(chunks)], { type: 'audio/wav' })
          const audioUrl = URL.createObjectURL(audioBlob)
          const audio = new Audio(audioUrl)
          audio.onended = () => {
            // TTS playback finished — commit the accumulated response
            chatStore.commitResponse()
            audioStore.isSpeaking = false
          }
          audio.onerror = () => {
            errorMessages.value.push('Audio playback error.')
          }
          audioStore.isSpeaking = true
          audio.play().catch(err => console.error('TTS play failed:', err))
        } catch (e) {
          errorMessages.value.push(`Audio decode error: ${e.message}`)
        }
        break

      case 'done':
        // LLM generation finished — commit accumulated response
        chatStore.commitResponse()
        audioStore.isSpeaking = false
        break

      case 'cancelled':
        // Interrupted by cancel button — commit partial response
        chatStore.commitResponse()
        audioStore.isSpeaking = false
        errorMessages.value.push('Response cancelled.')
        break

      case 'error':
        errorMessages.value.push(msg.message)
        break

      default:
        console.warn('Unrecognized WS message type:', msg.type)
    }
  }
}

/**
 * Push-to-Talk handler.
 * On mousedown/touchstart, capture mic audio and send it over the WebSocket.
 */
async function onPTTStart() {
  if (ws.readyState !== WebSocket.OPEN) return

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    audioStore.startListening()

    // Record a short clip while held, then send it when released.
    const recorder = new MediaRecorder(stream)
    const chunks = []

    recorder.ondataavailable = (e) => {
      e.target.readOnly && chunks.push(e.data)
      if (!e.target.readOnly) chunks.push(e.data)
    }

    recorder.start()

    // Stop recording when release triggers onPTTEnd
    pttButtonRef.value._pttRecorder = recorder
  } catch (err) {
    errorMessages.value.push(`Mic access denied: ${err.message}`)
  }
}

/**
 * Release handler — stop recording, send audio blob over WebSocket.
 */
function onPTTEnd() {
  if (!audioStore.isListening) return

  const recorder = pttButtonRef.value?._pttRecorder
  if (recorder && recorder.state !== 'inactive') {
    recorder.stop()
    recorder.onstop = () => {
      // Collect all chunks from the recording
      const blob = new Blob(recorder.stream.getTracks().length > 0 ? [] : [], { type: 'audio/webm' })
      // Use a fresh MediaRecorder to get the final blob
      const freshRecorder = new MediaRecorder(recorder.stream)
      const collectedChunks = []
      freshRecorder.ondataavailable = (e) => {
        if (!freshRecorder.readOnly) collectedChunks.push(e.data)
      }
      freshRecorder.start()
      recorder.stop()

      // Wait for the blob to be ready, then send it
      setTimeout(() => {
      const finalBlob = new Blob(collectedChunks, { type: 'audio/webm' })
      if (finalBlob.size > 0) {
        const reader = new FileReader()
        reader.onloadend = () => {
          // Send base64-encoded audio data to the backend
          ws.send(JSON.stringify({ type: 'audio', data: reader.result.split(',')[1] }))
        }
        reader.readAsDataURL(finalBlob)
      }
    }, 50)

      audioStore.stopListening()
    }
  }
}

/**
 * Cancel button handler — sends {type: "cancel"} to interrupt TTS.
 */
function onCancelClick() {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'cancel' }))
  }
}

/**
 * Scroll the message list to the bottom.
 */
function scrollToBottom() {
  const el = messageListRef.value
  if (!el) return
  nextTick(() => {
    el.scrollTop = el.scrollHeight
  })
}

onMounted(() => {
  initWebSocket()
})

onUnmounted(() => {
  if (ws) {
    ws.close()
  }
})
</script>

<style scoped>
.chat-area {
  display: flex;
  flex-direction: column;
  height: 100%;
}
</style>
