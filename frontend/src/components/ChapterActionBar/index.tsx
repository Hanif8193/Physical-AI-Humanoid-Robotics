import React, { useState } from 'react';

interface ChapterActionBarProps {
  chapterSlug: string;
  chapterContent: string;
  isAuthenticated: boolean;
  userId?: string;
  apiUrl?: string;
}

const API_URL = process.env.REACT_APP_API_URL || 'https://gleaming-joey-hanifmemon8193-7b25965a.koyeb.app/v1';

/**
 * ChapterActionBar — Shown only to authenticated users.
 * Provides [Personalize Chapter] and [Translate to Urdu] buttons.
 */
export default function ChapterActionBar({
  chapterSlug,
  chapterContent,
  isAuthenticated,
  userId,
  apiUrl = API_URL,
}: ChapterActionBarProps): JSX.Element | null {
  const [isPersonalizing, setIsPersonalizing] = useState(false);
  const [isTranslating, setIsTranslating] = useState(false);
  const [personalizedContent, setPersonalizedContent] = useState<string | null>(null);
  const [translatedContent, setTranslatedContent] = useState<string | null>(null);
  const [showOriginal, setShowOriginal] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Only render for authenticated users (Constitution Principle VI)
  if (!isAuthenticated) return null;

  const handlePersonalize = async () => {
    setIsPersonalizing(true);
    setError(null);
    try {
      const response = await fetch(`${apiUrl}/personalize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('session_token')}`,
        },
        body: JSON.stringify({
          chapter_slug: chapterSlug,
          user_id: userId,
          content: chapterContent,
        }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Personalization failed');
      }

      const data = await response.json();
      setPersonalizedContent(data.personalized_content);
      setShowOriginal(false);
    } catch (e: any) {
      setError(e.message || 'Failed to personalize chapter');
    } finally {
      setIsPersonalizing(false);
    }
  };

  const handleTranslate = async () => {
    // Check cache first
    const cacheKey = `translation:${chapterSlug}:ur`;
    const cached = sessionStorage.getItem(cacheKey);
    if (cached) {
      setTranslatedContent(cached);
      setShowOriginal(false);
      return;
    }

    setIsTranslating(true);
    setError(null);
    try {
      const response = await fetch(`${apiUrl}/translate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chapter_slug: chapterSlug,
          target_language: 'ur',
          content: chapterContent,
        }),
      });

      if (!response.ok) throw new Error('Translation failed');

      const data = await response.json();
      setTranslatedContent(data.translated_content);
      sessionStorage.setItem(cacheKey, data.translated_content);
      setShowOriginal(false);
    } catch (e: any) {
      setError(e.message || 'Failed to translate chapter');
    } finally {
      setIsTranslating(false);
    }
  };

  const handleShowOriginal = () => {
    setShowOriginal(true);
    setPersonalizedContent(null);
    setTranslatedContent(null);
  };

  const activeContent = showOriginal ? null : (personalizedContent || translatedContent);

  return (
    <div>
      <div className="chapter-action-bar">
        <button
          className="chapter-action-bar__button"
          onClick={handlePersonalize}
          disabled={isPersonalizing}
          title="Adapt this chapter to your background"
        >
          {isPersonalizing ? '⏳ Personalizing...' : '🎯 Personalize Chapter'}
        </button>

        <button
          className="chapter-action-bar__button"
          onClick={handleTranslate}
          disabled={isTranslating}
          title="Translate to Urdu"
        >
          {isTranslating ? '⏳ Translating...' : '🌐 Translate to Urdu'}
        </button>

        {(personalizedContent || translatedContent) && !showOriginal && (
          <button
            className="chapter-action-bar__button"
            onClick={handleShowOriginal}
            title="Show original content"
          >
            ↩ Show Original
          </button>
        )}
      </div>

      {error && (
        <div style={{ color: 'red', fontSize: '0.875rem', padding: '4px 0' }}>
          ⚠️ {error}
        </div>
      )}

      {activeContent && (
        <div
          className={translatedContent && !showOriginal ? 'rtl-content' : ''}
          dangerouslySetInnerHTML={{ __html: activeContent }}
        />
      )}
    </div>
  );
}
