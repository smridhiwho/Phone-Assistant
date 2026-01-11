import { User, Bot } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { ChatMessage } from '../../types'
import { ProductCard } from '../products/ProductCard'
import { clsx } from 'clsx'

interface MessageProps {
  message: ChatMessage;
  onSuggestionClick: (suggestion: string) => void;
}

export function Message({ message, onSuggestionClick }: MessageProps) {
  const isUser = message.role === 'user'

  return (
    <div
      className={clsx('flex gap-3', {
        'justify-end': isUser,
      })}
    >
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
          <Bot className="w-4 h-4 text-primary" />
        </div>
      )}

      <div
        className={clsx('flex flex-col gap-3 max-w-[85%]', {
          'items-end': isUser,
        })}
      >
        <div
          className={clsx('rounded-2xl px-4 py-3', {
            'bg-primary text-primary-foreground': isUser,
            'bg-secondary': !isUser,
          })}
        >
          {isUser ? (
            <p>{message.content}</p>
          ) : (
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Products */}
        {message.products && message.products.length > 0 && (
          <div className="w-full">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {message.products.slice(0, 6).map((phone) => (
                <ProductCard key={phone.id} phone={phone} compact />
              ))}
            </div>
          </div>
        )}

        {message.suggestions && message.suggestions.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {message.suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => onSuggestionClick(suggestion)}
                className="px-3 py-1.5 text-xs rounded-full border border-border hover:bg-secondary transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
          <User className="w-4 h-4 text-primary-foreground" />
        </div>
      )}
    </div>
  )
}
