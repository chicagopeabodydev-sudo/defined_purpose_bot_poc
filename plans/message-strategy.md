# Plan: Improve `## Enumerated Objects` in project-overview-skill/SKILL.md

## Context
The `## Enumerated Objects` section documents fixed-option variables used across the project. The current section has stale/wrong values that don't match the codebase, and is missing the `supervisor-intent` enum entirely. SKILL.md is the authoritative source — JSON resources and code are updated to conform to it.

---

## Changes Required

### 1. Update `## Enumerated Objects` in SKILL.md
Replace lines 45–48 with a table-per-enum layout covering four enums.

**off-topic-type** (SKILL.md is master; JSON updated to match):

| Value | Description |
|---|---|
| `sexual-content` | Crude or sexual language |
| `prompt-engineering` | Attempts to manipulate or re-prompt the AI |
| `not-understandable` | Input cannot be interpreted |
| `simply-unrelated` | Generic off-topic input unrelated to ordering |

**supervisor-intent** (was missing from SKILL.md entirely):

| Value | Description |
|---|---|
| `order_entry` | User is placing or modifying an order |
| `menu_question` | User is asking about the menu |
| `off_topic` | User input is unrelated to ordering |

**non-error-response-type** (new authoritative values; JSON updated to match):

| Value | Description |
|---|---|
| `next-order-step` | Prompt the user toward the next item in their order |
| `confirm-order` | Confirm a selected item |
| `greeting` | Initial greeting at the start of the session |
| `ending-session` | Message displayed when the session is closing |

**menu-item-type** (already correct — no change needed):

| Value | Description |
|---|---|
| `Main` | Main entrée |
| `Side` | Side item (e.g., fries) |
| `Drink` | Beverage |

---

### 2. Rename and update `src/resources/error_messages.json` → `off_topic_messages.json`

**Rename:** `error_messages.json` → `off_topic_messages.json`

**Remap existing `errorType` values:**

| Current value | New value |
|---|---|
| `off-topic` | `simply-unrelated` |
| `sexual-content` | `sexual-content` (no change) |
| `sarcastic-response` | `simply-unrelated` |

**Add missing entries** (no current entry exists for these):

| Value | Action |
|---|---|
| `prompt-engineering` | Add new entry with placeholder message |
| `not-understandable` | Add new entry with placeholder message |

After update, the file must contain at least one entry per value: `sexual-content`, `prompt-engineering`, `not-understandable`, `simply-unrelated`.

**Also update** the filename reference in `src/tools/get_error_response.py`.

---

### 3. Update `src/resources/non_error_messages.json`

**Current problems:**
1. Inconsistent field keys — entry 1 uses `"messageType"`, entry 2 uses `"errorType"`. Normalize all to `"messageType"`.
2. Values (`apologetic`, `acknowldgement`) don't match the new SKILL.md `non-error-response-type` values and have no direct mapping — replace entirely.

**Replace all entries** so the file contains at least one entry per value:

| Value | Action |
|---|---|
| `greeting` | Add new entry with placeholder message |
| `confirm-order` | Add new entry with placeholder message |
| `next-order-step` | Add new entry with placeholder message |
| `ending-session` | Add new entry with placeholder message |

**Also update** any field key references in `src/tools/get_non_error_response.py`.

---

## Critical Files
- `.claude/skills/project-overview-skill/SKILL.md` — lines 45–48
- `src/resources/error_messages.json` → renamed to `off_topic_messages.json`
- `src/resources/non_error_messages.json` — values and field keys updated
- `src/tools/get_error_response.py` — filename reference updated
- `src/tools/get_non_error_response.py` — field key references updated

## Verification
After all changes:
1. All values in `off_topic_messages.json` match the four SKILL.md `off-topic-type` values; each has at least one entry
2. All `messageType` values in `non_error_messages.json` match the four SKILL.md `non-error-response-type` values; each has at least one entry
3. `get_error_response.py` loads `off_topic_messages.json` without error
4. Run unit tests for `get_error_response` and `get_non_error_response`
