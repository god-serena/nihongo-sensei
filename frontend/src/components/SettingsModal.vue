<script setup lang="ts">
import { ref, watch } from 'vue';
import { X, Cpu, ScrollText, Eye, EyeOff, Check, AlertCircle, Loader2 } from 'lucide-vue-next';
import { useSettingsStore } from '../stores/settings';
import { testLlmConnection } from '../services/api';

const props = defineProps<{
  open: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
}>();

const settingsStore = useSettingsStore();

const activeTab = ref<'engine' | 'persona'>('engine');
const showApiKey = ref(false);

const testingConnection = ref(false);
const connectionResult = ref<{ success: boolean; message: string } | null>(null);

const DEFAULT_PERSONA = 'You are Koto Sensei (琴先生), a friendly, patient, and knowledgeable Japanese language teacher.';

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      settingsStore.loadFromBackend();
      connectionResult.value = null;
    }
  },
  { immediate: true }
);

async function handleTestConnection() {
  testingConnection.value = true;
  connectionResult.value = null;
  try {
    const res = await testLlmConnection({
      provider: settingsStore.provider,
      baseUrl: settingsStore.baseUrl,
      model: settingsStore.model,
      apiKey: settingsStore.apiKey,
    });
    connectionResult.value = res;
  } catch (err: any) {
    connectionResult.value = { success: false, message: err?.message || 'Connection failed' };
  } finally {
    testingConnection.value = false;
  }
}

