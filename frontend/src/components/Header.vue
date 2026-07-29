<script setup lang="ts">
import { Settings, Compass, MessageSquareText, Layers, BookOpen, Sparkles, Headphones, BarChart3, Upload, FileText } from 'lucide-vue-next';
import type { JLPTLevel, TabType } from '../types';

defineProps<{
  currentJlpt: JLPTLevel;
  hasApiServer?: boolean;
  activeTab: TabType;
}>();

const emit = defineEmits<{
  (e: 'update:jlpt', level: JLPTLevel): void;
  (e: 'update:tab', tab: TabType): void;
  (e: 'open-settings'): void;
}>();

const jlptLevels: JLPTLevel[] = ['N5', 'N4', 'N3', 'N2', 'N1'];

function onSelectJlpt(lvl: JLPTLevel) {
  emit('update:jlpt', lvl);
}

const tabNavs: { id: TabType; label: string; jp: string; icon: any }[] = [
  { id: 'chat', label: 'AI Sensei Chat', jp: '会話', icon: MessageSquareText },
  { id: 'flashcards', label: 'Flashcard Deck', jp: '単語帳', icon: Layers },
  { id: 'dictionary', label: 'Dictionary', jp: '辞書', icon: BookOpen },
  // { id: 'analyzer', label: 'Grammar Analyzer', jp: '解析', icon: Sparkles },
  // { id: 'listening', label: 'Listening Lab', jp: '聴解', icon: Headphones },
  { id: 'documents', label: 'Study Materials', jp: '教材', icon: Upload },
  // { id: 'summaries', label: 'Lesson Insights', jp: '分析', icon: FileText },
  { id: 'stats', label: 'Study Progress', jp: '記録', icon: BarChart3 }
];
</script>

<template>
  <header class="sticky top-0 z-50 bg-zinc-950 border-b border-zinc-800">
    <!-- Top Row: Brand + Controls -->
    <div class="px-4 py-3">
      <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
        
        <!-- Left: Brand & Hanko Seal -->
        <div class="flex items-center gap-3 w-full sm:w-auto justify-between sm:justify-start">
          <div class="flex items-center gap-2.5">
            <!-- Red Japanese Seal (Hanko / Stamp) -->
            <div class="relative flex items-center justify-center w-9 h-9 rounded bg-red-600 text-white font-mincho font-black text-xl shadow-lg shadow-red-600/30 ring-1 ring-red-400 select-none">
              琴
              <div class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-red-800 rounded-full border border-black"></div>
            </div>

            <div>
              <div class="flex items-center gap-2">
                <h1 class="text-lg font-bold tracking-tight text-white font-sans flex items-center gap-1.5">
                  Koto Sensei
                  <span class="hidden sm:inline text-xs font-mono font-medium px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-300 border border-zinc-700">
                    琴先生 (Vue 3)
                  </span>
                </h1>
                <span v-if="hasApiServer !== false" class="hidden md:inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-red-950/80 text-red-400 border border-red-800/60">
                  <span class="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></span>
                  Live Engine
                </span>
              </div>
              <p class="text-xs text-zinc-400 font-sans sm:hidden">
                Interactive Japanese Language & Calligraphy Studio
              </p>
            </div>
          </div>

          <!-- Mobile JLPT selector -->
          <div class="flex sm:hidden items-center gap-1">
            <span class="text-xs text-zinc-400 mr-1">JLPT:</span>
            <select
              :value="currentJlpt"
              @change="(e) => onSelectJlpt((e.target as HTMLSelectElement).value as JLPTLevel)"
              class="bg-zinc-900 border border-zinc-700 text-red-400 text-xs font-bold rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-red-500"
            >
              <option v-for="lvl in jlptLevels" :key="lvl" :value="lvl">{{ lvl }}</option>
            </select>
          </div>
        </div>

        <!-- Right: Controls -->
        <div class="flex items-center gap-3 w-full sm:w-auto justify-end">
          
          <!-- JLPT Level Pills (Desktop) -->
          <div class="hidden sm:flex items-center gap-1 bg-zinc-900/90 p-1 rounded-lg border border-zinc-800">
            <span class="text-xs font-semibold text-zinc-400 px-2 flex items-center gap-1">
              <Compass class="w-3.5 h-3.5 text-red-500" />
              Level:
            </span>
            <button
              v-for="lvl in jlptLevels"
              :key="lvl"
              @click="onSelectJlpt(lvl)"
              :class="[
                'px-2.5 py-1 text-xs font-bold rounded transition-all',
                currentJlpt === lvl
                  ? 'bg-red-600 text-white shadow-md shadow-red-600/20 ring-1 ring-red-400'
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-800'
              ]"
            >
              {{ lvl }}
            </button>
          </div>

          <!-- Settings Button -->
          <button
            @click="() => emit('open-settings')"
            title="Settings"
            class="p-2 rounded-lg border border-zinc-800 text-zinc-400 hover:text-white hover:bg-zinc-800 transition-all"
          >
            <Settings class="w-4 h-4" />
          </button>
        </div>

      </div>
    </div>

    <!-- Bottom Row: Tab Navigation -->
    <nav class="border-t border-zinc-800/50 px-4">
      <div class="max-w-7xl mx-auto flex items-center justify-start sm:justify-center gap-1.5 overflow-x-auto no-scrollbar scroll-smooth">
        <button
          v-for="tab in tabNavs"
          :key="tab.id"
          @click="emit('update:tab', tab.id)"
          :class="[
            'relative flex items-center gap-2 px-4 py-2.5 font-semibold text-xs tracking-wide rounded-t-lg transition-all whitespace-nowrap border-t border-x',
            activeTab === tab.id
              ? 'bg-zinc-900 text-white border-zinc-700 border-b-zinc-900 shadow-sm'
              : 'text-zinc-400 border-transparent hover:text-zinc-200 hover:bg-zinc-900/50'
          ]"
        >
          <component
            :is="tab.icon"
            :class="activeTab === tab.id ? 'text-red-500' : 'text-zinc-500'"
            class="w-4 h-4"
          />
          <span>{{ tab.label }}</span>
          <span
            :class="[
              'text-[10px] font-jp font-normal px-1.5 py-0.2 rounded',
              activeTab === tab.id
                ? 'bg-red-950 text-red-300 border border-red-800/60'
                : 'bg-zinc-900 text-zinc-500'
            ]"
          >
            {{ tab.jp }}
          </span>

          <!-- Active Tab Red Indicator Bar -->
          <span
            v-if="activeTab === tab.id"
            class="absolute bottom-0 left-0 right-0 h-0.5 bg-red-600 rounded-t-full shadow-md shadow-red-600"
          ></span>
        </button>
      </div>
    </nav>
  </header>
</template>
