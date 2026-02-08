/**
 * TranslationCache — Client-side session storage cache for chapter translations.
 * Keyed by `chapter_slug + language_code`. TTL = browser session.
 */

const CACHE_PREFIX = 'phy-ai-translation:';

export interface CacheEntry {
  content: string;
  timestamp: number;
  chapter_slug: string;
  language: string;
}

export function getCachedTranslation(chapterSlug: string, language: string): string | null {
  const key = `${CACHE_PREFIX}${chapterSlug}:${language}`;
  try {
    const item = sessionStorage.getItem(key);
    if (!item) return null;
    const entry: CacheEntry = JSON.parse(item);
    return entry.content;
  } catch {
    return null;
  }
}

export function setCachedTranslation(chapterSlug: string, language: string, content: string): void {
  const key = `${CACHE_PREFIX}${chapterSlug}:${language}`;
  const entry: CacheEntry = {
    content,
    timestamp: Date.now(),
    chapter_slug: chapterSlug,
    language,
  };
  try {
    sessionStorage.setItem(key, JSON.stringify(entry));
  } catch {
    // Session storage full — silently fail
  }
}

export function clearTranslationCache(chapterSlug?: string): void {
  if (chapterSlug) {
    // Clear specific chapter
    for (let i = sessionStorage.length - 1; i >= 0; i--) {
      const key = sessionStorage.key(i);
      if (key?.startsWith(`${CACHE_PREFIX}${chapterSlug}`)) {
        sessionStorage.removeItem(key);
      }
    }
  } else {
    // Clear all translations
    for (let i = sessionStorage.length - 1; i >= 0; i--) {
      const key = sessionStorage.key(i);
      if (key?.startsWith(CACHE_PREFIX)) {
        sessionStorage.removeItem(key);
      }
    }
  }
}
