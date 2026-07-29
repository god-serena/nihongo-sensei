import { Flashcard, DictionaryEntry, ListeningExercise } from '../types';

export const INITIAL_FLASHCARDS: Flashcard[] = [
  {
    id: 'fc-1',
    kanji: '日',
    hiragana: 'ひ / にち',
    romaji: 'hi / nichi',
    english: 'Sun, Day, Japan',
    jlpt: 'N5',
    type: 'kanji',
    strokeCount: 4,
    radicals: ['日 (sun)'],
    examples: [
      { japanese: '日本に行きます。', reading: 'にほん に いきます。', english: 'I am going to Japan.' },
      { japanese: '日曜日', reading: 'にちようび', english: 'Sunday' }
    ]
  },
  {
    id: 'fc-2',
    kanji: '本',
    hiragana: 'ほん',
    romaji: 'hon',
    english: 'Book, Origin, Real',
    jlpt: 'N5',
    type: 'kanji',
    strokeCount: 5,
    radicals: ['木 (tree)', '一 (one)'],
    examples: [
      { japanese: '本を読みます。', reading: 'ほん を よみます。', english: 'I read a book.' },
      { japanese: '山本さん', reading: 'やまもとさん', english: 'Mr./Ms. Yamamoto' }
    ]
  },
  {
    id: 'fc-3',
    kanji: '人',
    hiragana: 'ひと / じん',
    romaji: 'hito / jin',
    english: 'Person, Human',
    jlpt: 'N5',
    type: 'kanji',
    strokeCount: 2,
    radicals: ['人 (person)'],
    examples: [
      { japanese: 'あの人は誰ですか？', reading: 'あの ひと は だれ ですか？', english: 'Who is that person?' },
      { japanese: '日本人', reading: 'にほんじん', english: 'Japanese person' }
    ]
  },
  {
    id: 'fc-4',
    kanji: '学',
    hiragana: 'まな・ぶ / がく',
    romaji: 'mana-bu / gaku',
    english: 'Study, Learn, Science',
    jlpt: 'N5',
    type: 'kanji',
    strokeCount: 8,
    radicals: ['子 (child)'],
    examples: [
      { japanese: '大学で勉強します。', reading: 'だいがく で べんきょう します。', english: 'I study at university.' },
      { japanese: '学生です。', reading: 'がくせい です。', english: 'I am a student.' }
    ]
  },
  {
    id: 'fc-5',
    kanji: '食',
    hiragana: 'た・べる / しょく',
    romaji: 'ta-beru / shoku',
    english: 'Eat, Food',
    jlpt: 'N5',
    type: 'kanji',
    strokeCount: 9,
    radicals: ['食 (eat)'],
    examples: [
      { japanese: '朝ご飯を食べます。', reading: 'あさごはん を たべます。', english: 'I eat breakfast.' },
      { japanese: '食堂', reading: 'しょくどう', english: 'Cafeteria' }
    ]
  },
  {
    id: 'fc-6',
    kanji: '飲',
    hiragana: 'の・む / いん',
    romaji: 'no-mu / in',
    english: 'Drink',
    jlpt: 'N5',
    type: 'kanji',
    strokeCount: 12,
    radicals: ['食 (eat)', '欠 (lack)'],
    examples: [
      { japanese: 'お茶を飲みますか？', reading: 'おちゃ を のみますか？', english: 'Would you like to drink tea?' },
      { japanese: '飲み物', reading: 'のみもの', english: 'Beverage / Drink' }
    ]
  },
  {
    id: 'fc-7',
    kanji: '気',
    hiragana: 'き',
    romaji: 'ki',
    english: 'Spirit, Mind, Atmosphere',
    jlpt: 'N5',
    type: 'kanji',
    strokeCount: 6,
    radicals: ['气 (steam)'],
    examples: [
      { japanese: 'お元気ですか？', reading: 'おげんき ですか？', english: 'How are you?' },
      { japanese: '天気がいいですね。', reading: 'てんき が いいですね。', english: 'The weather is nice, isn’t it?' }
    ]
  },
  {
    id: 'fc-8',
    kanji: '旅',
    hiragana: 'たび / りょ',
    romaji: 'tabi / ryo',
    english: 'Trip, Travel',
    jlpt: 'N4',
    type: 'kanji',
    strokeCount: 10,
    radicals: ['方 (direction)'],
    examples: [
      { japanese: '旅行が好きです。', reading: 'りょこう が すきです。', english: 'I like traveling.' },
      { japanese: '一人旅', reading: 'ひとりたび', english: 'Solo journey' }
    ]
  }
];

