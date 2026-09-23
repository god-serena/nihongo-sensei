<script setup lang="ts">
import { Search, Loader2 } from 'lucide-vue-next';

defineProps<{
  query: string;
  isLoading: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:query', value: string): void;
}>();
</script>

<template>
  <div class="bg-zinc-900 border border-zinc-800 rounded-2xl p-5 shadow-lg space-y-4">
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
      <div>
        <h2 class="text-base font-bold text-white flex items-center gap-2">
          JMdict Japanese Dictionary
        </h2>
        <p class="text-xs text-zinc-400">Search by Kanji, Hiragana, or English meanings.</p>
      </div>
    </div>

    <!-- Search Input Bar -->
    <div class="relative">
      <Search class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
      <input
        :value="query"
        @input="emit('update:query', ($event.target as HTMLInputElement).value)"
        type="text"
        placeholder="Type Kanji, Hiragana, or English (e.g., '桜', 'さくら', 'cherry')..."
        class="w-full bg-zinc-950 border border-zinc-800 text-white placeholder-zinc-500 rounded-lg pl-10 pr-10 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-600 font-sans"
      />
      <div v-if="isLoading" class="absolute right-3.5 top-1/2 -translate-y-1/2">
        <Loader2 class="w-4 h-4 text-red-500 animate-spin" />
      </div>
    </div>
  </div>
</template>
