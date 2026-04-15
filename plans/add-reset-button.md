# Plan: Add Reset Button to Chat UI

## Context
The chat interface tracks conversation state (messages, off_topic_count, order_items, isEnded) per `thread_id`. Users currently have no way to start fresh mid-session — they must reload the page. A Reset button in the bottom-right of the UI should discard the current thread, call `/api/greet` to receive a new `thread_id` and fresh greeting, and clear all frontend state.

Backend state (held in `InMemorySaver` keyed by `thread_id`) does not require a new endpoint — issuing a new `/api/greet` call naturally creates a new UUID `thread_id`, which means all LangGraph state (including `off_topic_count` and `order_items`) starts fresh on the new thread. The old thread is simply abandoned in memory.

---

## Files to Modify

| File | Change |
|---|---|
| `frontend/src/App.jsx` | Extract `initialize` logic, create `handleReset`, pass `onReset` to `ChatPanel` |
| `frontend/src/components/ChatPanel/ChatPanel.jsx` | Accept `onReset` prop, add Reset button element |
| `frontend/src/components/ChatPanel/ChatPanel.css` | Add `.chat-reset-btn` styles matching existing aesthetic |

---

## Implementation Steps

### 1. `frontend/src/App.jsx` — extract `initialize`, add `handleReset`

Hoist the `initialize` function out of the `useEffect` callback so it can be called by the reset handler. The `handleReset` function resets all state then re-calls `initialize`.

```jsx
// hoist initialize as a standalone async function in the component body
const initialize = async () => {
  setIsEnded(false)
  setMessages([])
  setThreadId(null)
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

useEffect(() => { initialize() }, [])   // still fires on mount

// pass to ChatPanel
<ChatPanel ... onReset={initialize} />
```

Note: `initialize` is redefined on every render; since it's only called imperatively (not as an effect dependency), this is fine without `useCallback`.

### 2. `frontend/src/components/ChatPanel/ChatPanel.jsx` — add Reset button

Accept `onReset` prop. Place a Reset button inside `chat-input-form`, to the right of the Send button (far-right of the bottom bar).

```jsx
function ChatPanel({ messages, onSend, isEnded, isLoading, onReset }) {
  ...
  return (
    <aside className="chat-panel">
      ...
      <form className="chat-input-form" onSubmit={handleSubmit}>
        <textarea ... />
        <button className="chat-send-btn" type="submit" ...>Send</button>
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
```

The button is `type="button"` to prevent form submission. It is only disabled during `isLoading` (not `isEnded`) — resetting an ended session is the primary use case.

### 3. `frontend/src/components/ChatPanel/ChatPanel.css` — style `.chat-reset-btn`

Match the existing design language (wood-dark background, chalk-white text) to distinguish it visually from the primary Send button while staying on-theme.

```css
.chat-reset-btn {
  background: var(--wood-dark);
  color: rgba(240, 236, 224, 0.6);
  border: none;
  border-left: 1px solid var(--wood-mid);
  padding: 0 0.85rem;
  font-family: var(--font-display);
  font-size: 0.75rem;
  letter-spacing: 1px;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
  flex-shrink: 0;
}

.chat-reset-btn:hover:not(:disabled) {
  background: #3a1f0f;
  color: var(--chalk-white);
}

.chat-reset-btn:active:not(:disabled) {
  background: var(--accent-dim);
}

.chat-reset-btn:disabled {
  color: rgba(240, 236, 224, 0.2);
  cursor: not-allowed;
}
```

---

## No Backend Changes Required

The `/api/greet` endpoint already creates a new UUID `thread_id`. LangGraph's `InMemorySaver` scopes all state to the `thread_id`, so the new thread starts with zero `off_topic_count`, empty `order_items`, and no prior messages. The old thread's data is abandoned in memory (consistent with the existing session model).

---

## Verification

1. Run the dev server: `cd frontend && npm run dev` (and `uvicorn src.api:app` for the backend)
2. Open the chat, send a few messages (including some off-topic)
3. Click **Reset** — UI should clear and show a fresh greeting; old thread state discarded
4. Verify Reset is available even when `isEnded=true` (after off-topic limit or order completion)
5. Verify Reset is disabled while a response is loading (`isLoading=true`)
6. Run unit tests: `pytest tests/unit/` (no backend changes, so tests should be unaffected)