export const INITIAL_DICTIONARY: DictionaryEntry[] = [
  {
    id: 'dict-1',
    kanji: '琴',
    reading: 'こと',
    romaji: 'koto',
    meanings: ['Koto (traditional Japanese 13-string zither)', 'Lute', 'Music'],
    pos: ['Noun'],
    jlpt: 'N2',
    frequencyRank: 1200,
    pitchAccent: '② [こ・と]',
    examples: [
      { jp: '琴の音色が美しく響く。', reading: 'こと の ねいろ が うつくしく ひびく。', en: 'The timbre of the koto echoes beautifully.' }
    ]
  },
  {
    id: 'dict-2',
    kanji: '先生',
    reading: 'せんせい',
    romaji: 'sensei',
    meanings: ['Teacher', 'Master', 'Doctor', 'Instructor'],
    pos: ['Noun', 'Honorific suffix'],
    jlpt: 'N5',
    frequencyRank: 150,
    pitchAccent: '③ [せ・ん・せ・い]',
    examples: [
      { jp: '日本語の先生に質問する。', reading: 'にほんご の せんせい に しつもん する。', en: 'Ask a question to the Japanese teacher.' }
    ]
  },
  {
    id: 'dict-3',
    kanji: '言葉',
    reading: 'ことば',
    romaji: 'kotoba',
    meanings: ['Language', 'Word', 'Dialect', 'Expression'],
    pos: ['Noun'],
    jlpt: 'N4',
    frequencyRank: 320,
    pitchAccent: '③ [こ・と・ば]',
    examples: [
      { jp: '優しい言葉をかける。', reading: 'やさしい ことば を かける。', en: 'Speak kind words.' }
    ]
  },
  {
    id: 'dict-4',
    kanji: '勉強',
    reading: 'べんきょう',
    romaji: 'benkyou',
    meanings: ['Study', 'Diligence', 'Discount (colloquial)'],
    pos: ['Noun', 'Suru-verb'],
    jlpt: 'N5',
    frequencyRank: 210,
    pitchAccent: '⓪ [べ・ん・きょ・う]',
    examples: [
      { jp: '毎日図書館で勉強します。', reading: 'まいにち としょかん で べんきょう します。', en: 'I study at the library every day.' }
    ]
  },
  {
    id: 'dict-5',
    kanji: '朱印',
    reading: 'しゅいん',
    romaji: 'shuin',
    meanings: ['Red seal', 'Vermilion stamp given at Japanese temples'],
    pos: ['Noun'],
    jlpt: 'N2',
    frequencyRank: 2800,
    pitchAccent: '⓪ [しゅ・い・ん]',
    examples: [
      { jp: '神社で朱印帳に朱印をもらう。', reading: 'じんじゃ で しゅいんちょう に しゅいん を もらう。', en: 'Collect a red seal stamp in a notebook at a shrine.' }
    ]
  }
];

export const INITIAL_LISTENING: ListeningExercise[] = [
  {
    id: 'listen-1',
    title: 'Ordering Coffee in Tokyo',
    level: 'N5',
    japaneseText: 'いらっしゃいませ！ご注文はお決まりですか？アイスカフェラテを一つお願いします。',
    reading: 'いらっしゃいませ！ ごちゅうもん は おきまり ですか？ あいす かふぇらて を ひとつ おねがいします。',
    englishTranslation: 'Welcome! Have you decided on your order? One iced cafe latte, please.',
    audioSpeed: 1.0,
    question: 'What item did the customer order?',
    options: ['Hot Green Tea', 'Iced Cafe Latte', 'Water with Lemon', 'Iced Americano'],
    correctIndex: 1,
    explanation: 'The customer requested "アイスカフェラテ" (Iced Cafe Latte) with "一つお願いします" (One, please).'
  },
  {
    id: 'listen-2',
    title: 'Train Station Announcement',
    level: 'N4',
    japaneseText: 'まもなく２番線に電車が参ります。黄色い線の内側までお下がりください。',
    reading: 'まもなく にばんせん に でんしゃ が まいります。 きいろい せん の うちがわ まで おさがり ください。',
    englishTranslation: 'A train will arrive on track 2 shortly. Please step back behind the yellow line.',
    audioSpeed: 0.9,
    question: 'Where should passengers stand?',
    options: ['On track 2', 'Behind the yellow line', 'Near the ticket gate', 'Next to the train door'],
    correctIndex: 1,
    explanation: '"黄色い線の内側" means inside/behind the yellow warning line.'
  }
];

export const PARTICLE_GUIDE = [
  { particle: 'は (wa)', role: 'Topic Marker', example: '私は学生です (As for me, I am a student)', note: 'Highlights what comes AFTER the particle.' },
  { particle: 'が (ga)', role: 'Subject Marker', example: '雨が降っています (Rain is falling)', note: 'Focuses on the SUBJECT performing the action.' },
  { particle: 'を (o)', role: 'Direct Object', example: '寿司を食べます (I eat sushi)', note: 'Marks the recipient of transitive action.' },
  { particle: 'に (ni)', role: 'Target / Time / Location', example: '7時に学校に行きます (Go to school at 7 o’clock)', note: 'Indicates specific point in time or direction.' },
  { particle: 'で (de)', role: 'Means / Location of Action', example: '箸でラーメンを食べます (Eat ramen with chopsticks)', note: 'Indicates tool, method, or active location.' },
  { particle: 'と (to)', role: 'Together with / And', example: '友達と話す (Talk with a friend)', note: 'Connects nouns directly or marks company.' }
];
