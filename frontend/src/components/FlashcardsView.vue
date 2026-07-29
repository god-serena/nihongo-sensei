<script setup lang="ts">
import { ref, computed } from 'vue';
import { RotateCw, CheckCircle2, Volume2, Plus, Sparkles, Trash2, ArrowLeft, ArrowRight } from 'lucide-vue-next';
import type { Flashcard, JLPTLevel } from '../types';
import { INITIAL_FLASHCARDS as initialFlashcards } from '../data/japaneseData';
import { speakJapanese } from '../services/api';

const props = defineProps<{
  currentJlpt: JLPTLevel;
  masteredIds: string[];
}>();

const emit = defineEmits<{
  (e: 'toggle-mastered', id: string): void;
}>();

const deck = ref<Flashcard[]>([...initialFlashcards]);
const currentIndex = ref(0);
const isFlipped = ref(false);
const filterCategory = ref<'all' | 'unmastered' | 'mastered'>('all');

// Custom card creation modal state
const showCreateModal = ref(false);
const newKanji = ref('');
const newHiragana = ref('');
const newRomaji = ref('');
const newEnglish = ref('');
const newJlpt = ref<JLPTLevel>('N5');

const filteredDeck = computed(() => {
  return deck.value.filter(card => {
    const isMastered = props.masteredIds.includes(card.id);
    if (filterCategory.value === 'mastered') return isMastered;
    if (filterCategory.value === 'unmastered') return !isMastered;
    return true;
  });
});

const currentCard = computed<Flashcard | undefined>(() => {
  if (filteredDeck.value.length === 0) return undefined;
  const safeIdx = Math.min(currentIndex.value, filteredDeck.value.length - 1);
  return filteredDeck.value[safeIdx];
});

const isCurrentMastered = computed(() => {
  if (!currentCard.value) return false;
  return props.masteredIds.includes(currentCard.value.id);
});

function handleNext() {
  isFlipped.value = false;
  if (filteredDeck.value.length > 0) {
    currentIndex.value = (currentIndex.value + 1) % filteredDeck.value.length;
  }
}

function handlePrev() {
  isFlipped.value = false;
  if (filteredDeck.value.length > 0) {
    currentIndex.value = (currentIndex.value - 1 + filteredDeck.value.length) % filteredDeck.value.length;
  }
}

function handleSpeak(text: string) {
  speakJapanese(text);
}

function toggleCurrentMastered() {
  if (currentCard.value) {
    emit('toggle-mastered', currentCard.value.id);
  }
}

function createCard() {
  if (!newHiragana.value.trim() || !newEnglish.value.trim()) return;

  const card: Flashcard = {
    id: `custom-${Date.now()}`,
    kanji: newKanji.value.trim() || newHiragana.value.trim(),
    hiragana: newHiragana.value.trim(),
    romaji: newRomaji.value.trim() || newHiragana.value.trim(),
    english: newEnglish.value.trim(),
    jlpt: newJlpt.value,
    type: 'vocab',
    examples: [
      {
        japanese: `${newKanji.value || newHiragana.value}の勉強が好きです。`,
        reading: `${newHiragana.value}のべんきょうがすきです。`,
        english: `I like studying ${newEnglish.value}.`
      }
    ]
  };

  deck.value.unshift(card);
  showCreateModal.value = false;
  newKanji.value = '';
  newHiragana.value = '';
  newRomaji.value = '';
  newEnglish.value = '';
  currentIndex.value = 0;
  isFlipped.value = false;
}

function deleteCustomCard(id: string) {
  deck.value = deck.value.filter(c => c.id !== id);
  if (currentIndex.value >= deck.value.length) {
    currentIndex.value = Math.max(0, deck.value.length - 1);
  }
}
</script>