async function handleSave() {
  const success = await settingsStore.saveToBackend();
  if (success) {
    emit('close');
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-[9999] bg-black/70 backdrop-blur-sm flex items-center justify-center p-4"
      @click.self="emit('close')"
    >
      <div class="bg-zinc-900 border border-zinc-800 rounded-2xl shadow-2xl w-full max-w-xl overflow-hidden flex flex-col max-h-[90vh]">
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-zinc-800/80 bg-zinc-950/50">
          <div class="flex items-center gap-2">
            <div class="p-2 rounded-xl bg-red-500/10 text-red-400 border border-red-500/20">
              <Cpu class="w-5 h-5" />
            </div>
            <div>
              <h2 class="text-lg font-bold text-white tracking-wide">KotoSensei Settings</h2>
              <p class="text-xs text-zinc-400">Configure LLM orchestration, base URLs & persona</p>
            </div>
          </div>
          <button
            @click="emit('close')"
            class="p-2 rounded-xl border border-zinc-800 text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors"
            aria-label="Close settings"
          >
            <X class="w-4 h-4" />
          </button>
        </div>

        <!-- Navigation Tabs -->
        <div class="flex border-b border-zinc-800 bg-zinc-950/30 px-6 pt-2">
          <button
            @click="activeTab = 'engine'"
            :class="[
              'flex items-center gap-2 px-4 py-2.5 text-xs font-semibold rounded-t-lg transition-colors border-b-2 -mb-px',
              activeTab === 'engine'
                ? 'border-red-500 text-red-400 bg-zinc-900/90'
                : 'border-transparent text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/50'
            ]"
          >
            <Cpu class="w-4 h-4" />
            LLM Engine & Connection
          </button>
          <button
            @click="activeTab = 'persona'"
            :class="[
              'flex items-center gap-2 px-4 py-2.5 text-xs font-semibold rounded-t-lg transition-colors border-b-2 -mb-px',
              activeTab === 'persona'
                ? 'border-red-500 text-red-400 bg-zinc-900/90'
                : 'border-transparent text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/50'
            ]"
          >
            <ScrollText class="w-4 h-4" />
            Persona & System Prompts
          </button>
        </div>

        <!-- Content Area -->
        <div class="p-6 overflow-y-auto space-y-5 text-sm">
          <!-- Loading State -->
          <div v-if="settingsStore.loading" class="flex flex-col items-center justify-center py-8 text-zinc-400 gap-2">
            <Loader2 class="w-6 h-6 animate-spin text-red-400" />
            <span>Loading settings...</span>
          </div>

          <!-- Tab 1: LLM Engine & Connection -->
          <div v-else-if="activeTab === 'engine'" class="space-y-5">
            <!-- Provider Selector -->
            <div>
              <label class="block text-xs font-semibold text-zinc-300 uppercase tracking-wider mb-2">
                LLM Provider
              </label>
              <select
                v-model="settingsStore.provider"
                class="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3.5 py-2.5 text-zinc-100 focus:outline-none focus:border-red-500 transition-colors"
              >
                <option value="local">Local LLM Server (Ollama / LM Studio / llama.cpp)</option>
                <option value="openai">OpenAI API</option>
                <option value="gemini">Google Gemini API</option>
              </select>
            </div>

            <!-- Base URL & Presets -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <label class="text-xs font-semibold text-zinc-300 uppercase tracking-wider">
                  Base URL
                </label>
                <!-- Quick Presets -->
                <div class="flex gap-1.5">
                  <button
                    type="button"
                    @click="settingsStore.setBaseUrlPreset('http://localhost:11434/v1')"
                    class="px-2 py-0.5 text-[10px] font-medium bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded border border-zinc-700 transition-colors"
                  >
                    Ollama :11434
                  </button>
                  <button
                    type="button"
                    @click="settingsStore.setBaseUrlPreset('http://localhost:1234/v1')"
                    class="px-2 py-0.5 text-[10px] font-medium bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded border border-zinc-700 transition-colors"
                  >
                    LM Studio :1234
                  </button>
                  <button
                    type="button"
                    @click="settingsStore.setBaseUrlPreset('http://localhost:8080/v1')"
                    class="px-2 py-0.5 text-[10px] font-medium bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded border border-zinc-700 transition-colors"
                  >
                    llama.cpp :8080
                  </button>
                </div>
              </div>
              <input
                type="text"
                v-model="settingsStore.baseUrl"
                placeholder="http://localhost:11434/v1"
                class="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3.5 py-2 text-zinc-100 font-mono text-xs focus:outline-none focus:border-red-500 transition-colors"
              />
            </div>

            <!-- Model Name -->
            <div>
              <label class="block text-xs font-semibold text-zinc-300 uppercase tracking-wider mb-2">
                Model Name
              </label>
              <input
                type="text"
                v-model="settingsStore.model"
                placeholder="e.g. llama3.2, gpt-4o, gemini-1.5-flash"
                class="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3.5 py-2 text-zinc-100 font-mono text-xs focus:outline-none focus:border-red-500 transition-colors"
              />
            </div>

            <!-- API Key -->
            <div>
              <label class="block text-xs font-semibold text-zinc-300 uppercase tracking-wider mb-2">
                API Key <span class="text-zinc-500 font-normal lowercase">(optional for local servers)</span>
              </label>
              <div class="relative">
                <input
                  :type="showApiKey ? 'text' : 'password'"
                  v-model="settingsStore.apiKey"
                  placeholder="sk-..."
                  class="w-full bg-zinc-950 border border-zinc-800 rounded-xl pl-3.5 pr-10 py-2 text-zinc-100 font-mono text-xs focus:outline-none focus:border-red-500 transition-colors"
                />
                <button
                  type="button"
                  @click="showApiKey = !showApiKey"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-zinc-200 transition-colors"
                >
                  <EyeOff v-if="showApiKey" class="w-4 h-4" />
                  <Eye v-else class="w-4 h-4" />
                </button>
              </div>
            </div>

            <!-- Test Connection Section -->
            <div class="pt-2 border-t border-zinc-800/80 flex items-center justify-between gap-4">
              <button
                type="button"
                @click="handleTestConnection"
                :disabled="testingConnection"
                class="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-medium rounded-xl border border-zinc-700 transition-colors disabled:opacity-50"
              >
                <Loader2 v-if="testingConnection" class="w-3.5 h-3.5 animate-spin" />
                <span>{{ testingConnection ? 'Testing...' : 'Test Connection' }}</span>
              </button>

              <!-- Status Badge -->
              <div v-if="connectionResult" class="flex items-center gap-2 text-xs font-medium">
                <span
                  v-if="connectionResult.success"
                  class="flex items-center gap-1.5 px-3 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full"
                >
                  <Check class="w-3.5 h-3.5" />
                  Connected
                </span>
                <span
                  v-else
                  class="flex items-center gap-1.5 px-3 py-1 bg-red-500/10 text-red-400 border border-red-500/20 rounded-full max-w-xs truncate"
                  :title="connectionResult.message"
                >
                  <AlertCircle class="w-3.5 h-3.5 flex-shrink-0" />
                  <span class="truncate">Error: {{ connectionResult.message }}</span>
                </span>
              </div>
            </div>
          </div>

          <!-- Tab 2: Persona & System Prompts -->
          <div v-else-if="activeTab === 'persona'" class="space-y-5">
            <!-- Default Persona (Read-only) -->
            <div>
              <label class="block text-xs font-semibold text-zinc-300 uppercase tracking-wider mb-2">
                Default KotoSensei Persona <span class="text-zinc-500 font-normal lowercase">(read-only)</span>
              </label>
              <textarea
                readonly
                :value="DEFAULT_PERSONA"
                rows="3"
                class="w-full bg-zinc-950/60 border border-zinc-800/80 rounded-xl px-3.5 py-2.5 text-zinc-400 text-xs font-mono focus:outline-none resize-none"
              ></textarea>
            </div>

            <!-- Custom System Prompt -->
            <div>
              <label class="block text-xs font-semibold text-zinc-300 uppercase tracking-wider mb-2">
                Custom Instructions / System Prompt Additions
              </label>
              <textarea
                v-model="settingsStore.customSystemPrompt"
                rows="6"
                placeholder="Add custom teaching instructions, JLPT focus, or specific speaking styles here..."
                class="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3.5 py-2.5 text-zinc-100 text-xs font-mono focus:outline-none focus:border-red-500 transition-colors resize-y"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="flex items-center justify-between px-6 py-4 border-t border-zinc-800 bg-zinc-950/50">
          <div class="text-xs font-medium">
            <span v-if="settingsStore.saveStatus === 'saving'" class="text-amber-400 flex items-center gap-1.5">
              <Loader2 class="w-3.5 h-3.5 animate-spin" /> Saving...
            </span>
            <span v-else-if="settingsStore.saveStatus === 'saved'" class="text-emerald-400 flex items-center gap-1.5">
              <Check class="w-3.5 h-3.5" /> Saved!
            </span>
            <span v-else-if="settingsStore.saveStatus === 'error'" class="text-red-400 flex items-center gap-1.5">
              <AlertCircle class="w-3.5 h-3.5" /> Failed to save settings
            </span>
          </div>

          <div class="flex items-center gap-3">
            <button
              type="button"
              @click="emit('close')"
              class="px-4 py-2 text-xs font-medium text-zinc-400 hover:text-white transition-colors"
            >
              Cancel
            </button>
            <button
              type="button"
              @click="handleSave"
              :disabled="settingsStore.saveStatus === 'saving'"
              class="px-5 py-2 text-xs font-semibold bg-red-600 hover:bg-red-500 text-white rounded-xl shadow-lg shadow-red-600/20 transition-all active:scale-95 disabled:opacity-50"
            >
              Save Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
