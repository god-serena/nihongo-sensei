/**
 * Vitest global setup file.
 * Runs once per worker, before each test file is loaded.
 * Stubs browser APIs that are absent or read-only in jsdom.
 */

// ── navigator.mediaDevices.getUserMedia ─────────────────────────────────────
// jsdom exposes mediaDevices as a read-only getter on the Navigator prototype.
// We replace the whole property descriptor so tests can override getUserMedia.
Object.defineProperty(window.navigator, "mediaDevices", {
    writable: true,
    configurable: true,
    value: {
        getUserMedia: () => Promise.resolve({ getTracks: () => [] }),
    },
});

// ── AudioContext ─────────────────────────────────────────────────────────────
// jsdom has no AudioContext. Provide a minimal stub so `new AudioContext()`
// doesn't throw. Tests override the individual methods they need to spy on.
function MockAudioContext() {
    this.state = "running";
    this.close = () => Promise.resolve();
    this.createMediaStreamSource = () => ({ connect: () => {} });
    this.createAnalyser = () => ({
        fftSize: 2048,
        smoothingTimeConstant: 0.3,
        frequencyBinCount: 1024,
        getByteFrequencyData: () => {},
    });
}
window.AudioContext = MockAudioContext;
window.webkitAudioContext = MockAudioContext;

// ── requestAnimationFrame ────────────────────────────────────────────────────
// jsdom may define a no-op rAF. Provide a synchronous one-shot stub so
// canvas draw loops execute immediately in tests.
let _rafId = 0;
window.requestAnimationFrame = (cb) => {
    cb(performance.now());
    return ++_rafId;
};
window.cancelAnimationFrame = () => {};
