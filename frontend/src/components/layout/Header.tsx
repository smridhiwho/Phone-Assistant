import { Smartphone, Moon, Sun, RotateCcw } from 'lucide-react'
import { useChatStore } from '../../store/chatStore'
import { useSessionStore } from '../../store/sessionStore'

interface HeaderProps {
  isDark: boolean;
  onToggleDark: () => void;
}

export function Header({ isDark, onToggleDark }: HeaderProps) {
  const clearMessages = useChatStore((state) => state.clearMessages)
  const clearSession = useSessionStore((state) => state.clearSession)

  const handleNewChat = () => {
    clearMessages()
    clearSession()
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto max-w-6xl flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary text-primary-foreground">
            <Smartphone className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg font-semibold">Phone Assistant</h1>
            <p className="text-xs text-muted-foreground">AI-powered shopping helper</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleNewChat}
            className="flex items-center gap-2 px-3 py-2 text-sm rounded-lg hover:bg-secondary transition-colors"
            title="New conversation"
          >
            <RotateCcw className="w-4 h-4" />
            <span className="hidden sm:inline">New Chat</span>
          </button>

          <button
            onClick={onToggleDark}
            className="p-2 rounded-lg hover:bg-secondary transition-colors"
            title={isDark ? 'Light mode' : 'Dark mode'}
          >
            {isDark ? (
              <Sun className="w-5 h-5" />
            ) : (
              <Moon className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>
    </header>
  )
}
