import { create } from 'zustand'
import { ChatMessage, Phone } from '../types'

interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  comparePhones: Phone[];
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  setLoading: (loading: boolean) => void;
  addToCompare: (phone: Phone) => void;
  removeFromCompare: (phoneId: number) => void;
  clearCompare: () => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isLoading: false,
  comparePhones: [],

  addMessage: (message) => {
    const newMessage: ChatMessage = {
      ...message,
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
    }
    set((state) => ({
      messages: [...state.messages, newMessage],
    }))
  },

  setLoading: (loading) => {
    set({ isLoading: loading })
  },

  addToCompare: (phone) => {
    set((state) => {
      if (state.comparePhones.length >= 4) {
        return state // Max 4 phones
      }
      if (state.comparePhones.some((p) => p.id === phone.id)) {
        return state // Already in compare
      }
      return {
        comparePhones: [...state.comparePhones, phone],
      }
    })
  },

  removeFromCompare: (phoneId) => {
    set((state) => ({
      comparePhones: state.comparePhones.filter((p) => p.id !== phoneId),
    }))
  },

  clearCompare: () => {
    set({ comparePhones: [] })
  },

  clearMessages: () => {
    set({ messages: [] })
  },
}))
