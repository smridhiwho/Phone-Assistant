import { useState, useEffect } from 'react'
import { Header } from './components/layout/Header'
import { ChatContainer } from './components/chat/ChatContainer'
import { useSessionStore } from './store/sessionStore'

function App() {
  const [isDark, setIsDark] = useState(false)
  const initSession = useSessionStore((state) => state.initSession)

  useEffect(() => {
    initSession()

    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setIsDark(true)
      document.documentElement.classList.add('dark')
    }
  }, [initSession])

  const toggleDarkMode = () => {
    setIsDark(!isDark)
    document.documentElement.classList.toggle('dark')
  }

  return (
    <div className="min-h-screen bg-background">
      <Header isDark={isDark} onToggleDark={toggleDarkMode} />
      <main className="container mx-auto max-w-6xl px-4 py-6">
        <ChatContainer />
      </main>
    </div>
  )
}

export default App
