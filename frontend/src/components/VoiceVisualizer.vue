<template>
  <canvas ref="canvasRef" class="w-full h-24 rounded-lg bg-gray-900"></canvas>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  active: { type: Boolean, default: false },
  barCount: { type: Number, default: 32 },
  color: { type: String, default: '#6366f1' }
})

const emit = defineEmits(['error'])

const canvasRef = ref(null)

let audioContext = null
let analyser = null
let stream = null
let animationId = null

function drawBars() {
  if (!analyser || !canvasRef.value) return

  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  // Set canvas dimensions to match display size for crisp rendering
  const rect = canvas.getBoundingClientRect()
  if (canvas.width !== rect.width || canvas.height !== rect.height) {
    canvas.width = rect.width
    canvas.height = rect.height
  }

  const bufferLength = analyser.frequencyBinCount
  const dataArray = new Uint8Array(bufferLength)
  analyser.getByteFrequencyData(dataArray)

  ctx.clearRect(0, 0, canvas.width, canvas.height)

  const barWidth = canvas.width / props.barCount
  let x = 0

  for (let i = 0; i < props.barCount; i++) {
    // Map each bar to a frequency bin
    const index = Math.floor(i * bufferLength / props.barCount)
    const value = dataArray[index] || 0

    // Scale bar height based on frequency data
    const barHeight = (value / 255) * canvas.height * 0.9

    ctx.fillStyle = props.color
    ctx.fillRect(x, canvas.height - barHeight, barWidth - 1, barHeight)

    x += barWidth
  }

  animationId = requestAnimationFrame(drawBars)
}

function startVisualization() {
  if (!canvasRef.value) return

  navigator.mediaDevices.getUserMedia({ audio: true })
    .then((mediaStream) => {
      if (!props.active) {
        mediaStream.getTracks().forEach((track) => track.stop())
        return
      }
      stream = mediaStream
      audioContext = new (window.AudioContext || window.webkitAudioContext)()
      const source = audioContext.createMediaStreamSource(stream)

      analyser = audioContext.createAnalyser()
      analyser.fftSize = 2048
      analyser.smoothingTimeConstant = 0.3

      source.connect(analyser)

      drawBars()
    })
    .catch((err) => {
      emit('error', { message: err.message || 'Microphone access denied' })
    })
}

function stopVisualization() {
  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = null
  }

  if (stream) {
    stream.getTracks().forEach((track) => track.stop())
    stream = null
  }

  if (audioContext) {
    audioContext.close()
    audioContext = null
  }

  analyser = null
}

onMounted(() => {
  if (props.active) {
    startVisualization()
  }
})

watch(() => props.active, (newVal) => {
  if (newVal) {
    startVisualization()
  } else {
    stopVisualization()
  }
})

onUnmounted(() => {
  stopVisualization()
})
</script>
