import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";
import VoiceVisualizer from "@/components/VoiceVisualizer.vue";

describe("VoiceVisualizer", () => {
    let mockTrack;
    let mockStream;
    let mockSource;
    let mockAnalyser;
    let mockAudioCtx;

    beforeEach(() => {
        mockTrack = { stop: vi.fn() };
        mockStream = { getTracks: vi.fn(() => [mockTrack]) };
        mockSource = { connect: vi.fn() };
        mockAnalyser = {
            fftSize: 2048,
            smoothingTimeConstant: 0.3,
            frequencyBinCount: 1024,
            getByteFrequencyData: vi.fn(),
        };
        mockAudioCtx = {
            createMediaStreamSource: vi.fn(() => mockSource),
            createAnalyser: vi.fn(() => mockAnalyser),
            close: vi.fn(),
        };

        // Replace AudioContext with a constructor that returns our mock via closure.
        // This must be a 'function' (not arrow) to work with `new`.
        window.AudioContext = function FakeAudioContext() {
            return mockAudioCtx;
        };
        window.webkitAudioContext = window.AudioContext;

        // Replace getUserMedia to resolve with our mock stream.
        navigator.mediaDevices.getUserMedia = vi.fn().mockResolvedValue(mockStream);

        // Stub rAF/cAF asynchronously like real browser animation frames
        let rafCounter = 0;
        window.requestAnimationFrame = vi.fn((cb) => {
            rafCounter++;
            const id = rafCounter;
            setTimeout(() => cb(performance.now()), 0);
            return id;
        });
        window.cancelAnimationFrame = vi.fn();
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    function stubCanvas(wrapper) {
        const canvas = wrapper.find("canvas").element;
        canvas.width = 320;
        canvas.height = 96;
        const ctx = { clearRect: vi.fn(), fillRect: vi.fn(), fillStyle: "" };
        vi.spyOn(canvas, "getContext").mockReturnValue(ctx);
        return ctx;
    }

    // ── Test 1: error emission ────────────────────────────────────────────────

    it("emits error when getUserMedia is denied", async () => {
        navigator.mediaDevices.getUserMedia = vi
            .fn()
            .mockRejectedValue(new DOMException("Permission denied", "NotAllowedError"));

        const wrapper = mount(VoiceVisualizer, {
            props: { active: true },
            attachTo: document.body,
        });

        await flushPromises();

        expect(wrapper.emitted("error")).toBeTruthy();
        expect(wrapper.emitted("error")[0][0].message).toContain("Permission denied");
    });

    // ── Test 2: starts visualization ──────────────────────────────────────────

    it("starts visualization when active becomes true", async () => {
        const wrapper = mount(VoiceVisualizer, {
            props: { active: false },
            attachTo: document.body,
        });
        stubCanvas(wrapper);

        await wrapper.setProps({ active: true });
        await flushPromises();

        expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalledWith({
            audio: true,
        });
        expect(mockAnalyser.getByteFrequencyData).toHaveBeenCalled();
    });

    // ── Test 3: stops visualization ───────────────────────────────────────────

    it("stops visualization when active becomes false", async () => {
        const wrapper = mount(VoiceVisualizer, {
            props: { active: false },
            attachTo: document.body,
        });
        stubCanvas(wrapper);

        await wrapper.setProps({ active: true });
        await flushPromises();

        await wrapper.setProps({ active: false });
        await flushPromises();

        expect(window.cancelAnimationFrame).toHaveBeenCalledWith(1);
        expect(mockTrack.stop).toHaveBeenCalled();
        expect(mockAudioCtx.close).toHaveBeenCalled();
    });

    // ── Test 4: cleanup on unmount ────────────────────────────────────────────

    it("cleans up on unmount", async () => {
        const wrapper = mount(VoiceVisualizer, {
            props: { active: true },
            attachTo: document.body,
        });
        stubCanvas(wrapper);

        await flushPromises();

        wrapper.unmount();

        expect(window.cancelAnimationFrame).toHaveBeenCalled();
        expect(mockTrack.stop).toHaveBeenCalled();
        expect(mockAudioCtx.close).toHaveBeenCalled();
    });
});
