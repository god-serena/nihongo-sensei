import { ChatMessage, JLPTLevel, AppSettings, Session, DictionaryEntry } from '../types';

const BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(/\/$/, '');

function buildUrl(path: string): string {
  const cleanPath = path.startsWith('/api') ? path.slice(4) : path;
  return `${BASE_URL}${cleanPath.startsWith('/') ? '' : '/'}${cleanPath}`;
}

export async function transcribeAudio(base64Audio: string): Promise<string> {
  const response = await fetch(buildUrl('/api/transcribe'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data: base64Audio })
  });
  if (!response.ok) {
    throw new Error(`STT HTTP error ${response.status}`);
  }
  const data = await response.json();
  return data.text || '';
}

export async function sendChatMessageStream(
  message: string,
  history: ChatMessage[],
  jlptLevel: JLPTLevel = 'N4',
  topic: string = 'Grammar & Practice',
  onToken: (token: string) => void,
  onComplete: (fullReply: string) => void,
  onError: (err: any) => void,
  teachingMode: 'bilingual' | 'immersion' = 'bilingual'
): Promise<void> {
  try {
    const formattedMessages = history.map(h => ({
      role: h.role,
      content: h.content
    }));

    if (message && (formattedMessages.length === 0 || formattedMessages[formattedMessages.length - 1].content !== message)) {
      formattedMessages.push({ role: 'user', content: message });
    }

    const response = await fetch(buildUrl('/api/chat'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: formattedMessages, jlptLevel, topic, teaching_mode: teachingMode })
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const reader = response.body?.getReader();
    if (!reader) throw new Error('No readable stream');
    const decoder = new TextDecoder();
    let fullText = '';
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataStr = line.slice(6).trim();
          if (!dataStr) continue;
          try {
            const parsed = JSON.parse(dataStr);
            if (parsed.token) {
              fullText += parsed.token;
              onToken(parsed.token);
            } else if (parsed.error) {
              onError(parsed.error);
            }
          } catch (e) {
            // raw string fallback
            fullText += dataStr;
            onToken(dataStr);
          }
        }
      }
    }
    onComplete(fullText);
  } catch (err) {
    onError(err);
  }
}

export function cleanTextForJapaneseSpeech(text: string): string {
  if (!text) return '';
  // 1. Replace 漢字[かんじ] with just かんじ (reading only once)
  let clean = text.replace(/([一-龯ヶ]+)\[([ぁ-んァ-ヶ]+)\]/g, '$2');
  
  // 2. Remove parenthetical readings like (かんじ) or (kanji) after Japanese words
  clean = clean.replace(/([\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]+)\s*[\(（][^\)］]+[\)）]/g, '$1');

  // 3. Remove Markdown syntax
  clean = clean.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '$1').replace(/[*#_~`>]/g, '');

  // 4. Extract Japanese lines
  const lines = clean.split('\n');
  const jpLines = lines.filter(line => {
    const trimmed = line.trim();
    if (!trimmed) return false;
    if (/^(Translation|English|Meaning|Explanation|Note):/i.test(trimmed)) return false;
    return /[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]/.test(trimmed);
  });

  return (jpLines.length > 0 ? jpLines.join(' ') : clean).trim();
}

export function speakJapanese(text: string, speed: number = 0.9): Promise<void> {
  // TTS disabled per user directive
  return Promise.resolve();
}

export async function fetchSettings(): Promise<AppSettings> {
  const response = await fetch(buildUrl('/api/settings'));
  if (!response.ok) {
    throw new Error(`Failed to fetch settings: ${response.status}`);
  }
  const data = await response.json();
  return {
    provider: data.provider || 'local',
    baseUrl: data.base_url || 'http://localhost:11434/v1',
    model: data.model || 'llama3.2',
    apiKey: data.api_key || '',
    customSystemPrompt: data.custom_system_prompt || '',
    speechRate: data.speech_rate ?? 0.9,
  };
}

export async function saveSettings(settings: Partial<AppSettings>): Promise<AppSettings> {
  const payload: Record<string, any> = {};
  if (settings.provider !== undefined) payload.provider = settings.provider;
  if (settings.baseUrl !== undefined) payload.base_url = settings.baseUrl;
  if (settings.model !== undefined) payload.model = settings.model;
  if (settings.apiKey !== undefined) payload.api_key = settings.apiKey;
  if (settings.customSystemPrompt !== undefined) payload.custom_system_prompt = settings.customSystemPrompt;
  if (settings.speechRate !== undefined) payload.speech_rate = settings.speechRate;

  const response = await fetch(buildUrl('/api/settings'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`Failed to save settings: ${response.status}`);
  }
  const data = await response.json();
  return {
    provider: data.provider || 'local',
    baseUrl: data.base_url || 'http://localhost:11434/v1',
    model: data.model || 'llama3.2',
    apiKey: data.api_key || '',
    customSystemPrompt: data.custom_system_prompt || '',
    speechRate: data.speech_rate ?? 0.9,
  };
}

export async function testLlmConnection(settings: Partial<AppSettings>): Promise<{ success: boolean; message: string }> {
  try {
    const response = await fetch(buildUrl('/api/chat'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        provider: settings.provider,
        base_url: settings.baseUrl,
        model: settings.model,
        api_key: settings.apiKey,
        messages: [{ role: 'user', content: 'Ping' }],
      }),
    });
    if (!response.ok) {
      const errText = await response.text();
      return { success: false, message: `HTTP ${response.status}: ${errText}` };
    }
    const reader = response.body?.getReader();
    if (reader) {
      const { value } = await reader.read();
      const text = new TextDecoder().decode(value);
      if (text.includes('"error":')) {
        const jsonMatch = text.match(/\{.*"error":\s*"(.*)"\}/);
        if (jsonMatch && jsonMatch[1]) {
          return { success: false, message: jsonMatch[1] };
        }
      }
    }
    return { success: true, message: 'Connection successful' };
  } catch (err: any) {
    return { success: false, message: err?.message || 'Connection failed' };
  }
}

