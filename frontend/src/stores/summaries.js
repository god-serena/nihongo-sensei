import { defineStore } from "pinia";
import { ref } from "vue";
import { createSummary } from "@/services/api";

export const useSummaryStore = defineStore("summaries", () => {
    const summaries = ref([]); // { id, summary: { topics, new_vocabulary, mistakes } }
    const generating = ref(false);
    const error = ref(null);

    async function generate(sessionId, messages, llmConfig) {
        generating.value = true;
        error.value = null;
        try {
            const result = await createSummary({ sessionId, messages, llmConfig });
            summaries.value.push(result);
            return result;
        } catch (e) {
            error.value = e.message || "Summary generation failed";
            throw e;
        } finally {
            generating.value = false;
        }
    }

    return { summaries, generating, error, generate };
});
