<template>
    <div class="flex flex-col h-screen bg-slate-950 text-slate-100 font-sans overflow-hidden">
        <!-- Top Navigation / Header -->
        <header
            class="flex items-center justify-between px-6 py-3 bg-slate-900/90 border-b border-slate-800 backdrop-blur-md shrink-0 shadow-lg"
        >
            <div class="flex items-center space-x-3">
                <div
                    class="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center font-bold text-white shadow-md shadow-indigo-500/20"
                >
                    琴
                </div>
                <div>
                    <h1 class="text-lg font-bold tracking-tight text-white flex items-center gap-2">
                        <span>琴先生</span>
                        <span class="text-xs text-indigo-400 font-normal">KotoSensei</span>
                    </h1>
                    <p class="text-xs text-slate-400">Local Japanese AI Voice Tutor</p>
                </div>
            </div>

            <!-- Status Indicator -->
            <div class="flex items-center gap-3">
                <div
                    class="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700/60 text-xs"
                >
                    <span class="relative flex h-2 w-2">
                        <span
                            class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"
                        ></span>
                        <span
                            class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"
                        ></span>
                    </span>
                    <span class="text-slate-300 font-medium">Ready</span>
                </div>
            </div>
        </header>

        <!-- Main Body: Two-Column Workspace Layout -->
        <main class="flex-1 flex overflow-hidden p-4 gap-4 bg-slate-950">
            <!-- Left Workspace: Interactive Chat & Voice Tutor -->
            <section
                class="flex-1 flex flex-col min-w-0 bg-slate-900 rounded-2xl border border-slate-800 overflow-hidden shadow-xl"
            >
                <ChatArea class="flex-1 h-full" />
            </section>

            <!-- Right Workspace: Sidebar Inspector (Documents & Summaries) -->
            <aside
                class="w-[380px] lg:w-[440px] flex flex-col shrink-0 bg-slate-900 rounded-2xl border border-slate-800 overflow-hidden shadow-xl"
            >
                <!-- Tab Controls -->
                <div class="flex border-b border-slate-800 bg-slate-900/50 p-1.5 gap-1.5 shrink-0">
                    <button
                        @click="activeTab = 'documents'"
                        :class="[
                            'flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-xl text-xs font-semibold transition-all duration-200',
                            activeTab === 'documents'
                                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
                                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60',
                        ]"
                    >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M12 6207.293 7.293 1.414 1.414 0 011.414 0L15 6.414 21 12 15z"
                            />
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                            />
                        </svg>
                        Study Materials
                    </button>
                    <button
                        @click="activeTab = 'summaries'"
                        :class="[
                            'flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-xl text-xs font-semibold transition-all duration-200',
                            activeTab === 'summaries'
                                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
                                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60',
                        ]"
                    >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
                            />
                        </svg>
                        Lesson Insights
                    </button>
                </div>

                <!-- Tab Content Panel -->
                <div class="flex-1 overflow-y-auto p-4 text-slate-800">
                    <DocumentManager v-if="activeTab === 'documents'" />
                    <SessionSummaries v-else-if="activeTab === 'summaries'" />
                </div>
            </aside>
        </main>
    </div>
</template>

<script setup>
import { ref } from "vue";
import ChatArea from "@/components/ChatArea.vue";
import DocumentManager from "@/components/DocumentManager.vue";
import SessionSummaries from "@/components/SessionSummaries.vue";

const activeTab = ref("documents");
</script>

<style scoped></style>
