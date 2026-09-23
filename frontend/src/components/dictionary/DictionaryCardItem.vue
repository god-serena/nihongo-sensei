<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { Volume2, Sparkles, Layers, Loader2, ChevronDown, ChevronUp } from 'lucide-vue-next';
import type { DictionaryEntry } from '../../types';
import DictionaryAiAnalysis from './DictionaryAiAnalysis.vue';

const props = defineProps<{
  entry: DictionaryEntry;
  isAnalyzing?: boolean;
  analysis?: {
    romaji: string;
    jlpt_level: string;
    nuance: string;
    example?: { japanese: string; hiragana: string; english: string };
  };
}>();

const emit = defineEmits<{
  (e: 'speak', text: string): void;
  (e: 'askAi', entry: DictionaryEntry): void;
  (e: 'addFlashcard', entry: DictionaryEntry): void;
}>();

const isExpanded = ref(false);

const hasExcessContent = computed(() => {
  return props.entry.meanings.length > 3 || (props.entry.examples && props.entry.examples.length > 0) || !!props.analysis;
});

watch(
  () => props.analysis,
  (newVal) => {
    if (newVal) {
      isExpanded.value = true;
    }
  },
  { immediate: true }
);
</script>

<template>
  <div
    :class="[
      'bg-zinc-900/90 hover:bg-zinc-900 border border-zinc-800/80 hover:border-red-600/40 rounded-lg p-5 transition-all shadow-md flex flex-col justify-between space-y-4 group min-h-[167px]',
      !isExpanded && hasExcessContent ? 'max-h-[167px] overflow-hidden relative' : ''
    ]"
  >
    <!-- Clean Word Header with Icon-Only Action Buttons -->
    <div class="flex items-start justify-between gap-3">
      <div class="flex items-baseline gap-3">
        <span class="text-3xl font-bold font-jp text-white">
          {{ entry.kanji }}
        </span>
        <span class="text-sm font-semibold text-red-400 font-jp">
          {{ entry.reading }}
        </span>
      </div>

      <!-- Icon-Only Action Buttons (Speak, Ask AI, Make Flashcard, Expand/Collapse) -->
      <div class="flex items-center gap-1.5">
        <!-- Speak Button -->
        <button
          @click="emit('speak', entry.reading || entry.kanji)"
          class="p-2.5 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 hover:text-white transition-all cursor-pointer"
          title="Pronounce word"
        >
          <Volume2 class="w-4 h-4 text-red-500" />
        </button>

        <!-- Ask AI Button -->
        <button
          @click="emit('askAi', entry)"
          :disabled="isAnalyzing"
          class="p-2.5 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 hover:text-red-400 transition-all cursor-pointer border border-zinc-700/80 disabled:opacity-50"
          title="Ask AI Sensei for analysis & example reading"
        >
          <Loader2 v-if="isAnalyzing" class="w-4 h-4 text-red-400 animate-spin" />
          <Sparkles v-else class="w-4 h-4 text-red-400" />
        </button>

        <!-- Make Flashcard Button -->
        <button
          @click="emit('addFlashcard', entry)"
          class="p-2.5 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 hover:text-white transition-all cursor-pointer border border-zinc-700/80"
          title="Add word to Flashcards deck"
        >
          <Layers class="w-4 h-4 text-zinc-300" />
        </button>

        <!-- Expand / Collapse Button -->
        <button
          v-if="hasExcessContent"
          @click="isExpanded = !isExpanded"
          class="p-2.5 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 hover:text-white transition-all cursor-pointer border border-zinc-700/80"
          :title="isExpanded ? 'Collapse entry details' : 'Expand entry details'"
        >
          <ChevronUp v-if="isExpanded" class="w-4 h-4 text-red-500" />
          <ChevronDown v-else class="w-4 h-4 text-red-500" />
        </button>
      </div>
    </div>

    <!-- Content Container -->
    <div class="space-y-4">
      <!-- Part of Speech Badges & Meanings -->
      <div class="space-y-2">
        <div class="flex flex-wrap gap-1">
          <span
            v-for="(p, idx) in entry.pos"
            :key="idx"
            class="text-[10px] uppercase font-bold text-zinc-400 bg-zinc-950 px-2 py-0.5 rounded border border-zinc-800"
          >
            {{ p }}
          </span>
        </div>

        <div class="text-sm font-medium text-zinc-200">
          <ol class="list-decimal list-inside space-y-0.5">
            <li v-for="(m, idx) in entry.meanings" :key="idx">
              {{ m }}
            </li>
          </ol>
        </div>
      </div>

      <!-- Example Sentences -->
      <div v-if="entry.examples && entry.examples.length > 0" class="pt-3 border-t border-zinc-800/80 space-y-1 bg-zinc-950/60 p-2.5 rounded-lg border border-zinc-800/50">
        <p class="text-xs font-jp font-semibold text-zinc-300">
          {{ entry.examples[0].jp }}
        </p>
        <p class="text-[11px] font-jp text-red-400">
          {{ entry.examples[0].reading }}
        </p>
        <p class="text-[11px] text-zinc-400 italic">
          {{ entry.examples[0].en }}
        </p>
      </div>

      <!-- Inline AI Analysis Drawer/Badge (when fetched) -->
      <DictionaryAiAnalysis v-if="analysis" :analysis="analysis" />
    </div>
  </div>
</template>
