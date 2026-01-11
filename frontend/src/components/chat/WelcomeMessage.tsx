import { Smartphone, Camera, Battery, Gamepad2, DollarSign } from 'lucide-react'

interface WelcomeMessageProps {
  onSuggestionClick: (suggestion: string) => void;
}

const suggestions = [
  {
    icon: DollarSign,
    text: 'Best phones under Rs 30,000',
    color: 'text-green-500',
  },
  {
    icon: Camera,
    text: 'Best camera phones',
    color: 'text-blue-500',
  },
  {
    icon: Battery,
    text: 'Phones with best battery life',
    color: 'text-yellow-500',
  },
  {
    icon: Gamepad2,
    text: 'Best gaming phones',
    color: 'text-purple-500',
  },
]

export function WelcomeMessage({ onSuggestionClick }: WelcomeMessageProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] px-4">
      <div className="flex items-center justify-center w-16 h-16 mb-6 rounded-2xl bg-primary/10">
        <Smartphone className="w-8 h-8 text-primary" />
      </div>

      <h2 className="text-2xl font-bold text-center mb-2">
        Welcome to Phone Assistant
      </h2>
      <p className="text-muted-foreground text-center mb-8 max-w-md">
        I'm here to help you find the perfect smartphone. Ask me about phones,
        compare models, or get recommendations based on your needs.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion.text}
            onClick={() => onSuggestionClick(suggestion.text)}
            className="flex items-center gap-3 p-4 rounded-xl border border-border hover:bg-secondary transition-colors text-left"
          >
            <suggestion.icon className={`w-5 h-5 ${suggestion.color} flex-shrink-0`} />
            <span className="text-sm">{suggestion.text}</span>
          </button>
        ))}
      </div>

      <div className="mt-8 text-xs text-muted-foreground text-center">
        <p>Try asking:</p>
        <p className="mt-1 italic">
          "Compare Samsung S24 vs OnePlus 12" or "What is AMOLED display?"
        </p>
      </div>
    </div>
  )
}
