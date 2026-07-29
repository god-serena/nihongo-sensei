<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-[15px] font-semibold text-gray-900">Document Manager</h2>
      <span class="text-[12px] text-gray-400">{{ documentStore.documents.length }} loaded</span>
    </div>

    <!-- Drop zone -->
    <div
      ref="dropZone"
      class="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-gray-200 bg-gray-50 p-8 cursor-pointer transition-colors hover:border-gray-400"
      :class="{ 'border-blue-500 bg-blue-50': isDragOver }"
      @dragover.prevent="isDragOver = true"
      @dragleave.prevent="isDragOver = false"
      @drop.prevent="onDrop"
      @click="triggerFileInput"
    >
      <input ref="fileInput" type="file" accept=".txt,.md,.pdf" class="hidden" @change="onFileSelect" />
      <svg class="w-8 h-8 text-gray-400 mb-2" fill="none" stroke="currentColor" stroke-width="1.6" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/></svg>
      <p class="text-[13px] text-gray-600">Drag & drop files here, or <span class="text-gray-900 font-medium underline">click to browse</span></p>
      <p class="text-[11px] text-gray-400 mt-1">.txt, .md, .pdf</p>
    </div>

    <!-- Upload progress -->
    <div v-if="documentStore.uploading" class="flex items-center gap-2 text-[13px] text-gray-500">
      <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
      Uploading document…
    </div>

    <!-- Error -->
    <div v-if="documentStore.error" class="rounded-xl bg-red-50 border border-red-200 px-3 py-2 text-[12px] text-red-600">{{ documentStore.error }}</div>

    <!-- Document list -->
    <div v-if="documentStore.documents.length" class="space-y-2">
      <h3 class="text-[12px] font-semibold text-gray-400 uppercase tracking-wider">Uploaded Documents</h3>
      <div v-for="doc in documentStore.documents" :key="doc.id" class="flex items-center justify-between rounded-xl bg-gray-50 border border-gray-200 px-4 py-3">
        <div class="flex items-center gap-2 min-w-0">
          <svg class="w-5 h-5 text-gray-500 shrink-0" fill="none" stroke="currentColor" stroke-width="1.6" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
          <span class="text-[13px] font-medium text-gray-800 truncate">{{ doc.title }}</span>
        </div>
        <span class="rounded-full bg-gray-200 px-2.5 py-0.5 text-[11px] font-medium text-gray-600 shrink-0">{{ doc.chunk_count }} chunks</span>
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

function triggerFileInput() { fileInput.value?.click(); }

async function onFileSelect(event) {
  const file = event.target.files?.[0];
  if (file) { try { await documentStore.upload(file); } catch {} event.target.value = ""; }
}

async function onDrop(event) {
  isDragOver.value = false;
  const file = event.dataTransfer?.files?.[0];
  if (file) { try { await documentStore.upload(file); } catch {} }
}
</script>
