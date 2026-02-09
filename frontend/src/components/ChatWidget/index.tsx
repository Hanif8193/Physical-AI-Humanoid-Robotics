import React, { useState, useRef, useEffect } from 'react';
import useTextSelection from '../../hooks/useTextSelection';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: Array<{ chapter_slug: string; section: string; excerpt: string }>;
}

interface ChatWidgetProps {
  apiUrl?: string;
  chapterSlug?: string;
}

const API_URL = 'https://gleaming-joey-hanifmemon8193-7b25965a.koyeb.app/v1';

/**
 * ChatWidget — Floating RAG chat interface with citation display.
 * Supports global and chapter-scoped queries, plus text-selection context.
 */
export default function ChatWidget({ apiUrl = API_URL, chapterSlug }: ChatWidgetProps): JSX.Element {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const selectedText = useTextSelection();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const detectChapterSlug = (text: string): string | null => {
    const lower = text.toLowerCase();
    const map: Record<string, string> = {
      'chapter 1': 'ch01-intro-physical-ai',
      'ch1': 'ch01-intro-physical-ai',
      'ch01': 'ch01-intro-physical-ai',
      'chapter 2': 'ch02-ros2-fundamentals',
      'ch2': 'ch02-ros2-fundamentals',
      'ch02': 'ch02-ros2-fundamentals',
      'chapter 3': 'ch03-digital-twin',
      'ch3': 'ch03-digital-twin',
      'ch03': 'ch03-digital-twin',
      'chapter 4': 'ch04-isaac-platform',
      'ch4': 'ch04-isaac-platform',
      'ch04': 'ch04-isaac-platform',
      'chapter 5': 'ch05-vla',
      'ch5': 'ch05-vla',
      'ch05': 'ch05-vla',
      'chapter 6': 'ch06-capstone',
      'ch6': 'ch06-capstone',
      'ch06': 'ch06-capstone',
      // Urdu chapter references
      '\u0686\u06cc\u067e\u0679\u0631 1': 'ch01-intro-physical-ai',
      '\u0686\u06cc\u067e\u0679\u0631 \u0627\u06cc\u06a9': 'ch01-intro-physical-ai',
      '\u0686\u06cc\u067e\u0679\u0631 2': 'ch02-ros2-fundamentals',
      '\u0686\u06cc\u067e\u0679\u0631 \u062f\u0648': 'ch02-ros2-fundamentals',
      '\u0686\u06cc\u067e\u0679\u0631 3': 'ch03-digital-twin',
      '\u0686\u06cc\u067e\u0679\u0631 \u062a\u06cc\u0646': 'ch03-digital-twin',
      '\u0686\u06cc\u067e\u0679\u0631 4': 'ch04-isaac-platform',
      '\u0686\u06cc\u067e\u0679\u0631 5': 'ch05-vla',
      '\u0686\u06cc\u067e\u0679\u0631 6': 'ch06-capstone',
    };
    for (const [key, slug] of Object.entries(map)) {
      if (lower.includes(key)) return slug;
    }
    return null;
  };

  const translateQueryToEnglish = async (text: string): Promise<string> => {
    try {
      const res = await fetch(`${apiUrl}/translate/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      if (!res.ok) return text;
      const data = await res.json();
      return data.translated || text;
    } catch {
      return text;
    }
  };

  const translateToUrdu = async (text: string): Promise<string> => {
    try {
      const res = await fetch(`${apiUrl}/translate/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      if (!res.ok) return text;
      const data = await res.json();
      return data.translated || text;
    } catch {
      return text;
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    // Add placeholder assistant message
    setMessages((prev) => [...prev, { role: 'assistant', content: '', citations: [] }]);

    try {
      // Pre-translate Urdu queries to English for RAG embedding
      const englishQuery = await translateQueryToEnglish(userMessage);

      // Detect chapter reference in original or translated query
      const detectedChapter = detectChapterSlug(userMessage) || detectChapterSlug(englishQuery);
      const activeChapter = chapterSlug || detectedChapter;

      const endpoint = activeChapter
        ? `${apiUrl}/chat/chapter/${activeChapter}`
        : `${apiUrl}/chat`;

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: englishQuery,
          selected_context: selectedText || undefined,
        }),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const reader = response.body!.getReader();
      const decoder = new TextDecoder();
      let assistantContent = '';
      let citations: Message['citations'] = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const lines = decoder.decode(value).split('\n').filter(Boolean);
        for (const line of lines) {
          try {
            const event = JSON.parse(line);
            if (event.type === 'chunk') {
              assistantContent += event.content;
              setMessages((prev) => {
                const updated = [...prev];
                updated[updated.length - 1] = {
                  role: 'assistant',
                  content: assistantContent,
                  citations,
                };
                return updated;
              });
            } else if (event.type === 'citation') {
              citations = event.citations;
              setMessages((prev) => {
                const updated = [...prev];
                updated[updated.length - 1] = {
                  ...updated[updated.length - 1],
                  citations,
                };
                return updated;
              });
            } else if (event.type === 'done' && assistantContent) {
              // Auto-translate the full response to Urdu
              const urdu = await translateToUrdu(assistantContent);
              setMessages((prev) => {
                const updated = [...prev];
                updated[updated.length - 1] = {
                  role: 'assistant',
                  content: urdu,
                  citations,
                };
                return updated;
              });
            }
          } catch {
            // Skip malformed JSON lines
          }
        }
      }
    } catch (error) {
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          citations: [],
        };
        return updated;
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <button
        className="chat-widget-toggle"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle AI assistant"
        title="Ask the AI assistant"
      >
        {isOpen ? '✕' : '🤖'}
      </button>

      {isOpen && (
        <div className="chat-widget-panel" role="dialog" aria-label="AI Assistant">
          <div className="chat-widget-panel__header">
            🤖 Physical AI Assistant
            {selectedText && (
              <span style={{ fontSize: '0.75rem', opacity: 0.8 }}> · Context selected</span>
            )}
          </div>

          <div className="chat-widget-panel__messages">
            {messages.length === 0 && (
              <div style={{ color: 'var(--ifm-color-emphasis-600)', fontSize: '0.875rem', padding: '8px' }}>
                Ask me anything about the textbook! Select text for scoped questions.
              </div>
            )}
            {messages.map((msg, i) => {
              const isUrdu = /[\u0600-\u06FF]/.test(msg.content);
              return (
              <div key={i} className={`chat-message chat-message--${msg.role}${isUrdu ? ' rtl-content' : ''}`}>
                {msg.content || (isLoading && i === messages.length - 1 ? '⏳ Thinking...' : '')}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="chat-citation">
                    📚 Sources: {msg.citations.slice(0, 3).map((c) => `[${c.chapter_slug}]`).join(', ')}
                  </div>
                )}
              </div>
              );
            })}
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-widget-panel__input">
            <input
              type="text"
              placeholder={selectedText ? 'Ask about selected text...' : 'Ask a question...'}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              disabled={isLoading}
            />
            <button onClick={sendMessage} disabled={isLoading || !input.trim()}>
              {isLoading ? '...' : '→'}
            </button>
          </div>
        </div>
      )}
    </>
  );
}
