import { useState, useEffect } from 'react'
import { greet, chat } from './api/chatApi'
import Employee from './components/Employee/Employee'
import ChatPanel from './components/ChatPanel/ChatPanel'
import './App.css'

function App() {
  const [threadId, setThreadId] = useState(null)
  const [messages, setMessages] = useState([])
  const [isEnded, setIsEnded] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    const initialize = async () => {
      setIsLoading(true)
      try {
        const { thread_id, message } = await greet()
        setThreadId(thread_id)
        setMessages([{ role: 'bot', text: message }])
      } catch {
        setMessages([{ role: 'bot', text: 'Welcome to Shiver Shack!' }])
      } finally {
        setIsLoading(false)
      }
    }
    initialize()
  }, [])

  const sendMessage = async (text) => {
    if (!text.trim() || isEnded || isLoading || !threadId) return

    setMessages(prev => [...prev, { role: 'user', text }])
    setIsLoading(true)

    try {
      const { message, end_conversation } = await chat(threadId, text)
      setMessages(prev => [...prev, { role: 'bot', text: message }])
      if (end_conversation) setIsEnded(true)
    } catch {
      setMessages(prev => [
        ...prev,
        { role: 'bot', text: 'Something went sideways. Try again.' },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app">
      <Employee isLoading={isLoading} />
      <ChatPanel
        messages={messages}
        onSend={sendMessage}
        isEnded={isEnded}
        isLoading={isLoading}
      />
    </div>
  )
}

export default App
