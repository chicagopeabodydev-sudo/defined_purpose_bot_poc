# Plan: React UI + FastAPI Backend for Shiver Shack

## Context
The chatbot backend is feature-complete and fully tested (67 unit tests, 21 integration tests). The project spec calls for a visual chat UI resembling a locally-owned fast-food restaurant, but currently only a text REPL exists in `src/main.py`. This plan adds a FastAPI web API layer and a React frontend to fulfill the spec.

---

## New File Structure

```
defined_purpose_bot_poc/
├── requirements.txt                    # ADD: fastapi, uvicorn[standard]
├── src/
│   └── api.py                          # NEW: FastAPI app (greet + chat routes)
└── frontend/                           # NEW top-level directory
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── App.css
        ├── api/
        │   └── chatApi.js              # fetch wrapper for /api/greet + /api/chat
        ├── components/
        │   ├── MenuBoard/
        │   │   ├── MenuBoard.jsx       # chalk-style menu, reads menu.json directly
        │   │   └── MenuBoard.css
        │   ├── Employee/
        │   │   ├── Employee.jsx        # SAMN image + idle/thinking animations
        │   │   └── Employee.css
        │   ├── ChatPanel/
        │   │   ├── ChatPanel.jsx       # message list + input form
        │   │   └── ChatPanel.css
        │   ├── ChatMessage/
        │   │   ├── ChatMessage.jsx     # single message bubble (bot | user)
        │   │   └── ChatMessage.css
        │   └── SignTag/
        │       ├── SignTag.jsx         # decorative hand-written "Patio Open" sign
        │       └── SignTag.css
        └── assets/
            ├── samn.png               # copy of docs/Samn_in_parka_1.png
            ├── background.png         # copy of docs/shiver_shack_background.png
            └── menu.json              # copy of src/resources/menu.json
```

---

## Phase 1 — Backend API (`src/api.py`)

### Dependencies
Add to `requirements.txt`:
```
fastapi
uvicorn[standard]
```

### API Contract

**`GET /api/greet`** — called once on page load; creates a new `thread_id`
```json
// Response
{ "thread_id": "uuid-string", "message": "Welcome to Shiver Shack!..." }
```

**`POST /api/chat`** — one conversation turn
```json
// Request
{ "thread_id": "uuid-string", "message": "I want a burger" }
// Response
{ "message": "Added 1x Cheese Burrrrrrrrger...", "end_conversation": false }
```

### Key Implementation Details
- `load_dotenv()` and `logging.basicConfig()` called at top of `api.py` (mirrors `main.py` pattern, does NOT import `main.py`)
- Import `supervisor` from `src/agents/supervisor.py` after logging is configured
- Greet logic: read `src/resources/non_error_messages.json`, filter `messageType == "greeting"`, return random pick
- Chat logic: `supervisor.invoke({"messages": [...]}, config={"configurable": {"thread_id": ...}})`
  - Extract response from `result["structured_response"].response` if present, else `result["messages"][-1].content`
  - `end_conversation = "Goodbye" in last_message.content`
- CORS: allow `http://localhost:5173` (Vite dev server)
- Static file serving: `app.mount("/", StaticFiles(directory="frontend/dist", html=True))` — only if `frontend/dist/` exists, registered **after** all API routes
- Session note: `InMemorySaver` is process-local; single-worker only (`uvicorn` default)

---

## Phase 2 — React Frontend

### Visual Design Direction
- **Background**: `docs/shiver_shack_background.png` as full-viewport CSS `background-image`; CSS wood-plank fallback if needed
- **Layout**: Three-column scene — `[MenuBoard] [Employee + counter] [ChatPanel]`
- **Header**: "Shiver Shack" (display font) / "a calorie-neutral cafe" (smaller)
- **Fonts** (Google Fonts in `index.html`): `Permanent Marker` for header/board titles, `Cabin Sketch` for menu items, `Homemade Apple` for the taped sign
- **Palette** (CSS variables): `--wood-dark: #3d2b1f`, `--chalk-white: #f0ece0`, `--board-green: #2d4a2d`, `--accent: #e07b39`

### Component Responsibilities

| Component | Responsibility |
|---|---|
| `App.jsx` | Owns all state (`threadId`, `messages[]`, `isEnded`, `isLoading`); calls `/api/greet` on mount |
| `MenuBoard` | Renders `assets/menu.json` grouped by `itemType`; chalk-on-blackboard CSS |
| `Employee` | Renders `samn.png`; CSS idle animation; `employee--thinking` class while `isLoading` |
| `ChatPanel` | Scrollable message list + input form; disabled when `isEnded \|\| isLoading`; Enter to send |
| `ChatMessage` | Single bubble; `role` prop controls alignment/color; staggered `animationDelay` on appear |
| `SignTag` | Absolute-positioned aged-paper div with tape strips via `::before/::after`; decorative only |

### Session Management
- `thread_id` created server-side in `/api/greet`, stored in React state
- Lives only for the tab session — page refresh = new session (matches current REPL behavior)

### Vite Proxy (`vite.config.js`)
```js
server: { proxy: { '/api': 'http://localhost:8000' } }
```
All `chatApi.js` calls use relative URLs — no CORS issues in dev, identical behavior in production.

### Key Animations (CSS only, no extra libraries)
- **SAMN idle**: `translateY(-4px)` gentle float loop, 4s infinite
- **SAMN thinking**: `scaleY(0.97)` subtle pulse while `isLoading`
- **Message appear**: `opacity 0→1` + `translateY(8px→0)`, 250ms, staggered by `index * 60ms`
- **Send button**: `scale(0.93)` on `:active`

---

## Implementation Order

1. **Backend first** — add `fastapi`/`uvicorn` to requirements, create `src/api.py`, test with `curl` + FastAPI `/docs`
2. **Vite scaffold** — `npm create vite@latest frontend -- --template react`, add proxy, wire up `chatApi.js`, verify API round-trip in browser with plain HTML
3. **Copy assets** — `samn.png`, `background.png`, `menu.json` into `frontend/src/assets/`
4. **Component stubs** — create all 5 component files with minimal markup, wire props from `App.jsx`
5. **CSS and visual polish** — CSS variables, background, chalk board, SAMN animations, chat bubbles, fonts, sign tag
6. **End-state handling** — `end_conversation: true` disables input; 3-strike path tested end-to-end
7. **Production build** — `npm run build` in `frontend/`, verify FastAPI serves from `frontend/dist/`

---

## Critical Files

| File | Role |
|---|---|
| `src/main.py` | Reference for session/invocation pattern |
| `src/agents/supervisor.py` | Object imported by `api.py`; contains `InMemorySaver` and `OrderState` |
| `src/resources/non_error_messages.json` | Greeting source for `/api/greet` |
| `src/resources/menu.json` | Menu data copied to `frontend/src/assets/menu.json` |
| `docs/Samn_in_parka_1.png` | Employee image → copied to `frontend/src/assets/samn.png` |
| `docs/shiver_shack_background.png` | Background → copied to `frontend/src/assets/background.png` |

---

## Verification

1. `uvicorn src.api:app --reload --port 8000` starts without error
2. `curl http://localhost:8000/api/greet` returns `{ thread_id, message }`
3. `curl -X POST /api/chat` with a valid message returns a chatbot response
4. `npm run dev` in `frontend/` opens browser at `localhost:5173` with greeting visible
5. Full order flow: greet → order item → side → drink → "done" → summary displayed
6. Off-topic flow: 3 off-topic messages → farewell message → input disabled
7. `npm run build` + `uvicorn src.api:app --port 8000` → full app at `localhost:8000`
