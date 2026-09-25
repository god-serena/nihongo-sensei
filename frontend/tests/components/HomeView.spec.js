import { describe, it, expect, vi } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia } from "pinia";
import HomeView from "@/views/HomeView.vue";

// Mock API calls made by child components
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
                    SenseiChat: { template: "<div class='stub-chat-area'>ChatArea Stub</div>" },
                    DocumentManager: {
                        template: "<div class='stub-doc-manager'>DocumentManager Stub</div>",
                    },
                    SessionSummaries: {
                        template: "<div class='stub-session-summaries'>SessionSummaries Stub</div>",
                    },
                    FlashcardsView: { template: "<div class='stub-flashcards'>Flashcards Stub</div>" },
                    DictionaryView: { template: "<div class='stub-dictionary'>Dictionary Stub</div>" },
                    GrammarAnalyzer: { template: "<div class='stub-analyzer'>Analyzer Stub</div>" },
                    ListeningLab: { template: "<div class='stub-listening'>Listening Stub</div>" },
                    StatsProgress: { template: "<div class='stub-stats'>Stats Stub</div>" },
                },
            },
        });
    }

    it("renders branding header and title", () => {
        const wrapper = mountComponent();
        expect(wrapper.text()).toContain("琴先生");
        expect(wrapper.text()).toContain("Koto Sensei");
    });

    it("renders ChatArea in the main workspace section", () => {
        const wrapper = mountComponent();
        expect(wrapper.find(".stub-chat-area").exists()).toBe(true);
    });

    it("renders navigation buttons for switching views", () => {
        const wrapper = mountComponent();
        const navButtons = wrapper.findAll("button");
        const buttonTexts = navButtons.map((btn) => btn.text());
        expect(buttonTexts.some((t) => t.includes("Study Materials") || t.includes("Documents"))).toBe(true);
        expect(buttonTexts.some((t) => t.includes("Lesson Insights") || t.includes("Summaries"))).toBe(true);
    });

    it("toggles view when navigation tab is clicked", async () => {
        const wrapper = mountComponent();

        // Default view is chat — ChatArea visible, others hidden
        expect(wrapper.find(".stub-chat-area").exists()).toBe(true);
        expect(wrapper.find(".stub-session-summaries").exists()).toBe(false);

        // Find the summaries nav button and click it
        const buttons = wrapper.findAll("button");
        const summariesBtn = buttons.find(
            (btn) => btn.text().includes("Lesson Insights") || btn.text().includes("Summaries"),
        );
        expect(summariesBtn).toBeDefined();

        await summariesBtn.trigger("click");

        // Now SessionSummaries should be visible and ChatArea hidden
        expect(wrapper.find(".stub-session-summaries").exists()).toBe(true);
        expect(wrapper.find(".stub-chat-area").exists()).toBe(false);
    });
});