<template>
  <div class="max-w-5xl mx-auto px-4 py-4 w-full space-y-6">
    
    <!-- Controls Bar -->
    <div class="flex flex-col sm:flex-row items-center justify-between gap-4 bg-zinc-900/90 border border-zinc-800 p-4 rounded-2xl shadow-md">
      <div>
        <h2 class="text-base font-bold text-white flex items-center gap-2">
          Japanese Flashcard Deck
          <span class="text-xs font-mono font-normal px-2 py-0.5 rounded bg-red-950 text-red-400 border border-red-800">
            {{ filteredDeck.length }} Cards
          </span>
        </h2>
        <p class="text-xs text-zinc-400">Click card to flip, test recall & mark cards as mastered.</p>
      </div>

      <div class="flex items-center gap-3 w-full sm:w-auto justify-end">
        <!-- Filter Tabs -->
        <div class="flex items-center bg-zinc-950 p-1 rounded-lg border border-zinc-800 text-xs font-medium">
          <button
            @click="filterCategory = 'all'; currentIndex = 0"
            :class="['px-2.5 py-1 rounded transition-colors', filterCategory === 'all' ? 'bg-zinc-800 text-white' : 'text-zinc-400']"
          >
            All
          </button>
          <button
            @click="filterCategory = 'unmastered'; currentIndex = 0"
            :class="['px-2.5 py-1 rounded transition-colors', filterCategory === 'unmastered' ? 'bg-zinc-800 text-white' : 'text-zinc-400']"
          >
            Learning
          </button>
          <button
            @click="filterCategory = 'mastered'; currentIndex = 0"
            :class="['px-2.5 py-1 rounded transition-colors', filterCategory === 'mastered' ? 'bg-zinc-800 text-white' : 'text-zinc-400']"
          >
            Mastered
          </button>
        </div>

        <!-- Add Custom Card Button -->
        <button
          @click="showCreateModal = true"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-600 hover:bg-red-500 text-white text-xs font-bold transition-all shadow-md shadow-red-600/30"
        >
          <Plus class="w-3.5 h-3.5" />
          Add Card
        </button>
      </div>
    </div>

    <!-- Flashcard Display Area -->
    <div v-if="filteredDeck.length === 0" class="text-center py-16 bg-zinc-900 border border-zinc-800 rounded-2xl">
      <Sparkles class="w-8 h-8 text-red-500 mx-auto mb-2 opacity-60" />
      <p class="text-zinc-300 font-semibold text-sm">No cards match this filter category.</p>
      <button
        @click="filterCategory = 'all'"
        class="mt-3 px-3 py-1.5 bg-zinc-800 text-xs font-bold text-zinc-200 rounded-lg border border-zinc-700 hover:text-white"
      >
        Reset Filters
      </button>
    </div>

    <div v-else-if="currentCard" class="space-y-4">
      
      <!-- Flip Card Canvas -->
      <div
        @click="isFlipped = !isFlipped"
        class="relative min-h-[340px] bg-zinc-900 border-2 border-zinc-800 hover:border-red-600/50 rounded-3xl p-6 sm:p-10 flex flex-col items-center justify-between cursor-pointer transition-all duration-300 shadow-2xl group select-none"
      >
        <!-- Top Card Badge Header -->
        <div class="w-full flex items-center justify-between text-xs text-zinc-400">
          <span class="font-mono bg-zinc-950 px-2.5 py-1 rounded-md border border-zinc-800 font-bold text-zinc-300">
            Card {{ currentIndex + 1 }} / {{ filteredDeck.length }}
          </span>

          <div class="flex items-center gap-2">
            <span class="font-bold text-red-400 bg-red-950/80 px-2.5 py-1 rounded-md border border-red-800/80">
              {{ currentCard.jlpt }}
            </span>
            <button
              @click.stop="handleSpeak(currentCard.hiragana || currentCard.kanji)"
              class="p-1.5 rounded-md bg-zinc-800 hover:bg-zinc-700 text-zinc-200 transition-colors"
              title="Listen pronunciation"
            >
              <Volume2 class="w-4 h-4 text-red-500" />
            </button>
          </div>
        </div>

        <!-- Card Center Front / Back Content -->
        <div class="text-center my-auto py-6 space-y-3">
          <!-- Front Side -->
          <div v-if="!isFlipped" class="space-y-2 animate-fadeIn">
            <div class="text-6xl sm:text-7xl font-bold font-jp text-white tracking-wider drop-shadow-md">
              {{ currentCard.kanji }}
            </div>
            <div class="text-lg font-medium text-red-400 font-jp">
              {{ currentCard.hiragana }}
            </div>
            <div class="text-xs font-mono text-zinc-500 uppercase tracking-widest pt-2">
              (Click anywhere to reveal English meaning)
            </div>
          </div>

          <!-- Back Side -->
          <div v-else class="space-y-4 animate-fadeIn">
            <div class="text-3xl font-extrabold text-white">
              {{ currentCard.english }}
            </div>
            <div class="text-sm text-zinc-400 font-mono">
              Romaji: {{ currentCard.romaji }}
            </div>

            <div v-if="currentCard.examples && currentCard.examples.length > 0" class="pt-4 border-t border-zinc-800 max-w-lg mx-auto text-left space-y-1 bg-zinc-950/80 p-3 rounded-lg border border-zinc-800">
              <span class="text-[10px] uppercase font-bold text-zinc-500 tracking-wider">Example Sentence:</span>
              <p class="text-sm font-jp font-semibold text-zinc-200">{{ currentCard.examples[0].japanese }}</p>
              <p class="text-xs font-jp text-red-400">{{ currentCard.examples[0].reading }}</p>
              <p class="text-xs text-zinc-400 italic">{{ currentCard.examples[0].english }}</p>
            </div>
          </div>
        </div>

        <!-- Bottom Action Bar -->
        <div class="w-full flex items-center justify-between pt-4 border-t border-zinc-800/80 text-xs">
          <button
            @click.stop="toggleCurrentMastered"
            :class="[
              'flex items-center gap-1.5 px-3 py-1.5 rounded-lg border font-bold transition-all',
              isCurrentMastered
                ? 'bg-red-600/20 border-red-500 text-red-400'
                : 'bg-zinc-800 border-zinc-700 text-zinc-400 hover:text-white'
            ]"
          >
            <CheckCircle2 :class="['w-4 h-4', isCurrentMastered ? 'text-red-500' : 'text-zinc-500']" />
            <span>{{ isCurrentMastered ? 'Mastered (習得済み)' : 'Mark as Mastered' }}</span>
          </button>

          <span class="text-zinc-500 flex items-center gap-1">
            <RotateCw class="w-3.5 h-3.5" />
            Flip Card
          </span>

          <button
            v-if="currentCard.id.startsWith('custom-')"
            @click.stop="deleteCustomCard(currentCard.id)"
            class="p-1.5 rounded text-zinc-500 hover:text-red-400 transition-colors"
            title="Delete custom card"
          >
            <Trash2 class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- Navigation Arrows -->
      <div class="flex items-center justify-between gap-4 px-2">
        <button
          @click="handlePrev"
          class="flex-1 py-3 px-4 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 rounded-lg font-bold text-xs text-zinc-200 flex items-center justify-center gap-2 transition-all"
        >
          <ArrowLeft class="w-4 h-4 text-red-500" />
          Previous Card
        </button>

        <button
          @click="handleNext"
          class="flex-1 py-3 px-4 bg-red-600 hover:bg-red-500 text-white shadow-md shadow-red-600/30 rounded-lg font-bold text-xs flex items-center justify-center gap-2 transition-all"
        >
          Next Card
          <ArrowRight class="w-4 h-4" />
        </button>
      </div>

    </div>

    <!-- Create Card Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-zinc-900 border border-zinc-800 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl">
        <div class="flex items-center justify-between border-b border-zinc-800 pb-3">
          <h3 class="text-base font-bold text-white flex items-center gap-2">
            <Plus class="w-4 h-4 text-red-500" />
            Create Custom Flashcard
          </h3>
          <button @click="showCreateModal = false" class="text-zinc-500 hover:text-zinc-300">✕</button>
        </div>

        <div class="space-y-3 text-xs">
          <div>
            <label class="block text-zinc-400 font-semibold mb-1">Kanji (漢字) - Optional:</label>
            <input
              v-model="newKanji"
              type="text"
              placeholder="e.g. 猫"
              class="w-full bg-zinc-950 border border-zinc-800 text-white rounded-lg p-2.5 focus:outline-none focus:ring-1 focus:ring-red-500"
            />
          </div>

          <div>
            <label class="block text-zinc-400 font-semibold mb-1">Hiragana Reading (ひらがな) - Required:</label>
            <input
              v-model="newHiragana"
              type="text"
              placeholder="e.g. ねこ"
              class="w-full bg-zinc-950 border border-zinc-800 text-white rounded-lg p-2.5 focus:outline-none focus:ring-1 focus:ring-red-500"
            />
          </div>

          <div>
            <label class="block text-zinc-400 font-semibold mb-1">Romaji:</label>
            <input
              v-model="newRomaji"
              type="text"
              placeholder="e.g. neko"
              class="w-full bg-zinc-950 border border-zinc-800 text-white rounded-lg p-2.5 focus:outline-none focus:ring-1 focus:ring-red-500"
            />
          </div>

          <div>
            <label class="block text-zinc-400 font-semibold mb-1">English Meaning - Required:</label>
            <input
              v-model="newEnglish"
              type="text"
              placeholder="e.g. Cat"
              class="w-full bg-zinc-950 border border-zinc-800 text-white rounded-lg p-2.5 focus:outline-none focus:ring-1 focus:ring-red-500"
            />
          </div>

          <div>
            <label class="block text-zinc-400 font-semibold mb-1">JLPT Level Tag:</label>
            <select
              v-model="newJlpt"
              class="w-full bg-zinc-950 border border-zinc-800 text-white rounded-lg p-2.5 focus:outline-none focus:ring-1 focus:ring-red-500"
            >
              <option value="N5">N5</option>
              <option value="N4">N4</option>
              <option value="N3">N3</option>
              <option value="N2">N2</option>
              <option value="N1">N1</option>
            </select>
          </div>
        </div>

        <div class="flex items-center justify-end gap-2 pt-2 border-t border-zinc-800">
          <button
            @click="showCreateModal = false"
            class="px-4 py-2 rounded-lg bg-zinc-800 text-zinc-300 font-semibold text-xs hover:bg-zinc-700"
          >
            Cancel
          </button>
          <button
            @click="createCard"
            :disabled="!newHiragana.trim() || !newEnglish.trim()"
            class="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-500 text-white font-bold text-xs shadow-md shadow-red-600/30 disabled:opacity-50"
          >
            Save Flashcard
          </button>
        </div>
      </div>
    </div>

  </div>
</template>