export function createSpeechWebSocket(): WebSocket {
  const wsUrl = buildUrl('/ws/speech').replace(/^http/, 'ws');
  return new WebSocket(wsUrl);
}

// ── Session CRUD ─────────────────────────────────────────────────────────────

export async function fetchSessionById(sessionId: number): Promise<Session> {
  const response = await fetch(buildUrl(`/api/sessions/${sessionId}`));
  if (!response.ok) {
    throw new Error(`Failed to fetch session: ${response.status}`);
  }
  return response.json();
}

export async function fetchSessions(): Promise<Session[]> {
  const response = await fetch(buildUrl('/api/sessions'));
  if (!response.ok) {
    throw new Error(`Failed to fetch sessions: ${response.status}`);
  }
  return response.json();
}

export async function createSession(
  payload: Partial<Session> = {}
): Promise<Session> {
  const response = await fetch(buildUrl('/api/sessions'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`Failed to create session: ${response.status}`);
  }
  return response.json();
}

export async function updateSession(
  sessionId: number,
  payload: Partial<Session>
): Promise<Session> {
  const response = await fetch(buildUrl(`/api/sessions/${sessionId}`), {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`Failed to update session: ${response.status}`);
  }
  return response.json();
}

export async function deleteSession(sessionId: number): Promise<void> {
  const response = await fetch(buildUrl(`/api/sessions/${sessionId}`), {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error(`Failed to delete session: ${response.status}`);
  }
}

export async function searchDictionary(
  query: string = '',
  offset: number = 0,
  limit: number = 30
): Promise<DictionaryEntry[]> {
  const params = new URLSearchParams();
  if (query) params.append('q', query);
  params.append('offset', offset.toString());
  params.append('limit', limit.toString());

  const url = buildUrl(`/api/dictionary/search?${params.toString()}`);
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to search dictionary: ${response.status}`);
  }
  return response.json();
}

export async function analyzeDictionaryEntry(payload: {
  kanji: string;
  reading: string;
  meanings: string[];
}): Promise<{
  romaji: string;
  jlpt_level: string;
  nuance: string;
  example?: {
    japanese: string;
    hiragana: string;
    english: string;
  };
}> {
  const response = await fetch(buildUrl('/api/dictionary/analyze'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`Failed to analyze dictionary entry: ${response.status}`);
  }
  return response.json();
}




