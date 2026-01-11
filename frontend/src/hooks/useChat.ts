import { useMutation } from '@tanstack/react-query'
import { chatApi } from '../services/api'
import { useChatStore } from '../store/chatStore'
import { useSessionStore } from '../store/sessionStore'
import { ChatRequest } from '../types'

export function useChat() {
  const { addMessage, setLoading } = useChatStore()
  const sessionId = useSessionStore((state) => state.sessionId)

  const sendMessageMutation = useMutation({
    mutationFn: async (message: string) => {
      if (!sessionId) {
        throw new Error('No session ID')
      }

      const request: ChatRequest = {
        session_id: sessionId,
        message,
      }

      return chatApi.sendMessage(request)
    },
    onMutate: (message) => {
      addMessage({
        role: 'user',
        content: message,
      })
      setLoading(true)
    },
    onSuccess: (data) => {
      addMessage({
        role: 'assistant',
        content: data.response,
        products: data.products,
        suggestions: data.suggestions,
      })
    },
    onError: (error) => {
      console.error('Chat error:', error)
      addMessage({
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        suggestions: ['Try a different question', 'Start a new conversation'],
      })
    },
    onSettled: () => {
      setLoading(false)
    },
  })

  return {
    sendMessage: sendMessageMutation.mutate,
    isLoading: sendMessageMutation.isPending,
    error: sendMessageMutation.error,
  }
}
