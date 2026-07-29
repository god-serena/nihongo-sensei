<script setup lang="ts">
import { MessageSquareText, Layers, BookOpen, Headphones, BarChart3 } from 'lucide-vue-next';
import type { TabType } from '../types';

defineProps<{
  activeTab: TabType;
}>();

const emit = defineEmits<{
  (e: 'update:tab', tab: TabType): void;
}>();

const tabs: { id: TabType; label: string; jp: string; icon: any }[] = [
  { id: 'chat', label: 'AI Sensei Chat', jp: '会話', icon: MessageSquareText },
  { id: 'flashcards', label: 'Flashcard Deck', jp: '単語帳', icon: Layers },
  { id: 'dictionary', label: 'Dictionary', jp: '辞書', icon: BookOpen },
  { id: 'listening', label: 'Listening Lab', jp: '聴解', icon: Headphones },
  { id: 'stats', label: 'Study Progress', jp: '記録', icon: BarChart3 }
];
</script>

<template>
  <nav class="sticky bg-zinc-950 border-b border-zinc-800 px-4 pt-2 z-40">
    <div class="max-w-7xl mx-auto flex items-center justify-start sm:justify-center gap-1.5 overflow-x-auto no-scrollbar scroll-smooth pb-0">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="emit('update:tab', tab.id)"
        :class="[
          'relative flex items-center gap-2 px-4 py-3 font-semibold text-xs tracking-wide rounded-t-lg transition-all whitespace-nowrap border-t border-x',
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
</template>
