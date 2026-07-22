import { defineStore } from "pinia";
import { ref } from "vue";
import { uploadDocument } from "@/services/api";

export const useDocumentStore = defineStore("documents", () => {
    const documents = ref([]); // { id, title, chunk_count }
    const uploading = ref(false);
    const error = ref(null);

    async function upload(file) {
        uploading.value = true;
        error.value = null;
        try {
            const result = await uploadDocument(file);
            documents.value.push({
                id: result.id,
                title: result.title,
                chunk_count: result.chunk_count,
            });
            return result;
        } catch (e) {
            error.value = e.message || "Upload failed";
            throw e;
        } finally {
            uploading.value = false;
        }
    }

    return { documents, uploading, error, upload };
});
