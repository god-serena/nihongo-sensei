<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-[15px] font-semibold text-gray-900">Session Summaries</h2>
      <button
        :disabled="summaryStore.generating"
        @click="onGenerate"
        class="rounded-xl bg-gray-900 text-white px-3.5 py-1.5 text-[12px] font-semibold hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors cursor-pointer"
      >{{ summaryStore.generating ? "Generating…" : "Generate Summary" }}</button>
    </div>

    <!-- Error -->
    <div v-if="summaryStore.error" class="rounded-xl bg-red-50 border border-red-200 px-3 py-2 text-[12px] text-red-600">{{ summaryStore.error }}</div>

    <!-- Empty state -->
    <div v-if="!summaryStore.summaries.length && !summaryStore.generating" class="text-center py-8 text-[13px] text-gray-400">
      No summaries yet. Generate one to see structured session insights.
    </div>

    <!-- Summary cards -->
    <div v-for="(item, idx) in summaryStore.summaries" :key="item.id || idx" class="rounded-xl border border-gray-200 bg-gray-50 p-4 space-y-3">
      <!-- Topics -->
      <div v-if="item.summary?.topics?.length">
        <h3 class="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-1">Topics</h3>
        <div class="flex flex-wrap gap-1.5">
          <span v-for="topic in item.summary.topics" :key="topic" class="px-2 py-0.5 rounded bg-gray-200 text-[12px] font-medium text-gray-700">{{ topic }}</span>
        </div>
      </div>

      <!-- Vocabulary -->
      <div v-if="item.summary?.new_vocabulary?.length">
        <h3 class="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-1">New Vocabulary</h3>
        <table class="min-w-full divide-y divide-gray-200 text-[12px]">
          <thead><tr class="text-left text-gray-500"><th class="pb-1 pr-3 font-medium">Term</th><th class="pb-1 pr-3 font-medium">Reading</th><th class="pb-1 font-medium">Meaning</th></tr></thead>
          <tbody class="divide-y divide-gray-100 text-gray-700">
            <tr v-for="v in item.summary.new_vocabulary" :key="v.term">
              <td class="py-1.5 pr-3 font-semibold text-gray-900">{{ v.term }}</td>
              <td class="py-1.5 pr-3">{{ v.reading }}</td>
              <td class="py-1.5">{{ v.meaning }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mistakes -->
      <div v-if="item.summary?.mistakes?.length">
        <h3 class="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-1">Mistakes</h3>
        <div class="space-y-1.5">
          <details v-for="(m, mIdx) in item.summary.mistakes" :key="mIdx" class="rounded-xl border border-gray-200 bg-white overflow-hidden">
            <summary class="cursor-pointer list-none px-3 py-2 text-[12px] font-medium text-gray-800 select-none">{{ m.original }}</summary>
            <div class="border-t border-gray-200 px-3 py-2 text-[12px] text-gray-600 space-y-1 bg-gray-50">
              <p><span class="font-semibold text-gray-800">Correction:</span> {{ m.correction }}</p>
              <p><span class="font-semibold text-gray-800">Explanation:</span> {{ m.explanation }}</p>
            </div>
          </details>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useSummaryStore } from "@/stores/summaries";

const summaryStore = useSummaryStore();

const props = defineProps({
  sessionId: { type: String, required: true },
  messages:  { type: Array,  default: () => [] },
  llmConfig: { type: Object, default: () => ({}) },
});

const emit = defineEmits(["error"]);

async function onGenerate() {
  try { await summaryStore.generate(props.sessionId, props.messages, props.llmConfig); }
  catch (e) { emit("error", e.message); }
}
</script>
