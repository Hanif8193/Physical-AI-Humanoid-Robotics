import React, { createContext, useContext, useState, useEffect } from 'react';
import ChatWidget from '../components/ChatWidget';

// Auth context
interface AuthState {
  isAuthenticated: boolean;
  userId?: string;
  token?: string;
  login: (token: string, userId: string) => void;
  logout: () => void;
}

export const AuthContext = createContext<AuthState>({
  isAuthenticated: false,
  login: () => {},
  logout: () => {},
});

export function useAuth() {
  return useContext(AuthContext);
}

/**
 * Root swizzle — wraps entire Docusaurus app with:
 * 1. Auth context (from localStorage session)
 * 2. ChatWidget (floating, on all pages)
 */
export default function Root({ children }: { children: React.ReactNode }): JSX.Element {
  const [authState, setAuthState] = useState<Omit<AuthState, 'login' | 'logout'>>({
    isAuthenticated: false,
  });

  useEffect(() => {
    // Restore session from localStorage on mount (client-side only)
    if (typeof window === 'undefined') return;
    const token = localStorage.getItem('session_token');
    const userId = localStorage.getItem('user_id');
    if (token && userId) {
      setAuthState({ isAuthenticated: true, userId, token });
    }
  }, []);

  const login = (token: string, userId: string) => {
    localStorage.setItem('session_token', token);
    localStorage.setItem('user_id', userId);
    setAuthState({ isAuthenticated: true, userId, token });
  };

  const logout = () => {
    localStorage.removeItem('session_token');
    localStorage.removeItem('user_id');
    setAuthState({ isAuthenticated: false });
  };

  return (
    <AuthContext.Provider value={{ ...authState, login, logout }}>
      {children}
      <ChatWidget />
    </AuthContext.Provider>
  );
}
