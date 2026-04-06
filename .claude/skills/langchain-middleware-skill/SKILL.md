---
name: langchain-middleware-skill
description: LangChain uses Middleware as a way to more tightly control what happens inside the agent. There are many built-in middleware components suppl;ied by LangChain for common needs, and custom middleware can be created.

---

## Common Middleware Uses:
- Tracking agent behavior with logging, analytics, and debugging.
- Transforming prompts, tool selection, and output formatting.
- Adding retries, fallbacks, and early termination logic.
- Applying rate limits, guardrails, and PII detection.

### Middleware Hooks
The core agent loop involves calling a model, letting the model choose tools to execute, and then finishing when it calls no more tools. Middleware exposes "hooks" before and after each of those steps.

### Configuring Middleware
- "middleware" setting of an Agent can be set to an array of Middleware components

### 2 types of Hooks
1. Node-Style Hooks - run sequentially at specific execution points. Use for logging, validation, and state updates.
  - before_agent - runs after the request but before the model is invoked (only called once)
  - before_model - runs prior to using models
  - after_model - runs after the model has been invoked
  - after_agent - runs after all tools have been used and no more calls will be made to the model (only called once)
2. Wrap-Style Hooks - intercept execution and control when the handler is called. Use for retries, caching, and transformation.
  - wrap_model_call - around each model call
  - wrap_tool_call - around each tool call

### Middleware Best Practices
- Keep middleware focused - each should do one thing well
- Handle errors gracefully - don’t let middleware errors crash the agent
- Use appropriate hook types:
  - Node-style for sequential logic (logging, validation)
  - Wrap-style for control flow (retry, fallback, caching)
- Clearly document any custom state properties
- Unit test middleware independently before integrating
- Consider execution order - place critical middleware first in the list
- Use built-in middleware when possible


## Additional Resources
- For usage examples, see [examples.md](examples.md)
- [Built-in Middleware documentation](https://docs.langchain.com/oss/python/langchain/middleware/built-in)
- [Custom Middleware documentation](https://docs.langchain.com/oss/python/langchain/middleware/custom)