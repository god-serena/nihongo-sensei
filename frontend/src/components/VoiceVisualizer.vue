<template>
    <canvas ref="canvasRef" class="w-full h-full rounded bg-transparent"></canvas>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from "vue";

const props = defineProps({
    active: { type: Boolean, default: false },
    barCount: { type: Number, default: 24 },
    color: { type: String, default: "#c84040" },
});

const emit = defineEmits(["error"]);

const canvasRef = ref(null);

let audioContext = null;
let analyser = null;
let stream = null;
let animationId = null;

function drawBars() {
    if (!analyser || !canvasRef.value) return;

    const canvas = canvasRef.value;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const rect = canvas.getBoundingClientRect ? canvas.getBoundingClientRect() : { width: 320, height: 96 };
    if (rect.width && rect.height && (canvas.width !== rect.width || canvas.height !== rect.height)) {
        canvas.width = rect.width;
        canvas.height = rect.height;
    }

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyser.getByteFrequencyData(dataArray);

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const gap = 3;
    const barWidth = Math.max(2, (canvas.width - gap * (props.barCount - 1)) / props.barCount);
    let x = 0;

    for (let i = 0; i < props.barCount; i++) {
        const index = Math.floor((i * bufferLength) / props.barCount);
        const value = dataArray[index] || 0;

        const barHeight = Math.max(3, (value / 255) * canvas.height * 0.85);

        ctx.fillStyle = props.color;
        ctx.fillRect(x, canvas.height / 2 - barHeight / 2, barWidth, barHeight);
        x += barWidth + gap;
    }

    animationId = requestAnimationFrame(drawBars);
}

function startVisualization() {
    if (!canvasRef.value) return;

    navigator.mediaDevices
        .getUserMedia({ audio: true })
        .then((mediaStream) => {
            if (!props.active) {
                mediaStream.getTracks().forEach((track) => track.stop());
                return;
            }
            stream = mediaStream;
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const source = audioContext.createMediaStreamSource(stream);

            analyser = audioContext.createAnalyser();
            analyser.fftSize = 2048;
            analyser.smoothingTimeConstant = 0.3;

            source.connect(analyser);

            drawBars();
        })
        .catch((err) => {
            emit("error", { message: err.message || "Microphone access denied" });
        });
}

function stopVisualization() {
    if (animationId) {
        cancelAnimationFrame(animationId);
        animationId = null;
    }

    if (stream) {
        stream.getTracks().forEach((track) => track.stop());
        stream = null;
    }

    if (audioContext) {
        audioContext.close();
        audioContext = null;
    }

    analyser = null;
}

onMounted(() => {
    if (props.active) {
        startVisualization();
    }
});

watch(
    () => props.active,
    (newVal) => {
        if (newVal) {
            startVisualization();
        } else {
            stopVisualization();
        }
    },
);

onUnmounted(() => {
    stopVisualization();
});
</script>
