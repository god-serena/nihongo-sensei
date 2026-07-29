<script setup lang="ts">
import { ref } from 'vue';
import { User, Copy, Check, Sparkles } from 'lucide-vue-next';
import type { ChatMessage, SentenceAnalysis } from '../../types';

const props = defineProps<{
  msg: ChatMessage;
  streamingMessageId: string | null;
  analysis?: SentenceAnalysis | null;
  isAnalyzing?: boolean;
}>();

const emit = defineEmits<{
  (e: 'analyze', msg: ChatMessage): void;
  (e: 'copy', text: string): void;
  (e: 'save-vocab', word: string): void;
}>();

const copied = ref(false);

function isSensei(msg: ChatMessage): boolean {
  return msg.role === 'assistant';
}

function formatSenseiContent(content: string): string {
  if (!content) return '';
  let html = content.replace(/([一-龯ヶ]+)\[([ぁ-んァ-ヶ]+)\]/g, '<ruby class="font-jp font-bold text-zinc-100">$1<rt class="text-[10px] text-red-400 font-mono font-normal">$2</rt></ruby>');
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-white bg-zinc-800/60 px-1 py-0.5 rounded">$1</strong>');
  html = html.replace(/^### (.*$)/gim, '<h3 class="text-xs font-bold uppercase tracking-wider text-red-400 mt-3 mb-1">$1</h3>');
  html = html.replace(/^- (.*$)/gim, '<li class="ml-4 list-disc text-zinc-300">$1</li>');
  html = html.replace(/((?:<li[^>]*>[\s\S]*?<\/li>\s*<br\/?>?\s*)+)/g, '<ul class="space-y-0.5">$1</ul>');
  return html.replace(/\n/g, '<br/>');
}

async function handleCopy() {
  try {
    await navigator.clipboard.writeText(props.msg.content);
    copied.value = true;
    emit('copy', props.msg.content);
    setTimeout(() => {
      copied.value = false;
    }, 2000);
  } catch (err) {
    console.error('Failed to copy text:', err);
  }
}
</script>

<template>
  <div
    :class="[
      'flex gap-3 max-w-3xl group',
      isSensei(msg) ? 'mr-auto' : 'ml-auto flex-row-reverse'
    ]"
  >
    <!-- Avatar -->
    <div
      :class="[
        'w-8 h-8 rounded-xl flex items-center justify-center shrink-0 font-bold text-xs shadow-sm',
        isSensei(msg)
          ? 'bg-red-600 text-white ring-1 ring-red-400'
          : 'bg-white text-black ring-1 ring-zinc-300 font-sans'
      ]"
    >
      <span v-if="isSensei(msg)">琴</span>
      <User v-else class="w-4 h-4" />
    </div>

    <!-- Message Card -->
    <div
      :class="[
        'rounded-xl p-4 text-sm leading-relaxed border transition-all relative',
        isSensei(msg)
          ? 'bg-zinc-900/90 text-zinc-100 border-zinc-800 shadow-md'
          : 'bg-white text-zinc-950 border-zinc-200 shadow-md font-medium'
      ]"
    >
      <!-- Header info -->
      <div class="flex items-center justify-between gap-4 mb-2 pb-1 border-b border-zinc-800/40 text-[11px]">
        <span :class="['font-bold tracking-tight', isSensei(msg) ? 'text-red-400' : 'text-zinc-600']">
          {{ isSensei(msg) ? 'Koto Sensei (琴先生)' : 'You (Learner)' }}
        </span>
        <div class="flex items-center gap-2">
          <span class="text-zinc-500">
            {{ msg.timestamp }}
          </span>

          <!-- Copy Button -->
          <button
            @click="handleCopy"
            class="opacity-0 group-hover:opacity-100 transition-opacity text-zinc-400 hover:text-white p-1 rounded hover:bg-zinc-800 cursor-pointer"
            :title="copied ? 'Copied!' : 'Copy message'"
          >
            <Check v-if="copied" class="w-3.5 h-3.5 text-green-400" />
            <Copy v-else class="w-3.5 h-3.5" />
          </button>

          <!-- Grammar Analysis Trigger -->
          <button
            v-if="isSensei(msg)"
            @click="emit('analyze', msg)"
            class="opacity-0 group-hover:opacity-100 transition-opacity text-red-400 hover:text-red-300 p-1 rounded hover:bg-red-950/40 cursor-pointer flex items-center gap-1 text-[10px]"
            title="Grammar Breakdown"
          >
            <Sparkles class="w-3.5 h-3.5 text-red-400" />
          </button>
        </div>
      </div>

      <!-- Content body -->
      <div
        v-if="isSensei(msg)"
        class="space-y-2 font-sans prose prose-invert max-w-none"
      >
        <div
          v-html="formatSenseiContent(msg.content)"
          class="whitespace-pre-wrap"
        ></div>
        <!-- Streaming cursor indicator -->
        <span
          v-if="msg.id === streamingMessageId"
          class="inline-block w-1.5 h-5 bg-red-500 rounded animate-pulse ml-1 align-middle"
        ></span>
      </div>
      <div
        v-else
        class="whitespace-pre-wrap space-y-2 font-sans"
      >
        <p v-for="(paragraph, idx) in msg.content.split('\n\n')" :key="idx" class="leading-relaxed">
          {{ paragraph }}
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
ruby {
  line-break: normal;
  word-spacing: normal;
}

rt {
  color: #f87171;
  font-size: 10px;
}
</style>
