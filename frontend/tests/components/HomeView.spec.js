import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia } from "pinia";
import HomeView from "@/views/HomeView.vue";

// Mock API calls made by child components if needed
vi.mock("@/services/api", () => ({
    createSpeechWebSocket: vi.fn(() => ({
        readyState: 1,
        OPEN: 1,
        send: vi.fn(),
        close: vi.fn(),
    })),
    uploadDocument: vi.fn().mockResolvedValue({ id: 1, title: "test.txt", chunk_count: 3 }),
    generateSummary: vi
        .fn()
        .mockResolvedValue({
            id: 1,
            topics: ["Greetings"],
            new_vocabulary: [],
            common_mistakes: [],
        }),
    getSummaries: vi.fn().mockResolvedValue([]),
}));

describe("HomeView.vue", () => {
    function mountComponent() {
        const pinia = createPinia();
        return mount(HomeView, {
            global: {
                plugins: [pinia],
                stubs: {
                    ChatArea: { template: "<div class='stub-chat-area'>ChatArea Stub</div>" },
                    DocumentManager: {
                        template: "<div class='stub-doc-manager'>DocumentManager Stub</div>",
                    },
                    SessionSummaries: {
                        template: "<div class='stub-session-summaries'>SessionSummaries Stub</div>",
                    },
                },
            },
        });
    }

    it("renders branding header and title", () => {
        const wrapper = mountComponent();
        expect(wrapper.text()).toContain("琴先生");
        expect(wrapper.text()).toContain("KotoSensei");
    });

    it("renders ChatArea in the main workspace section", () => {
        const wrapper = mountComponent();
        expect(wrapper.find(".stub-chat-area").exists()).toBe(true);
    });

    it("renders tab toggles for Study Materials and Lesson Summaries", () => {
        const wrapper = mountComponent();
        const tabs = wrapper.findAll("button");
        const tabTexts = tabs.map((btn) => btn.text());
        expect(tabTexts.some((t) => t.includes("Study Materials") || t.includes("Documents"))).toBe(
            true,
        );
        expect(tabTexts.some((t) => t.includes("Summaries") || t.includes("Insights"))).toBe(true);
    });

    it("toggles auxiliary view when tab is clicked", async () => {
        const wrapper = mountComponent();

        // Default tab should show DocumentManager
        expect(wrapper.find(".stub-doc-manager").exists()).toBe(true);
        expect(wrapper.find(".stub-session-summaries").exists()).toBe(false);

        // Find the summaries tab button and click it
        const buttons = wrapper.findAll("button");
        const summariesBtn = buttons.find(
            (btn) => btn.text().includes("Summaries") || btn.text().includes("Insights"),
        );
        expect(summariesBtn).toBeDefined();

        await summariesBtn.trigger("click");

        // Now SessionSummaries should be visible and DocumentManager hidden
        expect(wrapper.find(".stub-session-summaries").exists()).toBe(true);
        expect(wrapper.find(".stub-doc-manager").exists()).toBe(false);
    });
});
