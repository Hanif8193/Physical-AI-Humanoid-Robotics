import { useState, useEffect } from 'react';

/**
 * useTextSelection — Captures user's text selection on the page.
 * Selected text is forwarded to the RAG chat as scoped context.
 */
export default function useTextSelection(): string {
  const [selectedText, setSelectedText] = useState('');

  useEffect(() => {
    const handleSelectionChange = () => {
      const selection = window.getSelection();
      if (selection && selection.toString().trim().length > 10) {
        setSelectedText(selection.toString().trim());
      } else if (!selection || selection.toString().trim().length === 0) {
        setSelectedText('');
      }
    };

    document.addEventListener('selectionchange', handleSelectionChange);
    return () => document.removeEventListener('selectionchange', handleSelectionChange);
  }, []);

  return selectedText;
}
