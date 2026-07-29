export type JLPTLevel = 'N5' | 'N4' | 'N3' | 'N2' | 'N1';

export type TabType = 'chat' | 'flashcards' | 'dictionary' | 'listening' | 'documents' | 'summaries' | 'stats';

export interface AppSettings {
  provider: 'local' | 'openai' | 'gemini';
  baseUrl: string;
  model: string;
  apiKey: string;
  customSystemPrompt: string;
  speechRate: number;
}


export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  audioText?: string;

  jlptLevel?: JLPTLevel;
}

export interface Session {
  id: number;
  title: string;
  messages?: ChatMessage[];
  message_count?: number;
  jlpt_level: JLPTLevel;
  teaching_mode: 'bilingual' | 'immersion';
  created_at: string;
  updated_at: string;
}

export interface TokenAnalysis {
  surface: string;
  reading?: string;
  pos: string;
  baseForm?: string;
  english?: string;
}

export interface SentenceAnalysis {
  tokens: TokenAnalysis[];
  grammarNotes?: string[];
  translation?: string;
}

export interface Flashcard {
  id: string;
  kanji: string;
  hiragana: string;
  romaji: string;
  english: string;
  jlpt: JLPTLevel;
  type: 'hiragana' | 'katakana' | 'kanji' | 'vocab';
  strokeCount?: number;
  radicals?: string[];
  examples: {
    japanese: string;
    reading: string;
    english: string;
  }[];
  mastered?: boolean;
}

export interface DictionaryEntry {
  id: string;
  kanji: string;
  reading: string;
  romaji: string;
  meanings: string[];
  pos: string[];
  jlpt: JLPTLevel;
  frequencyRank?: number;
  pitchAccent?: string;
  examples: {
    jp: string;
    reading: string;
    en: string;
  }[];
}


export interface ListeningExercise {
  id: string;
  title: string;
  level: JLPTLevel;
  japaneseText: string;
  reading: string;
  englishTranslation: string;
  audioSpeed: number;
  question: string;
  options: string[];
  correctIndex: number;
  explanation: string;
}

export interface UserStats {
  cardsMastered: number;
  cardsStudiedToday: number;
  chatSessionsCount: number;
  listeningCompleted: number;
  minutesSpent: number;
  level: JLPTLevel;
  savedVocabIds: string[];
}
