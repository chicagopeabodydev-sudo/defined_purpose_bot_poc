---
name: langchain-skill
description: LangChain is a python library that built around modular components that can be chained together (hence the name "LangChain") to create complex workflows. Use this skill to orchestrate the supervisor agent that routes between take_order, answer_menu_question, and get_error_response tools for the fast food order bot.

---

# When to use LangChain
Use LangChain to orchestrate the steps in responding to user input. This includes parsing user input for specific information, determining which tools may help, and generating a response based on a predefined structure. In this project, LangChain drives the supervisor agent that routes between `take_order`, `answer_menu_question`, and `get_error_response` tools.

## Steps to Creating and Using Agents
1. Define **"System Prompt(s)"**
2. Create **"Tools"** that can help the Agent integrate with external data or components
3. Create and configure **"Model(s)"** to use
4. Define **"Structured Output"** for predictable results

## Key Concepts
- **Agents**
- **Models**
- **Messages**
- **Tools**
- **System Prompt**
- **Structured Output**
- **Short-Term Memory**

### Two options to create Agents
1. Use `create_agent`
2. Use the model provider's package (for more control over the model configuration, initialize a model instance directly using the provider package)

### Static Model - set once for the Agent
- simplest solution
- **This project uses a static model approach** — the model is set once when the agent is created and does not change at runtime

### Dynamic Models - allow Agents to choose between models at runtime
- allows for more flexibility
- can choose best model based on runtime values
- requires middleware with `@wrap_model_call` decorator (see langchain-middleware-skill for details)

### Messages
Fundamental unit of context for models that represent the input and output of models, and they contain:
1. Role - Identifies the message type (e.g. system, user)
2. Content - Represents the actual content of the message (like text, images, audio, documents, etc.)
3. Metadata - Optional fields such as response information, message IDs, and token usage

### Tools
Give agents the ability to take actions
- Static Tools are supplied to Agents upfront
- Dynamic Tools are made available to Agents at runtime
  - Good if there are many tools

### System Prompt
You can shape how your agent approaches tasks by providing a prompt.
- can be either a string or SystemMessage
- model-provider prompt-features are accessed using SystemMessage

### Structured Output
Return output in a specific format via the response_format parameter.
- Uses a pydantic model to define the format
- ToolStrategy does not use the model to create the structured response
- ProviderStrategy leverages the model's native abilities to create the structured response

### Conversation History (Short-Term Memory)
Agents maintain conversation history automatically through message state, and this can use a custom state schema to remember specific information.
- Two ways to define custom state:
  1. Via middleware (preferred)
  2. Via state_schema when using create_agent
- Short-term Memory Strategies:
  1. Trim Messages - remove first or last messages (you can configure how many)
  2. Summarize Messages - summarize earlier messages and delete them, and then send the summary to the LLM
  3. Delete Messages - remove messages from LangGraph state permanently


## Additional Resources
- For usage examples, see [examples.md](examples.md)
- [Creating Basic Agents](https://docs.langchain.com/oss/python/langchain/quickstart)
- [Agents full documentation](https://docs.langchain.com/oss/python/langchain/agents)
- [Models full documentation](https://docs.langchain.com/oss/python/langchain/models)
- [Messages full documentation](https://docs.langchain.com/oss/python/langchain/messages)
- [Tools full documentation](https://docs.langchain.com/oss/python/langchain/tools)
- [Short-term Memory full documentation](https://docs.langchain.com/oss/python/langchain/short-term-memory)
- [Structured Output full documentation](https://docs.langchain.com/oss/python/langchain/structured-output)
