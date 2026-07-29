<script setup lang="ts">
import { ref, watch, nextTick, onMounted } from 'vue';
import { RefreshCw, MessageSquare, ChevronsRight } from 'lucide-vue-next';
import type { ChatMessage, JLPTLevel, Session, SentenceAnalysis } from '../types';
import {
  sendChatMessageStream,
  fetchSessions,
  fetchSessionById,
  createSession,
  updateSession,
  deleteSession
} from '../services/api';

import SessionSidebar from './chat/SessionSidebar.vue';
import ChatHeader from './chat/ChatHeader.vue';
import ChatMessageItem from './chat/ChatMessageItem.vue';
import GrammarBreakdown from './chat/GrammarBreakdown.vue';
import ChatInput from './chat/ChatInput.vue';

const props = defineProps<{
  messages: ChatMessage[];
  currentJlpt: JLPTLevel;
  savedVocabIds?: string[];
}>();

const emit = defineEmits<{
  (e: 'update:messages', newMessages: ChatMessage[]): void;
  (e: 'save-vocab', word: string): void;
  (e: 'clear-messages'): void;
}>();

// ── Orchestrator State ──────────────────────────────────────────────────────
const sidebarOpen = ref(true);
const sessions = ref<Session[]>([]);
const activeSession = ref<Session | null>(null);
const sidebarLoading = ref(true);
const isTeachingModeLocked = ref(false);
const teachingMode = ref<'bilingual' | 'immersion'>('bilingual');

const loading = ref(false);
const streamingMessageId = ref<string | null>(null);
const activeAnalysis = ref<SentenceAnalysis | null>(null);
const chatEndRef = ref<HTMLDivElement | null>(null);

// ── Teaching Mode Persistence ──────────────────────────────────────────────
watch(teachingMode, (newVal) => {
  try {
    localStorage.setItem('koto_teaching_mode', newVal);
  } catch (e) {
    console.error('Error saving teaching mode to localStorage:', e);
  }
});

// ── Sessions Management ────────────────────────────────────────────────────
async function loadSessions() {
  try {
    sidebarLoading.value = true;
    const all = await fetchSessions();
    sessions.value = all;
  } catch (e) {
    console.error('Failed to load sessions:', e);
  } finally {
    sidebarLoading.value = false;
  }
}

async function handleNewSession() {
  try {
    const created = await createSession({ title: 'New Practice' });
    emit('clear-messages');
    activeSession.value = created;
    isTeachingModeLocked.value = false;
    await loadSessions();
    sidebarOpen.value = true;
  } catch (e) {
    console.error('Failed to create session:', e);
  }
}

async function handleSelectSession(session: Session) {
  try {
    const full = await fetchSessionById(session.id);
    activeSession.value = full;
    teachingMode.value = full.teaching_mode;
    isTeachingModeLocked.value = true;
    if (full.messages && full.messages.length > 0) {
      emit('update:messages', full.messages);
    }
  } catch (e) {
    console.error('Failed to select session:', e);
  }
}

async function handleDeleteSession(sessionId: number) {
  try {
    await deleteSession(sessionId);
    if (activeSession.value?.id === sessionId) {
      activeSession.value = null;
      emit('clear-messages');
    }
    await loadSessions();
  } catch (e) {
    console.error('Failed to delete session:', e);
  }
}

async function handleRenameSession(payload: { id: number; title: string }) {
  try {
    await updateSession(payload.id, { title: payload.title });
    if (activeSession.value?.id === payload.id) {
      activeSession.value = { ...activeSession.value, title: payload.title };
    }
    await loadSessions();
  } catch (e) {
    console.error('Failed to rename session:', e);
  }
}

// ── Auto-save ────────────────────────────────────────────────────────────────
let saveTimer: ReturnType<typeof setTimeout> | null = null;

watch(
  () => props.messages,
  (newMessages) => {
    if (!activeSession.value) return;
    if (saveTimer) clearTimeout(saveTimer);
    saveTimer = setTimeout(async () => {
      try {
        const updated = await updateSession(activeSession.value!.id, {
          title: newMessages.length <= 2 ? 'New Practice' : (activeSession.value!.title || 'New Practice'),
          messages: newMessages,
        });
        activeSession.value = updated;
        await loadSessions();
      } catch (e) {
        console.error('Auto-save failed:', e);
      }
    }, 1000);
  },
  { deep: true }
);

// ── Scroll & Life Cycle ──────────────────────────────────────────────────────
function scrollToBottom() {
  nextTick(() => {
    chatEndRef.value?.scrollIntoView({ behavior: 'smooth' });
  });
}

watch(() => props.messages.length, () => {
  scrollToBottom();
});

onMounted(async () => {
  await loadSessions();
  scrollToBottom();
  const savedMode = localStorage.getItem('koto_teaching_mode');
  if (savedMode === 'bilingual' || savedMode === 'immersion') {
    teachingMode.value = savedMode;
  }
});

