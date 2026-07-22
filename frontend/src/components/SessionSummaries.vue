<template>
    <div class="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <div class="mb-4 flex items-center justify-between">
            <h2 class="text-xl font-semibold text-gray-800">Session Summaries</h2>
            <button
                :disabled="summaryStore.generating"
                @click="onGenerate"
                class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
                {{ summaryStore.generating ? "Generating…" : "Generate Summary" }}
            </button>
        </div>

        <!-- Error feedback -->
        <div v-if="summaryStore.error" class="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">
            {{ summaryStore.error }}
        </div>

        <!-- No summaries yet -->
        <div
            v-if="!summaryStore.summaries.length && !summaryStore.generating"
            class="text-center py-8 text-gray-400"
        >
            No summaries yet. Generate one to see structured session insights.
        </div>

        <!-- Summary cards -->
        <div
            v-for="(item, idx) in summaryStore.summaries"
            :key="item.id || idx"
            class="mb-6 rounded-xl border border-gray-200 bg-gray-50 p-5"
        >
            <!-- Topics -->
            <div v-if="item.summary?.topics?.length" class="mb-4">
                <h3 class="mb-2 text-sm font-semibold uppercase tracking-wide text-gray-500">
                    Topics
                </h3>
                <ul class="list-inside list-disc space-y-1 text-gray-700">
                    <li v-for="topic in item.summary.topics" :key="topic">{{ topic }}</li>
                </ul>
            </div>

            <!-- New Vocabulary -->
            <div v-if="item.summary?.new_vocabulary?.length" class="mb-4">
                <h3 class="mb-2 text-sm font-semibold uppercase tracking-wide text-gray-500">
                    New Vocabulary
                </h3>
                <table class="min-w-full divide-y divide-gray-200 text-sm">
                    <thead>
                        <tr class="text-left text-gray-500">
                            <th class="pb-2 pr-4 font-medium">Term</th>
                            <th class="pb-2 pr-4 font-medium">Reading</th>
                            <th class="pb-2 font-medium">Meaning</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
                        <tr v-for="vocab in item.summary.new_vocabulary" :key="vocab.term">
                            <td class="pr-4 py-2 font-medium text-gray-800">
                                {{ vocab.term }}
                            </td>
                            <td class="pr-4 py-2 text-gray-600">{{ vocab.reading }}</td>
                            <td class="py-2 text-gray-600">{{ vocab.meaning }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Mistakes -->
            <div v-if="item.summary?.mistakes?.length" class="mt-4">
                <h3 class="mb-2 text-sm font-semibold uppercase tracking-wide text-gray-500">
                    Mistakes
                </h3>
                <div class="space-y-2">
                    <details
                        v-for="(mistake, mIdx) in item.summary.mistakes"
                        :key="mIdx"
                        class="rounded-lg border border-gray-200 bg-white"
                    >
                        <summary
                            class="cursor-pointer list-none p-3 text-sm font-medium text-gray-700"
                        >
                            {{ mistake.original }}
                        </summary>
                        <div class="border-t border-gray-200 p-3 text-sm text-gray-600">
                            <p>
                                <span class="font-medium text-gray-700">Correction:</span>
                                {{ mistake.correction }}
                            </p>
                            <p class="mt-1">
                                <span class="font-medium text-gray-700">Explanation:</span>
                                {{ mistake.explanation }}
                            </p>
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

// Exposes session ID, messages, and llmConfig to the parent
const props = defineProps({
    sessionId: { type: String, required: true },
    messages: { type: Array, default: () => [] },
    llmConfig: { type: Object, default: () => ({}) },
});

const emit = defineEmits(["error"]);

async function onGenerate() {
    try {
        await summaryStore.generate(props.sessionId, props.messages, props.llmConfig);
    } catch (e) {
        emit("error", e.message);
    }
}
</script>
