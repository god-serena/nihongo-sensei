import { defineStore } from 'pinia';
import { ref } from 'vue';
import { fetchSettings, saveSettings } from '../services/api';
import { AppSettings } from '../types';

export const useSettingsStore = defineStore('settings', () => {
  const provider = ref<'local' | 'openai' | 'gemini'>('local');
  const baseUrl = ref('http://localhost:11434/v1');
  const model = ref('llama3.2');
  const apiKey = ref('');
  const customSystemPrompt = ref('');
  const speechRate = ref(0.9);

  const loading = ref(false);
  const saveStatus = ref<'idle' | 'saving' | 'saved' | 'error'>('idle');

  async function loadFromBackend() {
    loading.value = true;
    try {
      const data = await fetchSettings();
      provider.value = data.provider;
      baseUrl.value = data.baseUrl;
      model.value = data.model;
      apiKey.value = data.apiKey;
      customSystemPrompt.value = data.customSystemPrompt;
      speechRate.value = data.speechRate;
    } catch (err) {
      console.warn('Failed to load settings from backend:', err);
    } finally {
      loading.value = false;
    }
  }

  async function saveToBackend(newSettings?: Partial<AppSettings>) {
    saveStatus.value = 'saving';
    try {
      const payload: AppSettings = {
        provider: newSettings?.provider ?? provider.value,
        baseUrl: newSettings?.baseUrl ?? baseUrl.value,
        model: newSettings?.model ?? model.value,
        apiKey: newSettings?.apiKey ?? apiKey.value,
        customSystemPrompt: newSettings?.customSystemPrompt ?? customSystemPrompt.value,
        speechRate: newSettings?.speechRate ?? speechRate.value,
      };

      const saved = await saveSettings(payload);
      provider.value = saved.provider;
      baseUrl.value = saved.baseUrl;
      model.value = saved.model;
      apiKey.value = saved.apiKey;
      customSystemPrompt.value = saved.customSystemPrompt;
      speechRate.value = saved.speechRate;

      saveStatus.value = 'saved';
      return true;
    } catch (err) {
      console.error('Failed to save settings:', err);
      saveStatus.value = 'error';
      return false;
    }
  }

  function setBaseUrlPreset(url: string) {
    baseUrl.value = url;
  }

  return {
    provider,
    baseUrl,
    model,
    apiKey,
    customSystemPrompt,
    speechRate,
    loading,
    saveStatus,
    loadFromBackend,
    saveToBackend,
    setBaseUrlPreset,
  };
});
