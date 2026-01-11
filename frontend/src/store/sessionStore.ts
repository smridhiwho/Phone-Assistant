import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface SessionState {
  sessionId: string | null;
  initSession: () => void;
  clearSession: () => void;
}

const generateSessionId = (): string => {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

export const useSessionStore = create<SessionState>()(
  persist(
    (set, get) => ({
      sessionId: null,

      initSession: () => {
        const current = get().sessionId
        if (!current) {
          set({ sessionId: generateSessionId() })
        }
      },

      clearSession: () => {
        set({ sessionId: generateSessionId() })
      },
    }),
    {
      name: 'phone-assistant-session',
    }
  )
)
