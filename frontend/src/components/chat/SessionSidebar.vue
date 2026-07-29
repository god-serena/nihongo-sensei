<script setup lang="ts">
import { ref } from 'vue';
import { MessageSquare, Plus, Trash2, Pencil, Check, ChevronsLeft } from 'lucide-vue-next';
import type { Session } from '../../types';

const props = defineProps<{
  sessions: Session[];
  activeSessionId: number | null;
  sidebarOpen: boolean;
  loading: boolean;
  activeSession: Session | null;
}>();

const emit = defineEmits<{
  (e: 'select-session', session: Session): void;
  (e: 'new-session'): void;
  (e: 'delete-session', sessionId: number): void;
  (e: 'rename-session', payload: { id: number; title: string }): void;
  (e: 'toggle-sidebar'): void;
}>();

const editingSessionId = ref<number | null>(null);
const editingTitle = ref('');
const deleteConfirmId = ref<number | null>(null);

function startRename(session: Session, e: Event) {
  e?.stopPropagation();
  editingSessionId.value = session.id;
  editingTitle.value = session.title || 'Untitled';
}

function saveRename(sessionId: number) {
  if (!editingTitle.value.trim()) {
    cancelRename();
    return;
  }
  emit('rename-session', { id: sessionId, title: editingTitle.value.trim() });
  editingSessionId.value = null;
  editingTitle.value = '';
}

function cancelRename() {
  editingSessionId.value = null;
  editingTitle.value = '';
}

function handleDeleteClick(sessionId: number, e: Event) {
  e?.stopPropagation();
  deleteConfirmId.value = sessionId;
}

function confirmDelete() {
  if (deleteConfirmId.value !== null) {
    emit('delete-session', deleteConfirmId.value);
    deleteConfirmId.value = null;
  }
}

function cancelDelete() {
  deleteConfirmId.value = null;
}

function formatDate(dateStr: string): string {
  if (!dateStr) return 'Recent';
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
}

function groupByDate(sessionsList: Session[]): Record<string, Session[]> {
  const groups: Record<string, Session[]> = {};
  for (const s of sessionsList) {
    const key = formatDate(s.updated_at || s.created_at);
    if (!groups[key]) groups[key] = [];
    groups[key].push(s);
  }
  return groups;
}
</script>

