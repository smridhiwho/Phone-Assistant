import { ChatMessage } from '../../types'
import { Message } from './Message'
import { TypingIndicator } from './TypingIndicator'

interface MessageListProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onSuggestionClick: (suggestion: string) => void;
}

export function MessageList({
  messages,
  isLoading,
  onSuggestionClick,
}: MessageListProps) {
  return (
    <div className="space-y-4 px-2">
      {messages.map((message) => (
        <Message
          key={message.id}
          message={message}
          onSuggestionClick={onSuggestionClick}
        />
      ))}
      {isLoading && <TypingIndicator />}
    </div>
  )
}
