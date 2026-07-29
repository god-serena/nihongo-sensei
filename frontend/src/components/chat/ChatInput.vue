<script setup lang="ts">
import { ref, onBeforeUnmount } from 'vue';
import { Send, Mic, MicOff } from 'lucide-vue-next';
import { transcribeAudio } from '../../services/api';

const props = defineProps<{
  loading: boolean;
}>();

const emit = defineEmits<{
  (e: 'send', text: string): void;
}>();

const input = ref('');
const isListening = ref(false);
const sttLoading = ref(false);

let mediaRecorder: MediaRecorder | null = null;
let audioChunks: Blob[] = [];

function handleSend() {
  const text = input.value.trim();
  if (!text || props.loading || sttLoading.value) return;
  emit('send', text);
  input.value = '';
}

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioChunks = [];
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data);
      }
    };

    mediaRecorder.onstop = async () => {
      const mimeType = mediaRecorder?.mimeType || 'audio/webm';
      const audioBlob = new Blob(audioChunks, { type: mimeType });
      stream.getTracks().forEach((track) => track.stop());

      const reader = new FileReader();
      reader.readAsDataURL(audioBlob);
      reader.onloadend = async () => {
        const base64Data = (reader.result as string)?.split(',')[1];
        if (base64Data) {
          sttLoading.value = true;
          try {
            const transcript = await transcribeAudio(base64Data);
            sttLoading.value = false;
            if (transcript && transcript.trim()) {
              emit('send', transcript.trim());
              input.value = '';
            }
          } catch (e) {
            console.error('STT Transcription error:', e);
          } finally {
            sttLoading.value = false;
          }
        }
      };
    };

    mediaRecorder.start();
    isListening.value = true;
  } catch (err) {
    console.error('Microphone access error:', err);
    alert('Unable to access microphone.');
    isListening.value = false;
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
  }
  isListening.value = false;
}

function toggleMic() {
  if (isListening.value) {
    stopRecording();
  } else {
    startRecording();
  }
}

onBeforeUnmount(() => {
  stopRecording();
});
</script>

<template>
  <div class="shrink-0">
    <!-- Input bar -->
    <div class="h-[56px] flex items-center gap-2 bg-zinc-900 border border-zinc-800 rounded-xl p-2.5 focus-within:ring-2 focus-within:ring-red-600 focus-within:border-transparent transition-all shadow-lg">
      <input
        type="text"
        v-model="input"
        @keydown.enter.exact.prevent="handleSend"
        placeholder="Ask Sensei a question or type in Japanese (e.g. 「ありがとう」の意味は？)..."
        :disabled="loading || sttLoading"
        class="flex-1 bg-transparent text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none pr-2 font-sans"
      />
      <button
        @click="toggleMic"
        :disabled="loading || sttLoading"
        :class="[
          'h-10 px-3 rounded-xl flex items-center justify-center shrink-0 transition-all font-semibold text-xs border cursor-pointer',
          isListening
            ? 'bg-red-600 text-white animate-pulse shadow-md shadow-red-600/30 border-red-400'
            : 'bg-zinc-800 text-zinc-400 hover:text-white hover:bg-zinc-700 border-zinc-700'
        ]"
        :title="isListening ? 'Stop listening' : 'Start listening'"
      >
        <Mic v-if="!isListening" class="w-4 h-4" />
        <MicOff v-else class="w-4 h-4 text-white" />
        <span v-if="isListening">Listening...</span>
      </button>
      <button
        @click="handleSend"
        :disabled="!input.trim() || loading || sttLoading"
        :class="[
          'w-10 h-10 rounded-xl flex items-center justify-center shrink-0 transition-all font-medium text-sm cursor-pointer',
          input.trim() && !loading && !sttLoading
            ? 'bg-red-600 hover:bg-red-500 text-white shadow-md shadow-red-600/30 ring-1 ring-red-400'
            : 'bg-zinc-800 text-zinc-500 cursor-not-allowed border border-zinc-700'
        ]"
      >
        <Send class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>
