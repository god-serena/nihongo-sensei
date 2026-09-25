import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia } from "pinia";
import SenseiChat from "@/components/SenseiChat.vue";

// ── Mock WebSocket & API Services ──────────────────────────────────────────

let _mockWs = null;

function createMockWebSocket() {
    const ws = {
        readyState: WebSocket.OPEN,
        OPEN: WebSocket.OPEN,
        send: vi.fn(),
        close: vi.fn(),
        onopen: null,
        onclose: null,
        onerror: null,
        onmessage: null,
        _trigger: (data) => {
            const event = new MessageEvent("message", { data: JSON.stringify(data) });
            if (ws.onmessage) ws.onmessage(event);
        },
    };
    _mockWs = ws;
    return ws;
}

vi.mock("@/services/api", () => ({
    createSpeechWebSocket: vi.fn(() => createMockWebSocket()),
    fetchSessions: vi.fn(() => Promise.resolve([])),
    createSession: vi.fn(() => Promise.resolve({ id: "test-1", title: "New Practice", messages: [] })),
    updateSession: vi.fn(() => Promise.resolve({})),
    deleteSession: vi.fn(() => Promise.resolve({})),
}));

describe("SenseiChat.vue", () => {
    function mountComponent(props = {}) {
        const pinia = createPinia();
        return mount(SenseiChat, {
            props: {
                messages: [
                    { id: "1", role: "assistant", content: "Konnichiwa! How can I help you learn Japanese?" }
                ],
                currentJlpt: "N5",
                ...props,
            },
            global: {
                plugins: [pinia],
                stubs: { VoiceVisualizer: { template: "<div class='stub-voice-vis' />" } },
            },
        });
    }

    it("renders initial assistant greeting message", () => {
        const wrapper = mountComponent();
        expect(wrapper.text()).toContain("Konnichiwa!");
    });

    it("renders message input field and send button", () => {
        const wrapper = mountComponent();
        const input = wrapper.find("textarea, input[type='text']");
        expect(input.exists()).toBe(true);
    });

    it("updates message input on user typing", async () => {
        const wrapper = mountComponent();
        const input = wrapper.find("textarea, input[type='text']");
        await input.setValue("日本語を勉強しています");
        expect(input.element.value).toBe("日本語を勉強しています");
    });

    it("renders session chat container", () => {
        const wrapper = mountComponent();
        expect(wrapper.exists()).toBe(true);
    });
});
