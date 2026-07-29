<template>
  <div class="h-screen bg-zinc-950 text-zinc-100 flex flex-col font-sans selection:bg-red-600 selection:text-white overflow-hidden">

    <!-- Header (with embedded tab navigation) -->
    <Header
      :currentJlpt="currentJlpt"
      :stats="userStats"
      :hasApiServer="hasApiServer"
      :activeTab="activeTab"
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
        @update:messages="(msgs) => chatMessages = msgs"
        @save-vocab="toggleSavedVocab"
        @clear-messages="chatMessages = []"
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
        :savedVocabIds="userStats.savedVocabIds"
        @toggle-saved-vocab="toggleSavedVocab"
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

      <!-- RAG Study Materials Tab -->
      <div v-else-if="activeTab === 'documents'" class="max-w-5xl mx-auto p-4">
        <DocumentManager />
      </div>

      <!-- Lesson Summaries Insights Tab -->
      <div v-else-if="activeTab === 'summaries'" class="max-w-5xl mx-auto p-4">
        <SessionSummaries />
      </div>

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
          <span class="text-zinc-600">• Vue 3 + Tailwind CSS + FastAPI Engine</span>
        </div>
        <p class="text-zinc-600 font-serif">
          "継続は力なり" — Continuation is power.
        </p>
      </div>
    </footer>

  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import Header from '../components/Header.vue';
import SenseiChat from '../components/SenseiChat.vue';
import FlashcardsView from '../components/FlashcardsView.vue';
import DictionaryView from '../components/DictionaryView.vue';
import ListeningLab from '../components/ListeningLab.vue';
import StatsProgress from '../components/StatsProgress.vue';
import DocumentManager from '../components/DocumentManager.vue';
import SessionSummaries from '../components/SessionSummaries.vue';
import SettingsModal from '../components/SettingsModal.vue';

// App state
const activeTab = ref('chat');
const settingsModalOpen = ref(false);
const currentJlpt = ref('N5');
const hasApiServer = ref(true);

// Chat messages state
const chatMessages = ref([
  {
    id: 'welcome-1',
    role: 'assistant',
    content: 'Welcome to Koto Sensei Japanese Studio. How can I support your Japanese learning today?',
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    jlptLevel: 'N5'
  }
]);

// Mastered Flashcard IDs
const masteredFlashcardIds = ref([]);

// User Stats
const userStats = ref({
  streakDays: 3,
  cardsMastered: 0,
  cardsStudiedToday: 12,
  chatSessionsCount: 1,
  listeningCompleted: 1,
  minutesSpent: 45,
  level: 'N5',
  savedVocabIds: ['dict-1', 'dict-2']
});

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
      currentJlpt.value = savedJlpt;
    }
  } catch (e) {
    console.error('Error loading state from localStorage:', e);
  }
});

watch(masteredFlashcardIds, (newVal) => {
  try {
    localStorage.setItem('koto_mastered_flashcards', JSON.stringify(newVal));
    userStats.value.cardsMastered = newVal.length;
    localStorage.setItem('koto_user_stats', JSON.stringify(userStats.value));
  } catch (e) {
    console.error('Error saving mastered flashcards:', e);
  }
}, { deep: true });

watch(userStats, (newVal) => {
  try {
    localStorage.setItem('koto_user_stats', JSON.stringify(newVal));
  } catch (e) {
    console.error('Error saving stats:', e);
  }
}, { deep: true });

watch(currentJlpt, (newVal) => {
  try {
    localStorage.setItem('koto_jlpt_level', newVal);
    userStats.value.level = newVal;
  } catch (e) {
    console.error('Error saving JLPT level:', e);
  }
});

function toggleMastered(id) {
  if (masteredFlashcardIds.value.includes(id)) {
    masteredFlashcardIds.value = masteredFlashcardIds.value.filter(item => item !== id);
  } else {
    masteredFlashcardIds.value.push(id);
  }
}

function toggleSavedVocab(id) {
  if (userStats.value.savedVocabIds.includes(id)) {
    userStats.value.savedVocabIds = userStats.value.savedVocabIds.filter(item => item !== id);
  } else {
    userStats.value.savedVocabIds.push(id);
  }
}

function handleListeningComplete() {
  userStats.value.listeningCompleted += 1;
}

function handleResetStats() {
  masteredFlashcardIds.value = [];
  userStats.value = {
    streakDays: 1,
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
