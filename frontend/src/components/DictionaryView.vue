<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue';
import { Sparkles, Loader2 } from 'lucide-vue-next';
import type { DictionaryEntry } from '../types';
import { INITIAL_DICTIONARY } from '../data/japaneseData';
import { speakJapanese, searchDictionary, analyzeDictionaryEntry } from '../services/api';
import DictionaryToast from './dictionary/DictionaryToast.vue';
import DictionarySearchHeader from './dictionary/DictionarySearchHeader.vue';
import DictionaryCardItem from './dictionary/DictionaryCardItem.vue';

const query = ref('');
const entries = ref<DictionaryEntry[]>([]);
const isLoading = ref<boolean>(false);
const isLoadingMore = ref<boolean>(false);
const offset = ref<number>(0);
const hasMore = ref<boolean>(true);

const sentinelRef = ref<HTMLElement | null>(null);
let observer: IntersectionObserver | null = null;

const analysisLoading = ref<Record<string, boolean>>({});
const analysisData = ref<Record<string, { romaji: string; jlpt_level: string; nuance: string; example?: { japanese: string; hiragana: string; english: string } }>>({});

const toastMessage = ref<string>('');
let toastTimer: ReturnType<typeof setTimeout> | null = null;

function showToast(message: string) {
  toastMessage.value = message;
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toastMessage.value = '';
  }, 3000);
}

let debounceTimer: ReturnType<typeof setTimeout> | null = null;

async function performSearch() {
  isLoading.value = true;
  offset.value = 0;
  hasMore.value = true;
  try {
    const results = await searchDictionary(query.value, 0, 30);
    entries.value = results;
    if (results.length < 30) {
      hasMore.value = false;
    }
  } catch (err) {
    console.warn('Failed to search dictionary via API, using fallback filter:', err);
    entries.value = INITIAL_DICTIONARY.filter(entry => {
      const matchesQuery =
        !query.value ||
        entry.kanji.toLowerCase().includes(query.value.toLowerCase()) ||
        entry.reading.toLowerCase().includes(query.value.toLowerCase()) ||
        (entry.romaji ? entry.romaji.toLowerCase().includes(query.value.toLowerCase()) : false) ||
        entry.meanings.some(m => m.toLowerCase().includes(query.value.toLowerCase()));

      return matchesQuery;
    });
    hasMore.value = false;
  } finally {
    isLoading.value = false;
  }
}

async function fetchMoreEntries() {
  if (isLoadingMore.value || isLoading.value || !hasMore.value) return;
  isLoadingMore.value = true;
  const nextOffset = offset.value + 30;
  try {
    const nextResults = await searchDictionary(query.value, nextOffset, 30);
    if (nextResults.length > 0) {
      entries.value.push(...nextResults);
      offset.value = nextOffset;
    }
    if (nextResults.length < 30) {
      hasMore.value = false;
    }
  } catch (err) {
    console.warn('Failed to load more dictionary entries:', err);
    hasMore.value = false;
  } finally {
    isLoadingMore.value = false;
  }
}

function debouncedSearch() {
  if (debounceTimer) clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    performSearch();
  }, 300);
}

watch([query], () => {
  debouncedSearch();
});

function handleScroll(e: Event) {
  const target = e.target as HTMLElement;
  if (!target) return;
  if (target.scrollHeight - target.scrollTop - target.clientHeight < 300) {
    if (hasMore.value && !isLoadingMore.value && !isLoading.value) {
      fetchMoreEntries();
    }
  }
}

watch(sentinelRef, (el) => {
  if (el && observer) {
    observer.observe(el);
  }
});

onMounted(() => {
  performSearch();

  observer = new IntersectionObserver(
    (observerEntries) => {
      if (
        observerEntries[0].isIntersecting &&
        hasMore.value &&
        !isLoadingMore.value &&
        !isLoading.value
      ) {
        fetchMoreEntries();
      }
    },
    { rootMargin: '300px' }
  );

  const mainEl = document.querySelector('main');
  if (mainEl) {
    mainEl.addEventListener('scroll', handleScroll);
  }
});

onUnmounted(() => {
  if (observer) {
    observer.disconnect();
  }
  const mainEl = document.querySelector('main');
  if (mainEl) {
    mainEl.removeEventListener('scroll', handleScroll);
  }
});

function handleSpeak(text: string) {
  speakJapanese(text);
}

async function handleAskAI(entry: DictionaryEntry) {
  if (analysisLoading.value[entry.id]) return;
  analysisLoading.value[entry.id] = true;
  try {
    const res = await analyzeDictionaryEntry({
      kanji: entry.kanji,
      reading: entry.reading,
      meanings: entry.meanings,
    });
    analysisData.value[entry.id] = res;
  } catch (err: any) {
    analysisData.value[entry.id] = {
      romaji: entry.reading,
      jlpt_level: 'N3',
      nuance: `Analysis error: ${err?.message || 'Failed to connect to AI Sensei'}`,
    };
  } finally {
    analysisLoading.value[entry.id] = false;
  }
}

function handleAddFlashcard(entry: DictionaryEntry) {
  showToast(`Added '${entry.kanji || entry.reading}' to Flashcard Queue!`);
}
</script>

<template>
  <div class="max-w-5xl mx-auto px-4 py-4 w-full space-y-6 relative">
    <!-- Toast Notification -->
    <DictionaryToast :message="toastMessage" />

    <!-- Header & Search Box -->
    <DictionarySearchHeader
      v-model:query="query"
      :is-loading="isLoading"
    />

    <!-- Dictionary Cards Grid -->
    <div v-if="isLoading && entries.length === 0" class="text-center py-16 bg-zinc-900 border border-zinc-800 rounded-2xl">
      <Loader2 class="w-8 h-8 text-red-500 mx-auto mb-2 animate-spin" />
      <p class="text-zinc-300 font-semibold text-sm">Searching dictionary entries...</p>
    </div>

    <div v-else-if="entries.length === 0" class="text-center py-16 bg-zinc-900 border border-zinc-800 rounded-2xl">
      <Sparkles class="w-8 h-8 text-red-500 mx-auto mb-2 opacity-60" />
      <p class="text-zinc-300 font-semibold text-sm">No dictionary entries matched your query.</p>
      <button
        @click="query = ''"
        class="mt-3 px-3 py-1.5 bg-zinc-800 text-xs font-bold text-zinc-200 rounded-lg border border-zinc-700 hover:text-white"
      >
        Clear Search
      </button>
    </div>

    <div v-else class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <DictionaryCardItem
          v-for="entry in entries"
          :key="entry.id"
          :entry="entry"
          :is-analyzing="!!analysisLoading[entry.id]"
          :analysis="analysisData[entry.id]"
          @speak="handleSpeak"
          @ask-ai="handleAskAI"
          @add-flashcard="handleAddFlashcard"
        />
      </div>

      <!-- Sentinel Element for Infinite Scroll -->
      <div ref="sentinelRef" class="py-4 flex justify-center items-center min-h-[40px]">
        <Loader2 v-if="isLoadingMore" class="w-6 h-6 text-red-500 animate-spin" />
      </div>
    </div>
  </div>
</template>

