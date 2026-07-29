<script setup lang="ts">
import { ref } from 'vue';
import { Headphones, Volume2, CheckCircle2, XCircle, RotateCcw, HelpCircle } from 'lucide-vue-next';
import type { ListeningExercise, JLPTLevel } from '../types';
import { INITIAL_LISTENING as listeningExercises } from '../data/japaneseData';
import { speakJapanese } from '../services/api';

const props = defineProps<{
  currentJlpt: JLPTLevel;
}>();

const emit = defineEmits<{
  (e: 'listening-complete'): void;
}>();

const selectedIndex = ref(0);
const selectedOption = ref<number | null>(null);
const showAnswer = ref(false);
const audioSpeed = ref<number>(1.0);

const currentExercise = ref<ListeningExercise>(listeningExercises[0]);

function selectExercise(idx: number) {
  selectedIndex.value = idx;
  currentExercise.value = listeningExercises[idx];
  selectedOption.value = null;
  showAnswer.value = false;
}

function handlePlayAudio() {
  speakJapanese(currentExercise.value.japaneseText, audioSpeed.value);
}

function submitAnswer(optIdx: number) {
  selectedOption.value = optIdx;
  showAnswer.value = true;
  if (optIdx === currentExercise.value.correctIndex) {
    emit('listening-complete');
  }
}

function resetExercise() {
  selectedOption.value = null;
  showAnswer.value = false;
}
</script>

<template>
  <div class="max-w-5xl mx-auto px-4 py-4 w-full space-y-6">
    
    <!-- Exercise Picker Header -->
    <div class="bg-zinc-900 border border-zinc-800 rounded-2xl p-5 shadow-lg space-y-4">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div>
          <h2 class="text-base font-bold text-white flex items-center gap-2">
            <Headphones class="w-4 h-4 text-red-500" />
            Listening Comprehension & Audio Lab (聴解)
          </h2>
          <p class="text-xs text-zinc-400">
            Listen to authentic native speech, adjust playback speed, and test your understanding.
          </p>
        </div>

        <!-- Speed Buttons -->
        <div class="flex items-center gap-1 bg-zinc-950 p-1 rounded-lg border border-zinc-800 text-xs font-semibold">
          <span class="text-zinc-500 px-2">Speed:</span>
          <button
            v-for="spd in [0.75, 1.0, 1.25]"
            :key="spd"
            @click="audioSpeed = spd"
            :class="[
              'px-2 py-0.5 rounded transition-colors',
              audioSpeed === spd ? 'bg-red-600 text-white font-bold' : 'text-zinc-400 hover:text-white'
            ]"
          >
            {{ spd }}x
          </button>
        </div>
      </div>

      <!-- Scenarios Selector -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
        <button
          v-for="(ex, idx) in listeningExercises"
          :key="ex.id"
          @click="selectExercise(idx)"
          :class="[
            'p-3 rounded-xl border text-left transition-all',
            selectedIndex === idx
              ? 'bg-red-950/40 border-red-600/80 text-white'
              : 'bg-zinc-950 border-zinc-800 text-zinc-400 hover:text-zinc-200'
          ]"
        >
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-white">{{ ex.title }}</span>
            <span class="text-[10px] font-bold text-red-400 bg-red-950 px-1.5 py-0.2 rounded border border-red-800">
              {{ ex.level }}
            </span>
          </div>
          <p class="text-[11px] font-jp text-zinc-400 truncate mt-1">{{ ex.japaneseText }}</p>
        </button>
      </div>
    </div>

    <!-- Active Listening Card -->
    <div class="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 shadow-xl space-y-6">
      
      <!-- Audio Playback Control Hero -->
      <div class="bg-zinc-950 border border-zinc-800 rounded-xl p-6 text-center space-y-4">
        <div class="w-14 h-14 rounded-2xl bg-red-600/20 border border-red-500/50 text-red-500 mx-auto flex items-center justify-center shadow-lg shadow-red-600/20">
          <Headphones class="w-7 h-7" />
        </div>

        <div>
          <h3 class="text-lg font-bold text-white">{{ currentExercise.title }}</h3>
          <p class="text-xs text-zinc-400">Click the button below to play the audio scenario in Japanese.</p>
        </div>

        <button
          @click="handlePlayAudio"
          class="px-6 py-3 rounded-xl bg-red-600 hover:bg-red-500 text-white font-bold text-sm shadow-lg shadow-red-600/30 inline-flex items-center gap-2 transition-all"
        >
          <Volume2 class="w-5 h-5" />
          Play Japanese Audio ({{ audioSpeed }}x)
        </button>
      </div>

      <!-- Question & Options -->
      <div class="space-y-4">
        <h4 class="text-sm font-bold text-white flex items-center gap-2">
          <HelpCircle class="w-4 h-4 text-red-500" />
          Comprehension Question: {{ currentExercise.question }}
        </h4>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <button
            v-for="(opt, optIdx) in currentExercise.options"
            :key="optIdx"
            @click="submitAnswer(optIdx)"
            :disabled="showAnswer"
            :class="[
              'p-4 rounded-xl border font-semibold text-xs text-left transition-all flex items-center justify-between gap-2',
              showAnswer && optIdx === currentExercise.correctIndex
                ? 'bg-emerald-950/60 border-emerald-500 text-emerald-300'
                : showAnswer && selectedOption === optIdx && optIdx !== currentExercise.correctIndex
                ? 'bg-red-950/60 border-red-500 text-red-300'
                : 'bg-zinc-950 border-zinc-800 text-zinc-200 hover:border-zinc-700'
            ]"
          >
            <span>{{ opt }}</span>
            <CheckCircle2 v-if="showAnswer && optIdx === currentExercise.correctIndex" class="w-4 h-4 text-emerald-400 shrink-0" />
            <XCircle v-else-if="showAnswer && selectedOption === optIdx && optIdx !== currentExercise.correctIndex" class="w-4 h-4 text-red-400 shrink-0" />
          </button>
        </div>
      </div>

      <!-- Explanation & Script Reveal -->
      <div v-if="showAnswer" class="space-y-4 pt-4 border-t border-zinc-800">
        <!-- Transcript -->
        <div class="bg-zinc-950 p-4 rounded-xl border border-zinc-800 space-y-1.5">
          <span class="text-[10px] uppercase font-bold text-red-500 tracking-wider">Full Audio Transcript:</span>
          <p class="text-base font-jp font-bold text-white">{{ currentExercise.japaneseText }}</p>
          <p class="text-xs font-jp text-red-400">{{ currentExercise.reading }}</p>
          <p class="text-xs text-zinc-400 italic">"{{ currentExercise.englishTranslation }}"</p>
        </div>

        <!-- Explanation -->
        <div class="bg-zinc-950 p-4 rounded-xl border border-zinc-800 space-y-1">
          <span class="text-[10px] uppercase font-bold text-zinc-400 tracking-wider">Explanation:</span>
          <p class="text-xs text-zinc-300 leading-relaxed">{{ currentExercise.explanation }}</p>
        </div>

        <button
          @click="resetExercise"
          class="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-bold rounded-lg border border-zinc-700 inline-flex items-center gap-1.5"
        >
          <RotateCcw class="w-3.5 h-3.5" />
          Try Again
        </button>
      </div>

    </div>

  </div>
</template>
