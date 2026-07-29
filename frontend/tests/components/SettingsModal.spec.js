import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import SettingsModal from "@/components/SettingsModal.vue";
import { useSettingsStore } from "@/stores/settings";
import * as api from "@/services/api";

vi.mock("@/services/api", () => ({
  fetchSettings: vi.fn().mockResolvedValue({
    provider: "local",
    baseUrl: "http://localhost:11434/v1",
    model: "llama3.2",
    apiKey: "",
    customSystemPrompt: "Custom test prompt",
    speechRate: 0.9,
  }),
  saveSettings: vi.fn().mockImplementation(async (s) => s),
  testLlmConnection: vi.fn().mockResolvedValue({ success: true, message: "Connected" }),
}));

describe("SettingsModal.vue", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  function mountComponent(props = { open: true }) {
    return mount(SettingsModal, {
      props,
      global: {
        plugins: [createPinia()],
        stubs: {
          Teleport: true,
        },
      },
    });
  }

  it("renders when open is true", async () => {
    const wrapper = mountComponent();
    await flushPromises();
    expect(wrapper.text()).toContain("KotoSensei Settings");
    expect(wrapper.text()).toContain("LLM Provider");
  });

  it("switches tabs between LLM Engine and Persona", async () => {
    const wrapper = mountComponent();
    await flushPromises();
    const tabs = wrapper.findAll("button");
    const personaTab = tabs.find((b) => b.text().includes("Persona & System Prompts"));
    expect(personaTab).toBeDefined();

    if (personaTab) {
      await personaTab.trigger("click");
    }
    expect(wrapper.text()).toContain("Default KotoSensei Persona");
    expect(wrapper.text()).toContain("Custom Instructions");
  });

  it("updates base URL preset when preset button is clicked", async () => {
    const wrapper = mountComponent();
    await flushPromises();
    const store = useSettingsStore();
    const lmStudioBtn = wrapper.findAll("button").find((b) => b.text().includes("LM Studio"));
    expect(lmStudioBtn).toBeDefined();

    if (lmStudioBtn) {
      await lmStudioBtn.trigger("click");
    }
    expect(store.baseUrl).toBe("http://localhost:1234/v1");
  });

  it("calls testLlmConnection when Test Connection is clicked", async () => {
    const wrapper = mountComponent();
    await flushPromises();
    const testBtn = wrapper.findAll("button").find((b) => b.text().includes("Test Connection"));
    expect(testBtn).toBeDefined();

    if (testBtn) {
      await testBtn.trigger("click");
    }
    expect(api.testLlmConnection).toHaveBeenCalled();
  });

  it("calls saveToBackend and emits close on save", async () => {
    const wrapper = mountComponent();
    await flushPromises();
    const saveBtn = wrapper.findAll("button").find((b) => b.text().includes("Save Settings"));
    expect(saveBtn).toBeDefined();

    if (saveBtn) {
      await saveBtn.trigger("click");
      await flushPromises();
    }
    expect(wrapper.emitted("close")).toBeTruthy();
  });
});
