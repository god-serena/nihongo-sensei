import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia } from "pinia";
import SessionSummaries from "@/components/SessionSummaries.vue";

// ── Mock API ────────────────────────────────────────────────────────────────

const mockCreateSummary = vi.fn();

vi.mock("@/services/api", () => ({
    createSummary: (...args) => mockCreateSummary(...args),
}));

// ── Helpers ─────────────────────────────────────────────────────────────────

const defaultProps = {
    sessionId: "sess-1",
    messages: [
        { role: "user", content: "こんにちは" },
        { role: "assistant", content: "こんにちは！何かお手伝いできますか？" },
    ],
    llmConfig: { model: "gpt-4o-mini" },
};

function mountComponent(props = defaultProps) {
    const pinia = createPinia();
    return mount(SessionSummaries, {
        global: { plugins: [pinia] },
        props,
    });
}

const mockSummary = {
    id: 1,
    summary: {
        topics: ["挨拶", "自己紹介"],
        new_vocabulary: [
            { term: "琴", reading: "こと", meaning: "koto (zither)" },
            { term: "日本語", reading: "にほんご", meaning: "Japanese language" },
        ],
        mistakes: [
            {
                original: "私は行きます学校",
                correction: "私は学校に行きます",
                explanation: "Word order: destination + に + 行きます",
            },
        ],
    },
};

// ── Tests ───────────────────────────────────────────────────────────────────

describe("SessionSummaries.vue", () => {
    beforeEach(() => {
        mockCreateSummary.mockReset().mockResolvedValue(mockSummary);
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it("renders the generate button", () => {
        const wrapper = mountComponent();
        expect(wrapper.text()).toContain("Generate Summary");
    });

    it('shows "No summaries yet" when empty', () => {
        const wrapper = mountComponent();
        expect(wrapper.text()).toContain("No summaries yet");
    });

    it("disables the generate button while generating", async () => {
        let resolveGen;
        mockCreateSummary.mockReturnValue(
            new Promise((resolve) => {
                resolveGen = resolve;
            }),
        );
        const wrapper = mountComponent();
        const button = wrapper.find("button");

        await button.trigger("click");
        await wrapper.vm.$nextTick();

        expect(button.attributes("disabled")).toBeDefined();
        expect(button.text()).toContain("Generating");
        resolveGen(mockSummary);
    });

    it("renders summary topics when generated", async () => {
        mockCreateSummary.mockResolvedValue(mockSummary);
        const wrapper = mountComponent();
        const button = wrapper.find("button");

        await button.trigger("click");
        await wrapper.vm.$nextTick();

        expect(wrapper.text()).toContain("挨拶");
        expect(wrapper.text()).toContain("自己紹介");
    });

    it("renders vocabulary table with term, reading, meaning", async () => {
        mockCreateSummary.mockResolvedValue(mockSummary);
        const wrapper = mountComponent();
        const button = wrapper.find("button");

        await button.trigger("click");
        await wrapper.vm.$nextTick();

        expect(wrapper.text()).toContain("琴");
        expect(wrapper.text()).toContain("こと");
        expect(wrapper.text()).toContain("koto (zither)");
        expect(wrapper.text()).toContain("日本語");
        expect(wrapper.text()).toContain("にほんご");
    });

    it("renders mistake cards with expandable details", async () => {
        mockCreateSummary.mockResolvedValue(mockSummary);
        const wrapper = mountComponent();
        const button = wrapper.find("button");

        await button.trigger("click");
        await wrapper.vm.$nextTick();

        expect(wrapper.text()).toContain("私は行きます学校");
        expect(wrapper.text()).toContain("私は学校に行きます");
        expect(wrapper.text()).toContain("Word order");
    });

    it("emits error on generation failure", async () => {
        const err = new Error("API error");
        mockCreateSummary.mockImplementation(() => Promise.reject(err));
        const wrapper = mountComponent();
        const button = wrapper.find("button");

        await button.trigger("click");
        await wrapper.vm.$nextTick();
        await wrapper.vm.$nextTick();
        await wrapper.vm.$nextTick();

        expect(wrapper.emitted("error")).toBeTruthy();
        expect(wrapper.emitted("error")[0]).toEqual(["API error"]);
    });

    it("calls createSummary with correct payload", async () => {
        mockCreateSummary.mockResolvedValue(mockSummary);
        const wrapper = mountComponent();
        const button = wrapper.find("button");

        await button.trigger("click");
        await wrapper.vm.$nextTick();

        expect(mockCreateSummary).toHaveBeenCalledWith({
            sessionId: "sess-1",
            messages: defaultProps.messages,
            llmConfig: { model: "gpt-4o-mini" },
        });
    });
});
