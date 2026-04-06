---
name: project-overview-skill
description: Describes the goals and business rules of the project, and it is helpful in understanding the "big picture" of the project and its key steps.

---

# Project-Goal Summary
This project creates a chat ionterface to walk users through a fast-food order. If user chats go off topic, then the response should try to get the user back on topic. After too many inappropriate or off-topic user inputs the chat is ended.

## Key Steps
1. chatbot displays a greeting
2. users inputs an order entry, menu question, or off-topic text
3. Parse user input for:
  - IF an order entry THEN parse menu-item and quantity
  - ELSE IF a menu question THEN get the answer
  - ELSE is off-topic THEN use LLM to determine "off-topic-type"
4. Based on the result of step 3, use a tool to get the most appropriate4 response
5. return step 4 response to the user (UI)

## Desired Result
User successfully places and order that contains one or more menu items, and a summary of the transaction is presented at the end. If too many off-topic inputs from the user are received, then the conversation ends without a completed order.

## Tools
- summarize_complete_order
- summariaze_order_entry
- get_error_response
- answer_menu_question

## Models
- order_entry (represents a menu item and quantity)
- complete_order (array of order_entry items, total price, minutes to shiver)
- chat_response (text to display in the chat interface and, optionally, employee image)

## Resources
- menu and menu-items in a JSON format
- error messages in a JSON format
- "how-it-works" documentation

## UI
The background of the UI represents a fast-food restaurant counter with a menu board across the top, a counter that the employee stands behind, and a cach register on the counter. There is a chat interface is to the right of the employee. There is a default employee image displayed at the start of each chat, however responses to user chats may include alternative images to display for the employee.
