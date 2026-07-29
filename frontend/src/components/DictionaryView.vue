<script setup lang="ts">
import { ref, computed } from 'vue';
import { Search, Volume2, Bookmark, BookmarkCheck, Sparkles, Filter } from 'lucide-vue-next';
import type { DictionaryEntry, JLPTLevel } from '../types';
import { INITIAL_DICTIONARY as dictionaryEntries } from '../data/japaneseData';
import { speakJapanese } from '../services/api';

const props = defineProps<{
  savedVocabIds: string[];
}>();

const emit = defineEmits<{
  (e: 'toggle-saved-vocab', id: string): void;
}>();

const query = ref('');
const selectedJlptFilter = ref<string>('ALL');

const filteredEntries = computed(() => {
  return dictionaryEntries.filter(entry => {
    const matchesQuery =
      !query.value ||
      entry.kanji.toLowerCase().includes(query.value.toLowerCase()) ||
      entry.reading.toLowerCase().includes(query.value.toLowerCase()) ||
      entry.romaji.toLowerCase().includes(query.value.toLowerCase()) ||
      entry.meanings.some(m => m.toLowerCase().includes(query.value.toLowerCase()));

    const matchesJlpt = selectedJlptFilter.value === 'ALL' || entry.jlpt === selectedJlptFilter.value;

    return matchesQuery && matchesJlpt;
  });
});

function handleSpeak(text: string) {
  speakJapanese(text);
}

function isSaved(id: string) {
  return props.savedVocabIds.includes(id);
}
</script>

<template>
  <div class="max-w-5xl mx-auto px-4 py-4 w-full space-y-6">
    
    <!-- Header & Search Box -->
    <div class="bg-zinc-900 border border-zinc-800 rounded-2xl p-5 shadow-lg space-y-4">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div>
          <h2 class="text-base font-bold text-white flex items-center gap-2">
            Japanese Dictionary & Pitch Accent Reference
            <span class="text-xs font-mono font-normal px-2 py-0.5 rounded bg-red-950 text-red-400 border border-red-800">
              {{ filteredEntries.length }} Entries
            </span>
          </h2>
          <p class="text-xs text-zinc-400">Search by Kanji, Hiragana, Romaji, or English meanings.</p>
        </div>

        <!-- JLPT Filter Buttons -->
        <div class="flex items-center gap-1 bg-zinc-950 p-1 rounded-lg border border-zinc-800 text-xs font-semibold">
          <button
            v-for="lvl in ['ALL', 'N5', 'N4', 'N3', 'N2', 'N1']"
            :key="lvl"
            @click="selectedJlptFilter = lvl"
            :class="[
              'px-2.5 py-1 rounded transition-colors',
              selectedJlptFilter === lvl ? 'bg-red-600 text-white font-bold' : 'text-zinc-400 hover:text-white'
            ]"
          >
            {{ lvl }}
          </button>
        </div>
      </div>

      <!-- Search Input Bar -->
      <div class="relative">
        <Search class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
        <input
          v-model="query"
          type="text"
          placeholder="Type Kanji, Hiragana, Romaji or English (e.g., '桜', 'sakura', 'cherry')..."
          class="w-full bg-zinc-950 border border-zinc-800 text-white placeholder-zinc-500 rounded-xl pl-10 pr-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-600 font-sans"
        />
      </div>
    </div>

    <!-- Dictionary Cards Grid -->
    <div v-if="filteredEntries.length === 0" class="text-center py-16 bg-zinc-900 border border-zinc-800 rounded-2xl">
      <Sparkles class="w-8 h-8 text-red-500 mx-auto mb-2 opacity-60" />
      <p class="text-zinc-300 font-semibold text-sm">No dictionary entries matched your query.</p>
      <button
        @click="query = ''; selectedJlptFilter = 'ALL'"
        class="mt-3 px-3 py-1.5 bg-zinc-800 text-xs font-bold text-zinc-200 rounded-lg border border-zinc-700 hover:text-white"
      >
        Clear Search & Filters
      </button>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div
        v-for="entry in filteredEntries"
        :key="entry.id"
        class="bg-zinc-900/90 hover:bg-zinc-900 border border-zinc-800/80 hover:border-red-600/40 rounded-xl p-5 transition-all shadow-md flex flex-col justify-between space-y-3 group"
      >
        <!-- Card Header -->
        <div class="flex items-start justify-between gap-3">
          <div class="flex items-baseline gap-3">
            <span class="text-3xl font-bold font-jp text-white">
              {{ entry.kanji }}
            </span>
            <div class="flex flex-col">
              <span class="text-sm font-semibold text-red-400 font-jp">
                {{ entry.reading }}
              </span>
              <span class="text-[11px] font-mono text-zinc-500">
                {{ entry.romaji }}
              </span>
            </div>
          </div>

          <div class="flex items-center gap-1.5">
            <span class="text-[10px] font-bold text-red-400 bg-red-950 px-2 py-0.5 rounded border border-red-800">
              {{ entry.jlpt }}
            </span>

            <button
              @click="handleSpeak(entry.reading || entry.kanji)"
              class="p-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 transition-colors"
              title="Pronounce word"
            >
              <Volume2 class="w-3.5 h-3.5 text-red-500" />
            </button>

            <button
              @click="emit('toggle-saved-vocab', entry.id)"
              :class="[
                'p-1.5 rounded-lg border transition-colors',
                isSaved(entry.id)
                  ? 'bg-red-600/20 border-red-500 text-red-400'
                  : 'bg-zinc-800 border-zinc-700 text-zinc-400 hover:text-white'
              ]"
              :title="isSaved(entry.id) ? 'Remove from saved vocabulary' : 'Save to vocabulary list'"
            >
              <BookmarkCheck v-if="isSaved(entry.id)" class="w-3.5 h-3.5 text-red-500" />
              <Bookmark v-else class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        <!-- Part of Speech & Meanings -->
        <div class="space-y-2">
          <div class="flex flex-wrap gap-1">
            <span
              v-for="(p, idx) in entry.pos"
              :key="idx"
              class="text-[10px] uppercase font-bold text-zinc-400 bg-zinc-950 px-2 py-0.5 rounded border border-zinc-800"
            >
              {{ p }}
            </span>
            <span v-if="entry.pitchAccent" class="text-[10px] font-mono text-amber-400 bg-amber-950/40 px-2 py-0.5 rounded border border-amber-900/50">
              Pitch: {{ entry.pitchAccent }}
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

        <!-- Example Sentence -->
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

      </div>
    </div>

  </div>
</template>
