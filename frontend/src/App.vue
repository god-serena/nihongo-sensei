<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import Header from './components/Header.vue';
import SenseiChat from './components/SenseiChat.vue';
import FlashcardsView from './components/FlashcardsView.vue';
import DictionaryView from './components/DictionaryView.vue';
import ListeningLab from './components/ListeningLab.vue';
import StatsProgress from './components/StatsProgress.vue';
import SettingsModal from './components/SettingsModal.vue';

import type { TabType, JLPTLevel, UserStats, ChatMessage } from './types';

// App state
const activeTab = ref<TabType>('chat');
const settingsModalOpen = ref<boolean>(false);
const currentJlpt = ref<JLPTLevel>('N5');
const isSessionLocked = ref<boolean>(false);
const hasApiServer = ref<boolean>(true);

// Mastered Flashcard IDs
const masteredFlashcardIds = ref<string[]>([]);

// Chat History
const chatMessages = ref<ChatMessage[]>([
  {
    id: 'welcome-1',
    role: 'assistant',
    content: 'Welcome to Koto Sensei Japanese Studio.\n\nHow can I support your Japanese learning today? You can practice conversation, ask grammar questions, or request vocabulary explanations!',
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    jlptLevel: 'N5'
  }
]);

// User Stats
const userStats = ref<UserStats>({
  cardsMastered: 0,
  cardsStudiedToday: 12,
  chatSessionsCount: 1,
  listeningCompleted: 1,
  minutesSpent: 45,
  level: 'N5',
  savedVocabIds: ['dict-1', 'dict-2']
});

// Load state from localStorage on mount
onMounted(() => {
  try {
    const savedMastered = localStorage.getItem('koto_mastered_flashcards');
    if (savedMastered) {
      masteredFlashcardIds.value = JSON.parse(savedMastered);
    }

    const savedStats = localStorage.getItem('koto_user_stats');
    if (savedStats) {
      userStats.value = JSON.parse(savedStats);
    }

    const savedJlpt = localStorage.getItem('koto_jlpt_level');
    if (savedJlpt) {
      currentJlpt.value = savedJlpt as JLPTLevel;
    }
  } catch (e) {
    console.error('Error loading state from localStorage:', e);
  }
});

// Watch and sync mastered flashcards count
watch(masteredFlashcardIds, (newVal) => {
  try {
    localStorage.setItem('koto_mastered_flashcards', JSON.stringify(newVal));
    userStats.value.cardsMastered = newVal.length;
    localStorage.setItem('koto_user_stats', JSON.stringify(userStats.value));
  } catch (e) {
    console.error('Error saving mastered flashcards:', e);
  }
}, { deep: true });

// Sync stats
watch(userStats, (newVal) => {
  try {
    localStorage.setItem('koto_user_stats', JSON.stringify(newVal));
  } catch (e) {
    console.error('Error saving stats:', e);
  }
}, { deep: true });

// Sync JLPT level
watch(currentJlpt, (newVal) => {
  try {
    localStorage.setItem('koto_jlpt_level', newVal);
    userStats.value.level = newVal;
  } catch (e) {
    console.error('Error saving JLPT level:', e);
  }
});

// Handlers
function toggleMastered(id: string) {
  if (masteredFlashcardIds.value.includes(id)) {
    masteredFlashcardIds.value = masteredFlashcardIds.value.filter(item => item !== id);
  } else {
    masteredFlashcardIds.value.push(id);
  }
}

function toggleSavedVocab(id: string) {
  if (userStats.value.savedVocabIds.includes(id)) {
    userStats.value.savedVocabIds = userStats.value.savedVocabIds.filter(item => item !== id);
  } else {
    userStats.value.savedVocabIds.push(id);
  }
}

function handleMessagesUpdate(newMsgs: ChatMessage[]) {
  chatMessages.value = newMsgs;
  if (newMsgs.length > chatMessages.value.length) {
    userStats.value.chatSessionsCount += 1;
  }
}

function handleListeningComplete() {
  userStats.value.listeningCompleted += 1;
}

function handleClearMessages() {
  chatMessages.value = [];
}

function handleResetStats() {
  masteredFlashcardIds.value = [];
  userStats.value = {
    cardsMastered: 0,
    cardsStudiedToday: 0,
    chatSessionsCount: 1,
    listeningCompleted: 0,
    minutesSpent: 10,
    level: currentJlpt.value,
    savedVocabIds: ['dict-1']
  };
}
</script>

<template>
  <div class="h-screen bg-zinc-950 text-zinc-100 flex flex-col font-sans selection:bg-red-600 selection:text-white overflow-hidden min-w-[900px] min-h-[600px] max-w-[1000px] mx-auto shadow-2xl border-x border-zinc-900">

    <!-- Header (with embedded tab navigation) -->
    <Header
      :currentJlpt="currentJlpt"
      :stats="userStats"
      :hasApiServer="hasApiServer"
      :activeTab="activeTab"
      :isLocked="activeTab === 'chat' && isSessionLocked"
      @update:jlpt="(lvl) => currentJlpt = lvl"
      @update:tab="(tab) => activeTab = tab"
      @open-settings="settingsModalOpen = true"
    />

    <!-- Main Workspace Container (scrollable) -->
    <main class="flex-1 overflow-y-auto">
      
      <!-- Chat Tab -->
      <SenseiChat
        v-if="activeTab === 'chat'"
        :messages="chatMessages"
        :currentJlpt="currentJlpt"
        :savedVocabIds="userStats.savedVocabIds"
        @update:messages="handleMessagesUpdate"
        @update:jlpt="(lvl) => currentJlpt = lvl"
        @update:isLocked="(locked) => isSessionLocked = locked"
        @save-vocab="toggleSavedVocab"
        @clear-messages="handleClearMessages"
      />

      <!-- Flashcards Tab -->
      <FlashcardsView
        v-else-if="activeTab === 'flashcards'"
        :currentJlpt="currentJlpt"
        :masteredIds="masteredFlashcardIds"
        @toggle-mastered="toggleMastered"
      />

      <!-- Dictionary Tab -->
      <DictionaryView
        v-else-if="activeTab === 'dictionary'"
      />

      <!-- Listening Lab Tab -->
      <ListeningLab
        v-else-if="activeTab === 'listening'"
        :currentJlpt="currentJlpt"
        @listening-complete="handleListeningComplete"
      />

      <!-- Stats & Progress Tab -->
      <StatsProgress
        v-else-if="activeTab === 'stats'"
        :stats="userStats"
        @reset-stats="handleResetStats"
      />

    </main>

    <!-- Settings Modal -->
    <SettingsModal
      :open="settingsModalOpen"
      @close="settingsModalOpen = false"
    />

    <!-- Footer Stamp -->
    <footer class="border-t border-zinc-900 bg-zinc-950 py-4 text-center text-xs text-zinc-500 font-sans">
      <div class="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
        <div class="flex items-center gap-2">
          <span class="w-2.5 h-2.5 rounded-full bg-red-600"></span>
          <span class="font-bold text-zinc-400">Koto Sensei Japanese Studio</span>
          <span class="text-zinc-600">• Vue 3 + Tailwind CSS + Gemini AI</span>
        </div>
        <p class="text-zinc-600">
          "継続は力なり" — Continuation is power.
        </p>
      </div>
    </footer>

  </div>
</template>
