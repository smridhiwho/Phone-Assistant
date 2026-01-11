import { Bot } from 'lucide-react'

export function TypingIndicator() {
  return (
    <div className="flex gap-3">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
        <Bot className="w-4 h-4 text-primary" />
      </div>

      <div className="bg-secondary rounded-2xl px-4 py-3">
        <div className="flex gap-1">
          <span className="w-2 h-2 rounded-full bg-muted-foreground/50 typing-dot" />
          <span className="w-2 h-2 rounded-full bg-muted-foreground/50 typing-dot" />
          <span className="w-2 h-2 rounded-full bg-muted-foreground/50 typing-dot" />
        </div>
      </div>
    </div>
  )
}