<template>
  <!-- Backdrop overlay — shown when sidebar is open to collapse drawer -->
  <div
    v-if="sidebarOpen"
    class="fixed inset-0 z-30 bg-black/40"
    @click="emit('toggle-sidebar')"
  />

  <!-- Expanded floating drawer panel — absolute overlay on left -->
  <aside
    v-if="sidebarOpen"
    class="absolute left-0 top-0 bottom-0 z-40 w-72 sm:w-80 shadow-2xl bg-zinc-900/98 backdrop-blur-md border-r border-zinc-800 rounded-xl flex flex-col min-w-0"
  >
    <div class="flex flex-col h-full min-w-0">
      <!-- Sidebar Header -->
      <div class="flex items-center justify-between px-3 py-2.5 border-b border-zinc-800">
        <span class="text-xs font-bold text-zinc-300 uppercase tracking-wider flex items-center gap-1.5">
          <MessageSquare class="w-3.5 h-3.5 text-red-500" />
          Practice Sessions
        </span>
        <div class="flex items-center gap-1">
          <button
            @click="emit('toggle-sidebar')"
            class="p-1.5 rounded-md hover:bg-zinc-800 text-zinc-400 hover:text-white transition-all cursor-pointer"
            title="Collapse sidebar"
          >
            <ChevronsLeft class="w-3.5 h-3.5" />
          </button>
          <button
            @click="emit('new-session')"
            class="p-1.5 rounded-md bg-red-600 hover:bg-red-500 text-white transition-all cursor-pointer"
            title="New Practice"
          >
            <Plus class="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      <!-- Sessions List -->
      <div class="flex-1 overflow-y-auto p-2">
        <template v-if="loading">
          <div class="text-xs text-zinc-500 px-2 py-4 text-center">Loading sessions...</div>
        </template>
        <template v-else-if="sessions.length === 0">
          <div class="text-xs text-zinc-500 px-2 py-4 text-center">No practice sessions yet.</div>
        </template>
        <template v-else>
          <div v-for="(group, date) in groupByDate(sessions)" :key="date" class="mb-3">
            <div class="text-[11px] font-semibold text-zinc-500 uppercase tracking-wider px-2 py-1">
              {{ date }}
            </div>
            <div class="space-y-1">
              <div
                v-for="s in group"
                :key="s.id"
                @click="editingSessionId !== s.id && emit('select-session', s)"
                :class="[
                  'flex items-center justify-between gap-1 px-2.5 py-2 rounded-lg text-sm transition-all',
                  activeSessionId === s.id
                    ? 'bg-red-950/60 text-red-100 border border-red-900/40'
                    : 'text-zinc-300 hover:bg-zinc-800/80 border border-transparent'
                ]"
                :style="editingSessionId === s.id ? { cursor: 'default' } : { cursor: 'pointer' }"
              >
                <!-- Inline rename input -->
                <div v-if="editingSessionId === s.id" class="flex-1 min-w-0 flex items-center gap-1">
                  <input
                    v-model="editingTitle"
                    @keydown.enter.prevent="saveRename(s.id)"
                    @keydown.esc="cancelRename"
                    class="flex-1 bg-zinc-950 text-zinc-100 text-sm rounded-md px-2 py-1 border border-red-700 focus:outline-none focus:ring-1 focus:ring-red-500 font-medium truncate"
                    autofocus
                  />
                  <button
                    @click="saveRename(s.id)"
                    class="shrink-0 p-1 rounded hover:bg-red-900/60 text-red-400 transition-all cursor-pointer"
                    title="Save title"
                  >
                    <Check class="w-3.5 h-3.5" />
                  </button>
                </div>
                <!-- Normal display -->
                <template v-else>
                  <div class="flex-1 min-w-0">
                    <div class="font-medium truncate">{{ s.title || 'Untitled' }}</div>
                    <div class="text-[11px] text-zinc-500">
                      {{ s.message_count ?? s.messages?.length ?? 0 }} messages
                    </div>
                  </div>
                  <!-- Rename button -->
                  <button
                    @click="startRename(s, $event)"
                    class="shrink-0 p-1 rounded hover:bg-red-950/60 text-zinc-500 hover:text-red-400 transition-all cursor-pointer"
                    title="Rename session"
                  >
                    <Pencil class="w-3.5 h-3.5" />
                  </button>
                  <!-- Delete button (only show when not active session) -->
                  <button
                    v-if="activeSessionId !== s.id"
                    @click="handleDeleteClick(s.id, $event)"
                    class="shrink-0 p-1 rounded hover:bg-red-950 text-zinc-600 hover:text-red-400 transition-all cursor-pointer"
                    title="Delete session"
                  >
                    <Trash2 class="w-3.5 h-3.5" />
                  </button>
                  <span v-else class="shrink-0 text-[10px] px-1.5 py-0.5 rounded bg-red-950 text-red-400">
                    Active
                  </span>
                </template>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="deleteConfirmId !== null"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60"
      @click="cancelDelete"
    >
      <div
        class="bg-zinc-900 border border-zinc-700 rounded-xl p-6 max-w-sm w-full mx-4 shadow-2xl"
        @click.stop
      >
        <h3 class="text-lg font-bold text-white mb-2">Delete Session?</h3>
        <p class="text-sm text-zinc-400 mb-4">
          This will permanently delete this practice session and all its messages. This action cannot be undone.
        </p>
        <div class="flex gap-3 justify-end">
          <button
            @click="cancelDelete"
            class="px-4 py-2 rounded-lg bg-zinc-800 text-zinc-300 hover:bg-zinc-700 cursor-pointer transition-all text-sm"
          >
            Cancel
          </button>
          <button
            @click="confirmDelete"
            class="px-4 py-2 rounded-lg bg-red-600 text-white hover:bg-red-500 cursor-pointer transition-all text-sm"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  </aside>
</template>
