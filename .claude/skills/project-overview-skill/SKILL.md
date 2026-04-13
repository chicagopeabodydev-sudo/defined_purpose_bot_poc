---
name: project-overview-skill
description: Describes the goals and business rules of the project, and it is helpful in understanding the "big picture" of the project and its key steps.

---

# Project-Goal Summary
This project creates a chat interface to walk users through a fast-food order. The menu has "main" items, "sides" such af french fries, and "drinks". An order must contain at least one item, however it could include a main item, side, and drink. If user chats go off topic, meaning it is not a menu question nor menu-item order, then the response should try to get the user back on topic via an error message. After too many inappropriate or off-topic user inputs the chat is ended.

## Key Steps
1. Chatbot displays a greeting
2. Users inputs an order entry, menu question, or off-topic text
3. Parse user input for:
  - IF an order entry can be parsed THEN save the parsed menu-item and quantity
  - ELSE IF a menu question THEN get the answer
  - ELSE is off-topic THEN use LLM to determine "off-topic-type" to help determine the appropriate response
4. Based on the result of step 3, use a tool to get the most appropriate response
5. Return the response generated in step 4 to the user (UI)

## Parsing Order Item Errors
- IF a particular order-item has am amount greater than 5, THEN this is an error and should be clarified
- IF the item being ordered is not an entry in the menu.json resource, THEN this is an error

## Desired Result
User successfully places and order that contains one or more menu items, and a summary of the items ordered is presented at the end. If too many off-topic inputs from the user are received, then the conversation ends without a completed order.

## Tools
- summarize_complete_order
- summariaze_order_entry
- get_error_response
- get_non_error_response
- answer_menu_question

## Models
- order_entry (represents a menu item and quantity)
- complete_order (array of order_entry items, total price, minutes to shiver)
- chat_response (text to display in the chat interface and, optionally, employee image)

## Resources
- menu and menu-items in a JSON format
- error messages in a JSON format
- non-error messages in a JSON format
- "how-it-works" documentation

## Enumerated Objects

These are fixed-option values used across the project. Values must match exactly as shown — they are used as keys in JSON resources or as `Literal` type constraints in Python.

### supervisor-intent
Classifies each user message. Defined as a `Literal` in `src/agents/supervisor.py`.

| Value | Description |
|---|---|
| `order_entry` | User is placing or modifying an order |
| `menu_question` | User is asking about the menu |
| `off_topic` | User input is unrelated to ordering |

### off-topic-type
Key used to look up a response in `src/resources/off_topic_messages.json`.

| Value | Description |
|---|---|
| `sexual-content` | Crude or sexual language |
| `prompt-engineering` | Attempts to manipulate or re-prompt the AI |
| `not-understandable` | Input cannot be interpreted |
| `simply-unrelated` | Generic off-topic input unrelated to ordering |

### non-error-response-type
Key used to look up a response in `src/resources/non_error_messages.json`.

| Value | Description |
|---|---|
| `greeting` | Initial greeting at the start of the session |
| `next-step-only-main-ordered` | Prompt for a side or drink after only a Main is ordered |
| `next-step-main-and-side-ordered` | Prompt for a drink after a Main and Side are ordered |
| `next-step-generic` | Generic next-step prompt for any other order state |
| `ending-comment` | Closing message displayed after the final order summary |

### menu-item-type
The `itemType` field on each item in `src/resources/menu.json`.

| Value | Description |
|---|---|
| `Main` | Main entrée |
| `Side` | Side item (e.g., fries) |
| `Drink` | Beverage |

## UI
The background of the UI represents a fast-food restaurant counter with a menu board across the top, a counter that the employee stands behind, and a cach register on the counter. There is a chat interface is to the right of the employee. There is a default employee image displayed at the start of each chat, however responses to user chats may include alternative images to display for the employee.
