import { useState, useRef, useEffect } from 'react'
import ChatMessage from '../ChatMessage/ChatMessage'
import './ChatPanel.css'

function ChatPanel({ messages, onSend, isEnded, isLoading, onReset }) {
  const [input, setInput] = useState('')
  const listRef = useRef(null)

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight
    }
  }, [messages, isLoading])

  const handleSubmit = (e) => {
    e.preventDefault()
    const text = input.trim()
    if (!text) return
    onSend(text)
    setInput('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const disabled = isEnded || isLoading

  return (
    <aside className="chat-panel">
      <div className="chat-panel-header">
        <span className="chat-panel-title">Chat with SAMN</span>
        {isEnded && <span className="chat-ended-badge">Session Ended</span>}
      </div>

      <div className="chat-messages" ref={listRef}>
        {messages.map((msg, i) => (
          <ChatMessage key={i} role={msg.role} text={msg.text} index={i} />
        ))}

        {isLoading && (
          <div className="chat-typing" aria-label="SAMN is thinking">
            <span /><span /><span />
          </div>
        )}
      </div>

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <textarea
          className="chat-input"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={isEnded ? 'Session has ended.' : 'What would you like?'}
          disabled={disabled}
          rows={2}
          aria-label="Your message"
        />
        <button
          className="chat-send-btn"
          type="submit"
          disabled={disabled || !input.trim()}
          aria-label="Send message"
        >
          Send
        </button>
        <button
          className="chat-reset-btn"
          type="button"
          onClick={onReset}
          disabled={isLoading}
          aria-label="Reset conversation"
          title="Start over"
        >
          Reset
        </button>
      </form>
    </aside>
  )
}

export default ChatPanel
