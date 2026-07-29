<script setup lang="ts">
import { BarChart3, Flame, Trophy, Layers, Headphones, MessageSquare, BookMarked, Award, RefreshCcw } from 'lucide-vue-next';
import type { UserStats } from '../types';

defineProps<{
  stats: UserStats;
}>();

const emit = defineEmits<{
  (e: 'reset-stats'): void;
}>();
</script>

<template>
  <div class="max-w-5xl mx-auto px-4 py-4 w-full space-y-6">
    
    <!-- Hero Banner -->
    <div class="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 shadow-xl relative overflow-hidden">
      <!-- Background Japanese Graphic -->
      <div class="absolute right-4 -bottom-6 text-9xl font-mincho font-bold text-zinc-800/20 select-none pointer-events-none">
        学習
      </div>

      <div class="relative z-10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div class="space-y-1">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-red-600 animate-pulse"></span>
            <span class="text-xs font-bold text-red-500 uppercase tracking-widest">Target Proficiency</span>
          </div>
          <h2 class="text-2xl font-bold text-white flex items-center gap-3">
            JLPT {{ stats.level }} Studio Mastery
            <span class="text-xs bg-red-600 text-white font-mono px-2.5 py-0.5 rounded-full shadow-md">
              Level {{ stats.level }}
            </span>
          </h2>
          <p class="text-xs text-zinc-400 max-w-md">
            Track your flashcard review progress, chat sessions with Koto Sensei, listening practice, and study streaks.
          </p>
        </div>

        <button
          @click="emit('reset-stats')"
          class="px-3 py-1.5 rounded-lg bg-zinc-950 hover:bg-zinc-800 text-zinc-400 hover:text-red-400 border border-zinc-800 text-xs font-semibold flex items-center gap-1.5 transition-colors"
        >
          <RefreshCcw class="w-3.5 h-3.5" />
          Reset Progress
        </button>
      </div>
    </div>

    <!-- Stat Metrics Grid -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
      
      <!-- Metric 1: Streak -->
      <div class="bg-zinc-900 border border-zinc-800 rounded-2xl p-4 flex flex-col justify-between space-y-2 shadow-md">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-zinc-400">Daily Streak</span>
          <Flame class="w-4 h-4 text-red-500" />
        </div>
        <div class="text-3xl font-extrabold text-white font-mono">
          {{ stats.streakDays }} <span class="text-xs font-sans text-zinc-500 font-normal">Days</span>
        </div>
        <p class="text-[11px] text-red-400 font-semibold">Keep logging in daily!</p>
      </div>

      <!-- Metric 2: Flashcards Mastered -->
      <div class="bg-zinc-900 border border-zinc-800 rounded-2xl p-4 flex flex-col justify-between space-y-2 shadow-md">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-zinc-400">Cards Mastered</span>
          <Layers class="w-4 h-4 text-red-500" />
        </div>
        <div class="text-3xl font-extrabold text-white font-mono">
          {{ stats.cardsMastered }} <span class="text-xs font-sans text-zinc-500 font-normal">Cards</span>
        </div>
        <p class="text-[11px] text-zinc-400">In flashcard deck</p>
      </div>

      <!-- Metric 3: Chat Sessions -->
      <div class="bg-zinc-900 border border-zinc-800 rounded-2xl p-4 flex flex-col justify-between space-y-2 shadow-md">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-zinc-400">Sensei Dialogues</span>
          <MessageSquare class="w-4 h-4 text-red-500" />
        </div>
        <div class="text-3xl font-extrabold text-white font-mono">
          {{ stats.chatSessionsCount }} <span class="text-xs font-sans text-zinc-500 font-normal">Chats</span>
        </div>
        <p class="text-[11px] text-zinc-400">AI practice sessions</p>
      </div>

      <!-- Metric 4: Saved Vocab -->
      <div class="bg-zinc-900 border border-zinc-800 rounded-2xl p-4 flex flex-col justify-between space-y-2 shadow-md">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-zinc-400">Saved Words</span>
          <BookMarked class="w-4 h-4 text-red-500" />
        </div>
        <div class="text-3xl font-extrabold text-white font-mono">
          {{ stats.savedVocabIds.length }} <span class="text-xs font-sans text-zinc-500 font-normal">Words</span>
        </div>
        <p class="text-[11px] text-zinc-400">Bookmarked in dictionary</p>
      </div>

    </div>

    <!-- Mastery Breakdown & Achievements -->
    <div class="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 shadow-xl space-y-4">
      <h3 class="text-sm font-bold text-white flex items-center gap-2">
        <Award class="w-4 h-4 text-red-500" />
        JLPT Roadmap Badges
      </h3>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div class="bg-zinc-950 p-4 rounded-xl border border-zinc-800 space-y-1">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-white">Hiragana & Katakana</span>
            <span class="text-[10px] font-bold text-emerald-400 bg-emerald-950 px-1.5 py-0.2 rounded border border-emerald-800">100%</span>
          </div>
          <p class="text-[11px] text-zinc-400">Kana syllabary mastered.</p>
        </div>

        <div class="bg-zinc-950 p-4 rounded-xl border border-zinc-800 space-y-1">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-white">N5 Basic Vocabulary</span>
            <span class="text-[10px] font-bold text-red-400 bg-red-950 px-1.5 py-0.2 rounded border border-red-800">Active</span>
          </div>
          <p class="text-[11px] text-zinc-400">Core 800 words & particles.</p>
        </div>

        <div class="bg-zinc-950 p-4 rounded-xl border border-zinc-800 space-y-1">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-white">Listening Practice</span>
            <span class="text-[10px] font-bold text-zinc-400 bg-zinc-900 px-1.5 py-0.2 rounded border border-zinc-800">{{ stats.listeningCompleted }} Scenarios</span>
          </div>
          <p class="text-[11px] text-zinc-400">Audio comprehension lab.</p>
        </div>
      </div>
    </div>

  </div>
</template>