// ── Send & Stream Handler ────────────────────────────────────────────────────
async function handleSend(text: string) {
  if (!text.trim() || loading.value) return;

  const userMsg: ChatMessage = {
    id: `msg-${Date.now()}`,
    role: 'user',
    content: text,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  };

  const updatedMessages = [...props.messages, userMsg];
  emit('update:messages', updatedMessages);
  loading.value = true;
  streamingMessageId.value = `msg-stream-${Date.now()}`;

  const streamingMsg: ChatMessage = {
    id: streamingMessageId.value,
    role: 'assistant',
    content: '',
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    jlptLevel: props.currentJlpt
  };

  let fullReply = '';

  try {
    await sendChatMessageStream(
      text,
      updatedMessages,
      props.currentJlpt,
      'Grammar & Practice',
      (token: string) => {
        fullReply += token;
        emit('update:messages', [
          ...updatedMessages,
          { ...streamingMsg, content: fullReply }
        ]);
        scrollToBottom();
      },
      (complete: string) => {
        emit('update:messages', [
          ...updatedMessages,
          { ...streamingMsg, content: complete }
        ]);
        streamingMessageId.value = null;
        loading.value = false;
      },
      (err: any) => {
        console.error('Stream error:', err);
        emit('update:messages', [
          ...updatedMessages,
          { ...streamingMsg, content: `**Error:** ${err?.message || 'Streaming failed.'}` }
        ]);
        streamingMessageId.value = null;
        loading.value = false;
      },
      teachingMode.value
    );
  } catch (err) {
    console.error('Error sending message:', err);
    emit('update:messages', [
      ...updatedMessages,
      { ...streamingMsg, content: `**Error:** ${(err as any)?.message || 'Failed to get response.'}` }
    ]);
    streamingMessageId.value = null;
    loading.value = false;
  }
}

function handleAnalyze(msg: ChatMessage) {
  // Mock / simple grammar analysis structure for selected message
  activeAnalysis.value = {
    translation: msg.content,
    tokens: [
      { surface: msg.content.substring(0, 10), pos: 'Phrase', english: 'Selected text chunk' }
    ],
    grammarNotes: ['Analysis generated for selected Sensei response.']
  };
}

function handleSaveVocab(word: string) {
  emit('save-vocab', word);
}
</script>

<template>
  <div class="flex flex-col h-[calc(100vh-154px)] max-w-5xl mx-auto px-4 w-full py-2 sm:py-4 overflow-hidden">
    <!-- Top Session Header -->
    <ChatHeader
      :activeSession="activeSession"
      :currentJlpt="currentJlpt"
      v-model:teachingMode="teachingMode"
      :isLocked="isTeachingModeLocked"
    />

    <!-- Main Content Area -->
    <div class="flex-1 min-h-0 flex overflow-hidden relative">
      <!-- Floating overlay Sidebar (positioned absolutely, controlled by sidebarOpen state) -->
      <SessionSidebar
        :sessions="sessions"
        :activeSessionId="activeSession?.id ?? null"
        :sidebarOpen="sidebarOpen"
        :loading="sidebarLoading"
        :activeSession="activeSession"
        @select-session="handleSelectSession"
        @new-session="handleNewSession"
        @delete-session="handleDeleteSession"
        @rename-session="handleRenameSession"
        @toggle-sidebar="sidebarOpen = !sidebarOpen"
      />

      <!-- Chat Feed & Input Area -->
      <div class="flex-1 flex flex-col min-w-0">
        <!-- Messages Scroll Container -->
        <div class="flex-1 min-h-0 overflow-y-auto space-y-4 pr-1 sm:pr-2 py-2">
          <ChatMessageItem
            v-for="msg in messages"
            :key="msg.id"
            :msg="msg"
            :streamingMessageId="streamingMessageId"
            @analyze="handleAnalyze"
            @save-vocab="handleSaveVocab"
          />

          <!-- Loading Spinner Indicator -->
          <div v-if="loading && !streamingMessageId" class="flex gap-3 max-w-md mr-auto">
            <div class="w-8 h-8 rounded-lg bg-red-600 text-white font-bold text-xs flex items-center justify-center ring-1 ring-red-400">
              琴
            </div>
            <div class="bg-zinc-900 text-zinc-300 border border-zinc-800 rounded-xl p-4 text-xs flex items-center gap-2">
              <RefreshCw class="w-4 h-4 text-red-500 animate-spin" />
              <span>琴先生 is thinking and preparing response...</span>
            </div>
          </div>

          <!-- Active Grammar Breakdown Panel if triggered -->
          <GrammarBreakdown
            v-if="activeAnalysis"
            :analysis="activeAnalysis"
            @close="activeAnalysis = null"
            @save-vocab="handleSaveVocab"
          />

          <div ref="chatEndRef" />
        </div>

        <!-- Bottom Row: Collapsed sidebar bar (30%) + Chat Input (70%) -->
        <div class="shrink-0 flex items-center gap-2 w-full top-[703px]">
          <div
            @click="sidebarOpen = true"
            class="w-[30%] sm:w-[28%] h-[46px] bg-zinc-900 border border-zinc-800 rounded-xl px-3 flex items-center justify-between gap-2 shadow-lg hover:border-zinc-700 cursor-pointer shrink-0"
          >
            <div class="flex items-center gap-2 min-w-0">
              <MessageSquare class="w-4 h-4 text-red-500 shrink-0" />
              <span class="text-xs font-semibold text-zinc-200 truncate">
                {{ activeSession?.title || 'New Practice' }}
              </span>
            </div>
            <ChevronsRight class="w-4 h-4 text-zinc-400 shrink-0" />
          </div>
          <ChatInput
            :loading="loading"
            @send="handleSend"
            class="flex-1 min-w-0"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #3f3f46;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #52525b;
}
</style>
