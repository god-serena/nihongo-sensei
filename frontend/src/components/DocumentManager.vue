<template>
    <div class="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <h2 class="mb-4 text-xl font-semibold text-gray-800">Document Manager</h2>

        <!-- Drop zone -->
        <div
            ref="dropZone"
            class="relative flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 bg-gray-50 p-10 transition-colors hover:border-blue-400 hover:bg-blue-50"
            :class="{ 'border-blue-500 bg-blue-50': isDragOver }"
            @dragover.prevent="isDragOver = true"
            @dragleave.prevent="isDragOver = false"
            @drop.prevent="onDrop"
            @click="triggerFileInput"
        >
            <input
                ref="fileInput"
                type="file"
                accept=".txt,.md,.pdf"
                class="hidden"
                @change="onFileSelect"
            />
            <svg
                class="mb-3 h-10 w-10 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
            >
                <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
            </svg>
            <p class="text-gray-600">
                Drag & drop files here, or
                <span class="text-blue-500 underline">click to browse</span>
            </p>
            <p class="mt-1 text-sm text-gray-400">.txt, .md, .pdf</p>
        </div>

        <!-- Upload progress -->
        <div v-if="documentStore.uploading" class="mt-4 flex items-center gap-3">
            <svg class="h-5 w-5 animate-spin text-blue-500" fill="none" viewBox="0 0 24 24">
                <circle
                    class="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    stroke-width="4"
                />
                <path
                    class="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
            </svg>
            <span class="text-sm text-gray-600">Uploading document…</span>
        </div>

        <!-- Error feedback -->
        <div v-if="documentStore.error" class="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">
            {{ documentStore.error }}
        </div>

        <!-- Document list -->
        <div v-if="documentStore.documents.length" class="mt-6 space-y-3">
            <h3 class="text-lg font-medium text-gray-700">Uploaded Documents</h3>
            <div
                v-for="doc in documentStore.documents"
                :key="doc.id"
                class="flex items-center justify-between rounded-lg border border-gray-200 bg-gray-50 p-4"
            >
                <div class="flex items-center gap-3">
                    <svg
                        class="h-6 w-6 text-gray-500"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                        />
                    </svg>
                    <span class="font-medium text-gray-800">{{ doc.title }}</span>
                </div>
                <span class="rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-700">
                    {{ doc.chunk_count }} chunks
                </span>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from "vue";
import { useDocumentStore } from "@/stores/documents";

const documentStore = useDocumentStore();
const isDragOver = ref(false);
const fileInput = ref(null);

function triggerFileInput() {
    fileInput.value?.click();
}

async function onFileSelect(event) {
    const file = event.target.files?.[0];
    if (file) {
        try {
            await documentStore.upload(file);
        } catch {
            // Error is set in documentStore.error
        }
        // Reset so the same file can be re-uploaded
        event.target.value = "";
    }
}

async function onDrop(event) {
    isDragOver.value = false;
    const file = event.dataTransfer?.files?.[0];
    if (file) {
        try {
            await documentStore.upload(file);
        } catch {
            // Error is set in documentStore.error
        }
    }
}
</script>
