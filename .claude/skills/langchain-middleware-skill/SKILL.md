---
name: langchain-middleware-skill
description: LangChain uses Middleware as a way to more tightly control what happens inside the agent. There are many built-in middleware components supplied by LangChain for common needs, and custom middleware can be created.

---

# LangChain Middleware

Middleware lets you intercept and control what happens inside the agent loop — before/after model calls, before/after tool calls, and at the start/end of the full agent run. Configure it via the `middleware` parameter of `create_agent`.

In this project, middleware is the mechanism for tracking off-topic inputs and terminating the conversation after too many are received. It is also used to manage the `@wrap_model_call` decorator for dynamic model selection (see `langchain-skill` for context, and Example 5 in `examples.md` for `@wrap_model_call` usage).

## Common Middleware Uses

- Tracking agent behavior with logging, analytics, and debugging.
- Transforming prompts, tool selection, and output formatting.
- Adding retries, fallbacks, and early termination logic.
- Applying rate limits, guardrails, and PII detection.

## Hook Types

The core agent loop calls a model, lets the model choose tools, and finishes when no more tools are called. Middleware exposes hooks before and after each step. There are two styles:

### Node-Style Hooks
Run sequentially at specific execution points. Use for logging, validation, and state updates.

| Hook | When it runs | Good for |
|---|---|---|
| `before_agent` | Once, before the first model call | Initializing custom state |
| `before_model` | Before each model call | Prompt injection, context trimming |
| `after_model` | After each model call | Logging responses, updating counters |
| `after_agent` | Once, after the last tool call | Order summary finalization, cleanup |

### Wrap-Style Hooks
Intercept execution and control when the inner handler is called. Use for retries, caching, and transformation.

| Hook | Wraps | Good for |
|---|---|---|
| `wrap_model_call` | Each model call | Retries, dynamic model selection, token tracking |
| `wrap_tool_call` | Each tool call | Error handling, caching, rate limiting |

## Best Practices

- Keep middleware focused — each component should do one thing well.
- Handle errors gracefully — don’t let middleware errors crash the agent.
- Use appropriate hook types:
    - Node-style for sequential logic (logging, validation)
    - Wrap-style for control flow (retry, fallback, caching)
- Clearly document any custom state properties.
- Unit test middleware independently before integrating.
- Consider execution order — place critical middleware first in the list.
- Use built-in middleware when possible.


## Additional Resources
- For usage examples, see [examples.md](examples.md)
- [Built-in Middleware documentation](https://docs.langchain.com/oss/python/langchain/middleware/built-in)
- [Custom Middleware documentation](https://docs.langchain.com/oss/python/langchain/middleware/custom)