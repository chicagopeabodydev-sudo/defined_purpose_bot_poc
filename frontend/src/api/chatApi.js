const BASE = '/api'

export async function greet() {
  const res = await fetch(`${BASE}/greet`)
  if (!res.ok) throw new Error(`Greet failed: ${res.status}`)
  return res.json()
}

export async function chat(threadId, message) {
  const res = await fetch(`${BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ thread_id: threadId, message }),
  })
  if (!res.ok) throw new Error(`Chat failed: ${res.status}`)
  return res.json()
}
