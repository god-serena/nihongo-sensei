import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia } from "pinia";
import ChatArea from "@/components/ChatArea.vue";

// ── Mock WebSocket ──────────────────────────────────────────────────────────

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
}));

// ── Helpers ─────────────────────────────────────────────────────────────────

function resetStores() {
    _mockWs = null;
}

// ── Tests ───────────────────────────────────────────────────────────────────

describe("ChatArea.vue", () => {
    beforeEach(() => {
        resetStores();
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    function mountComponent() {
        const pinia = createPinia();
        return mount(ChatArea, {
            global: {
                plugins: [pinia],
                stubs: { VoiceVisualizer: { template: "<div />" } },
            },
        });
    }

    it("renders PTT button", () => {
        const wrapper = mountComponent();
        const pttBtn = wrapper.findAll("button").find(b => b.text().includes("Push-to-Talk"));
        expect(pttBtn).toBeDefined();
    });

    it("renders cancel button when isSpeaking is true", async () => {
        const wrapper = mountComponent();
        const { useAudioStore } = await import("@/stores/audio");
        const audioStore = useAudioStore();
        audioStore.isSpeaking = true;
        await wrapper.vm.$nextTick();
        const cancelBtn = wrapper.findAll("button").find(b => b.text().includes("Cancel"));
        expect(cancelBtn).toBeDefined();
    });

    it("does not render cancel button when isSpeaking is false", async () => {
        const wrapper = mountComponent();
        const { useAudioStore } = await import("@/stores/audio");
        const audioStore = useAudioStore();
        audioStore.isSpeaking = false;
        await wrapper.vm.$nextTick();
        const cancelBtn = wrapper.findAll("button").find(b => b.text().includes("Cancel"));
        expect(cancelBtn).toBeUndefined();
    });

    it("appends tokens from WebSocket messages", async () => {
        const wrapper = mountComponent();
        const { useChatStore } = await import("@/stores/chat");
        const chatStore = useChatStore();
        _mockWs._trigger({ type: "token", token: "Hello" });
        await wrapper.vm.$nextTick();
        expect(chatStore.partialResponse).toBe("Hello");
    });

    it("commits partial response when done is received", async () => {
        const wrapper = mountComponent();
        const { useChatStore } = await import("@/stores/chat");
        const chatStore = useChatStore();
        chatStore.partialResponse = "Hello world";
        _mockWs._trigger({ type: "done" });
        await wrapper.vm.$nextTick();
        expect(chatStore.messages).toHaveLength(1);
        expect(chatStore.messages[0].role).toBe("assistant");
        expect(chatStore.messages[0].content).toBe("Hello world");
    });

    it("adds user message when transcript is received", async () => {
        const wrapper = mountComponent();
        const { useChatStore } = await import("@/stores/chat");
        const chatStore = useChatStore();
        _mockWs._trigger({ type: "transcript", text: "こんにちは" });
        await wrapper.vm.$nextTick();
        expect(chatStore.messages).toHaveLength(1);
        expect(chatStore.messages[0].role).toBe("user");
        expect(chatStore.messages[0].content).toBe("こんにちは");
    });

    it("sends cancel message when cancel button is clicked", async () => {
        const wrapper = mountComponent();
        const { useAudioStore } = await import("@/stores/audio");
        const audioStore = useAudioStore();
        audioStore.isSpeaking = true;
        await wrapper.vm.$nextTick();
        const cancelBtn = wrapper.findAll("button").find(b => b.text().includes("Cancel"));
        expect(cancelBtn).toBeDefined();
        await cancelBtn.trigger("click");
        expect(_mockWs.send).toHaveBeenCalledWith(JSON.stringify({ type: "cancel" }));
    });
});
