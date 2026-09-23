<script setup lang="ts">
import { Sparkles } from 'lucide-vue-next';

defineProps<{
  analysis: {
    romaji: string;
    jlpt_level: string;
    nuance: string;
    example?: {
      japanese: string;
      hiragana: string;
      english: string;
    };
  };
}>();
</script>

<template>
  <div
    class="p-3.5 rounded-xl bg-gradient-to-br from-red-950/40 via-zinc-950 to-zinc-900 border border-red-500/30 text-xs space-y-2 shadow-inner"
  >
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <Sparkles class="w-4 h-4 text-red-400 animate-pulse" />
        <span class="font-bold text-red-400 uppercase tracking-wider text-[10px]">AI Sensei Analysis</span>
      </div>
      <div class="flex items-center gap-2">
        <span v-if="analysis.romaji" class="font-mono text-zinc-300 text-[11px] bg-zinc-900 px-2 py-0.5 rounded border border-zinc-800">
          {{ analysis.romaji }}
        </span>
        <span v-if="analysis.jlpt_level" class="font-bold text-red-400 bg-red-950 px-2 py-0.5 rounded border border-red-800 text-[10px]">
          {{ analysis.jlpt_level }}
        </span>
      </div>
    </div>
    <p class="text-zinc-300 leading-relaxed font-sans text-xs pt-1 border-t border-zinc-800/50">
      {{ analysis.nuance }}
    </p>

    <!-- AI Example Sentence -->
    <div
      v-if="analysis.example && analysis.example.japanese"
      class="mt-2 pt-2 border-t border-zinc-800/80 space-y-1 bg-zinc-950/70 p-2.5 rounded-lg border border-red-900/30"
    >
      <p class="text-xs font-jp font-semibold text-zinc-200">
        {{ analysis.example.japanese }}
      </p>
      <p v-if="analysis.example.hiragana" class="text-[11px] font-jp text-red-400">
        {{ analysis.example.hiragana }}
      </p>
      <p v-if="analysis.example.english" class="text-[11px] text-zinc-400 italic">
        {{ analysis.example.english }}
      </p>
    </div>
  </div>
</template>
