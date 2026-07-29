<script setup lang="ts">
import type { JLPTLevel, Session } from '../../types';

const props = defineProps<{
  activeSession: Session | null;
  currentJlpt: JLPTLevel;
  teachingMode: 'bilingual' | 'immersion';
  isLocked: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:teachingMode', mode: 'bilingual' | 'immersion'): void;
  (e: 'rename-session', title: string): void;
}>();
</script>

<template>
  <div class="shrink-0 flex flex-wrap items-center justify-between gap-2 px-3.5 py-2.5 bg-zinc-900/90 border border-zinc-800 rounded-xl shadow-md">
    <div class="flex items-center gap-2">
      <span class="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse"></span>
      <span v-if="activeSession" class="text-xs font-semibold text-zinc-200">
        <span class="hidden sm:inline">Session: </span>{{ activeSession.title || 'Untitled' }}
      </span>
      <span v-else class="text-xs font-semibold text-zinc-200">1-on-1 Practice Session</span>
      <span class="text-xs text-zinc-500 hidden sm:inline">• Target Level: <strong class="text-red-400">{{ currentJlpt }}</strong></span>
    </div>

    <!-- Teaching Mode Toggle Badge -->
    <div class="flex items-center gap-1 bg-zinc-950 p-1 rounded-lg border border-zinc-800">
      <button
        @click="!isLocked && emit('update:teachingMode', 'bilingual')"
        :disabled="isLocked"
        :class="[
          'px-2.5 py-1 text-xs font-semibold rounded-md transition-all flex items-center gap-1.5',
          isLocked ? 'cursor-not-allowed' : 'cursor-pointer',
          teachingMode === 'bilingual'
            ? (isLocked ? 'bg-red-950/60 text-red-300 shadow-sm border border-red-900/40' : 'bg-red-600 text-white shadow-sm font-bold')
            : (isLocked ? 'text-zinc-600 hover:text-zinc-500 hover:bg-zinc-900' : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800')
        ]"
        :title="isLocked ? 'Teaching mode is locked for this session' : 'Bilingual mode: English explanations + Japanese phrase demonstrations'"
      >
        <span>{{ isLocked ? '🔒' : '🌐' }}</span>
        <span>{{ isLocked ? 'Bilingual Teacher' : 'Bilingual Teacher' }}</span>
      </button>
      <button
        @click="!isLocked && emit('update:teachingMode', 'immersion')"
        :disabled="isLocked"
        :class="[
          'px-2.5 py-1 text-xs font-semibold rounded-md transition-all flex items-center gap-1.5',
          isLocked ? 'cursor-not-allowed' : 'cursor-pointer',
          teachingMode === 'immersion'
            ? (isLocked ? 'bg-red-950/60 text-red-300 shadow-sm border border-red-900/40' : 'bg-red-600 text-white shadow-sm font-bold')
            : (isLocked ? 'text-zinc-600 hover:text-zinc-500 hover:bg-zinc-900' : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800')
        ]"
        :title="isLocked ? 'Teaching mode is locked for this session' : 'Full Immersion mode: 100% Japanese responses (日本語オンリー)'"
      >
        <span>{{ isLocked ? '🔒' : '🇯🇵' }}</span>
        <span>{{ isLocked ? 'Full Immersion' : 'Full Immersion (日本語)' }}</span>
      </button>
    </div>
  </div>
</template>
