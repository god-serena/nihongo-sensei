const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";
const WS_BASE = import.meta.env.VITE_WS_BASE ?? "ws://localhost:8000";

export async function getHealth() {
    const res = await fetch(`${API_BASE}/api/health`);
    return res.json();
}

export async function postChat(payload) {
    const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    return res.json();
}

export async function uploadDocument(file) {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/api/rag/upload`, {
        method: "POST",
        body: formData,
    });
    return res.json();
}

export async function createSummary(payload) {
    const res = await fetch(`${API_BASE}/api/summaries`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    return res.json();
}

export function createSpeechWebSocket() {
    return new WebSocket(`${WS_BASE}/ws/speech`);
}
