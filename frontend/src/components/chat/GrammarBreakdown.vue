<script setup lang="ts">
import { X, BookmarkPlus, BookOpen } from 'lucide-vue-next';
import type { SentenceAnalysis, TokenAnalysis } from '../../types';

const props = defineProps<{
  analysis: SentenceAnalysis;
}>();

const emit = defineEmits<{
  (e: 'save-vocab', word: string): void;
  (e: 'close'): void;
}>();

function getPosBadgeColor(pos: string): string {
  const lower = pos.toLowerCase();
  if (lower.includes('noun') || lower.includes('名詞')) {
    return 'bg-blue-950/80 text-blue-300 border-blue-800/60';
  }
  if (lower.includes('verb') || lower.includes('動詞')) {
    return 'bg-emerald-950/80 text-emerald-300 border-emerald-800/60';
  }
  if (lower.includes('particle') || lower.includes('助詞')) {
    return 'bg-purple-950/80 text-purple-300 border-purple-800/60';
  }
  if (lower.includes('adj') || lower.includes('形容詞')) {
    return 'bg-amber-950/80 text-amber-300 border-amber-800/60';
  }
  if (lower.includes('auxiliary') || lower.includes('助動詞')) {
    return 'bg-pink-950/80 text-pink-300 border-pink-800/60';
  }
  return 'bg-zinc-800 text-zinc-300 border-zinc-700';
}

function handleSaveVocab(token: TokenAnalysis) {
  const wordToSave = token.baseForm || token.surface;
  if (wordToSave) {
    emit('save-vocab', wordToSave);
  }
}
</script>

<template>
  <div class="bg-zinc-900 border border-zinc-800 rounded-xl p-4 shadow-xl space-y-4 my-2">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-zinc-800 pb-2">
      <div class="flex items-center gap-2">
        <BookOpen class="w-4 h-4 text-red-500" />
        <h3 class="text-sm font-bold text-white tracking-wide">Grammar & Token Breakdown</h3>
      </div>
      <button
        @click="emit('close')"
        class="p-1 rounded-md text-zinc-400 hover:text-white hover:bg-zinc-800 transition-all cursor-pointer"
        title="Close breakdown"
      >
        <X class="w-4 h-4" />
      </button>
    </div>

    <!-- Translation / Summary if available -->
    <div v-if="analysis.translation" class="text-xs text-zinc-300 bg-zinc-950/60 p-2.5 rounded-lg border border-zinc-800/60">
      <span class="text-zinc-500 font-semibold uppercase text-[10px] tracking-wider block mb-1">Translation</span>
      {{ analysis.translation }}
    </div>

    <!-- Tokens Grid -->
    <div v-if="analysis.tokens && analysis.tokens.length > 0" class="space-y-2">
      <span class="text-zinc-500 font-semibold uppercase text-[10px] tracking-wider block">Words & Parts of Speech</span>
      <div class="flex flex-wrap gap-2">
        <div
          v-for="(token, index) in analysis.tokens"
          :key="index"
          class="flex flex-col gap-1 p-2.5 rounded-lg bg-zinc-950 border border-zinc-800/80 hover:border-zinc-700 transition-all min-w-[100px]"
        >
          <!-- Surface & Reading -->
          <div class="flex flex-col">
            <span v-if="token.reading" class="text-[10px] text-red-400 font-mono">{{ token.reading }}</span>
            <span class="text-sm font-bold text-zinc-100 font-jp">{{ token.surface }}</span>
          </div>

          <!-- POS Badge -->
          <div class="flex items-center justify-between gap-1.5 mt-1">
            <span
              :class="[
                'text-[10px] px-1.5 py-0.5 rounded border font-medium uppercase tracking-wider',
                getPosBadgeColor(token.pos)
              ]"
            >
              {{ token.pos }}
            </span>

            <!-- Save Vocab Button -->
            <button
              @click="handleSaveVocab(token)"
              class="p-1 rounded text-zinc-500 hover:text-red-400 hover:bg-red-950/40 transition-all cursor-pointer"
              title="Save to Vocabulary"
            >
              <BookmarkPlus class="w-3.5 h-3.5" />
            </button>
          </div>

          <!-- English definition if provided -->
          <span v-if="token.english" class="text-[11px] text-zinc-400 mt-0.5 line-clamp-2">
            {{ token.english }}
          </span>
        </div>
      </div>
    </div>

    <!-- Grammar Notes -->
    <div v-if="analysis.grammarNotes && analysis.grammarNotes.length > 0" class="space-y-1.5 pt-2 border-t border-zinc-800/60">
      <span class="text-zinc-500 font-semibold uppercase text-[10px] tracking-wider block">Grammar Notes</span>
      <ul class="list-disc list-inside space-y-1 text-xs text-zinc-300">
        <li v-for="(note, idx) in analysis.grammarNotes" :key="idx">
          {{ note }}
        </li>
      </ul>
    </div>
  </div>
</template>
