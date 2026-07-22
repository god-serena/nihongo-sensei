import { defineStore } from "pinia";
import { ref } from "vue";

export const useAudioStore = defineStore("audio", () => {
    const isListening = ref(false);
    const isSpeaking = ref(false);

    function startListening() {
        isListening.value = true;
    }

    function stopListening() {
        isListening.value = false;
    }

    return { isListening, isSpeaking, startListening, stopListening };
});
