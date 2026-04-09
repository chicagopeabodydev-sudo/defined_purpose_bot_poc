---
name: project-goals-skill
description: Describes the architectural goals of the project and what measures should be used to determine success.

---

# Summary
This project creates a chat interface to walk users through a fast-food order. An overview of the project and its key steps can be found in ../project-overview-skill.

## Limit What Users Can Do
Users are being guided down the process of ordering a meal. Users should be limited to **two valid tasks**:
1. Completing a step in the meal ordering process, such as:
    - Adding one or more menu items
    - Updating or deleting already ordered items
    - Indicating ordering is complete
2. Asking questions about the menu or how the claim of calorie-neutral works.

### Everything else is considered "off-topic" and handled the same way:
1. Determine the off-topic-type.
2. Generate an appropriate response for the off-topic-type that tries to return to the food ordering process.
3. If greater than the defined off-topic limit, end the chat conversation with the user.

## Limit LLM calls and Token Usage
This goal is achieved by not calling the LLM to generate the text of every response. In many cases how to respond can be determined when parsing the user's input. In these cases, a predefined response will be selected from the system's resources in place of the LLM call.

### When TO USE the LLM/Model
1. To parse user input and place it into one of three buckets:
    a. successfully parsing an order entry
    b. identifying a valid menu question
    c. based on semantics/text what off-topic-type is it
2. To synthesize order summaries

### When NOT to use the LLM/Model 
1. To generate the text of final responses (these will be selected from a resource file of predefined responses)

## Success Measures
1. User completes a food order and agrees to the summary presented at the end.
2. Bonus points if this is done in less than 4 total chats back and forth.
3. Users should be cut off after too many off-topic inputs (based on any off-topic-tolerance settings)

## Additional Resources
[Project overview](../project-overview-skill)
