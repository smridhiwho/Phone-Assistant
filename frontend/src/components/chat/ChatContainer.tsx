import { useRef, useEffect } from 'react'
import { MessageList } from './MessageList'
import { MessageInput } from './MessageInput'
import { WelcomeMessage } from './WelcomeMessage'
import { useChatStore } from '../../store/chatStore'
import { useChat } from '../../hooks/useChat'

export function ChatContainer() {
  const { messages, isLoading } = useChatStore()
  const { sendMessage } = useChat()
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSendMessage = (message: string) => {
    sendMessage(message)
  }

  const handleSuggestionClick = (suggestion: string) => {
    sendMessage(suggestion)
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <div className="flex-1 overflow-y-auto pb-4">
        {messages.length === 0 ? (
          <WelcomeMessage onSuggestionClick={handleSuggestionClick} />
        ) : (
          <MessageList
            messages={messages}
            isLoading={isLoading}
            onSuggestionClick={handleSuggestionClick}
          />
        )}
        <div ref={bottomRef} />
      </div>

      <div className="sticky bottom-0 bg-background pt-4">
        <MessageInput onSend={handleSendMessage} disabled={isLoading} />
      </div>
    </div>
  )
}
