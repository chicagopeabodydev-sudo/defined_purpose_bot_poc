import './ChatMessage.css'

function ChatMessage({ role, text, index }) {
  return (
    <div
      className={`chat-message chat-message--${role}`}
      style={{ animationDelay: `${index * 60}ms` }}
    >
      {role === 'bot' && (
        <span className="chat-message-sender">SAMN</span>
      )}
      <p className="chat-message-text">{text}</p>
    </div>
  )
}

export default ChatMessage
