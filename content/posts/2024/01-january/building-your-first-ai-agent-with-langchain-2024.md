---
title: "Building Your First AI Agent with LangChain in 2024"
subtitle: "A step-by-step developer guide to writing an autonomous agent with real-world tool execution."
date: "2024-01-16"
author: "Shantanu Vishwanadha"
authorUrl: "https://substack.com/@thecoderpanda"
tags: ["tutorials", "langchain", "ai-agents", "python", "software-engineering"]
seoTitle: "Build an AI Agent with LangChain: 2024 Tutorial"
seoDescription: "Learn how to build your first autonomous AI agent with LangChain and Python. Step-by-step developer tutorial with code examples, tool use, and best practices."
featuredImage: "https://images.unsplash.com/photo-1555066931-4365d14bab8c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
imageAlt: "A clean high-resolution close-up of high-contrast colorful code displayed on a modern dark mode code editor on a wide screen"
category: "tutorials"
readingTime: "5 min read"
slug: "building-your-first-ai-agent-with-langchain-2024"
---

# Building Your First AI Agent with LangChain in 2024

> **TL;DR:** Ready to move past basic chatbot APIs? In this comprehensive tutorial, we’ll build an autonomous AI agent from scratch using LangChain and Python, equipping it with custom tools to execute real-world calculations and system operations.

So, you’ve spent the last year playing with basic OpenAI chat completions. You know how to send a prompt, you know how to parse the JSON response, and you’ve probably built a simple wrapper or two that formats text. But deep down, you know that’s just glorified templating. You’re ready for the real deal: building an autonomous, self-correcting agent that can decide which tools to use, write and execute code, and solve multi-step problems without you holding its hand.

In this developer guide, we are going to build exactly that. We’ll use LangChain and Python to construct an autonomous agent that can read user queries, determine if it needs external tools, execute those tools, and synthesize a final response. And we're going to build it clean—no hacky, fragile regex parses. We'll be writing our code inside a workspace file named `./agent.py`, setting up our configuration in `./.env`, and managing dependencies via `./requirements.txt`. Grab a coffee, open your terminal, and let's build some digital life.

## Setting Up Your Workspace Environment

Before we write a single line of Python, we need to set up a clean, isolated environment to ensure we don't pollute our system packages. Let's create our project directory structure. We will manage our dependencies inside the file `./requirements.txt` and store our API secrets securely inside `./.env`. 

First, let’s list the libraries we need. We will be using `langchain`, `langchain-openai` for model access, and `python-dotenv` to load our secret environment variables. Open `./requirements.txt` and populate it with the following dependencies:

```text
langchain>=0.1.0
langchain-openai>=0.0.2
python-dotenv>=1.0.0
```

Once your `./requirements.txt` is ready, create your configuration file `./.env` in the same directory. This file will store your API keys. Make sure you replace the placeholder with your actual OpenAI API key:

```env
OPENAI_API_KEY=sk-proj-yourActualKeyGoesHere
```

*(Note: Always add `./.env` to your global ignore file to prevent accidentally committing your secret keys to a public GitHub repository. Security is a first-class feature, not an afterthought.)*

## Writing the Tool Definitions

An agent is only as good as the tools it can access. For our agent, we’re going to build a custom tool: a Python code executor that can solve complex mathematical operations. While language models are amazing at processing semantics, they are notoriously terrible at basic arithmetic because they predict text rather than performing logical calculations. By giving our agent a calculator tool, we solve this bottleneck.

Let's start writing our script in `./agent.py`. We will import our libraries and define our custom tools. LangChain makes defining tools incredibly elegant using the `@tool` decorator. Each tool requires a descriptive docstring—the LLM reads this docstring to understand *when* and *how* to use the tool.

Let's look at the implementation inside `./agent.py`:

```python
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain import hub

# Load environment variables from ./.env
load_dotenv()

@tool
def calculate_expression(expression: str) -> str:
    """Useful for solving complex mathematical and algebraic expressions.
    Pass the expression as a raw mathematical string, e.g., '2 + 2 * (10 / 5)'."""
    try:
        # Use a safe evaluation context to prevent arbitrary code execution
        # In production, use a more secure sandboxed execution environment
        result = eval(expression, {"__builtins__": None}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

# Pack our tool into a list that the agent can read
tools = [calculate_expression]
```

## Initializing the Agent and Executing the Loop

Now that we have our custom math tool defined, we need to wire up the brain of the operation. We'll use OpenAI's `gpt-4-turbo` as our reasoning engine. To orchestrate the loop, we’ll pull a pre-configured prompt template from the LangChain hub, build an OpenAI tools-based agent, and wrap it inside an `AgentExecutor` which manages the iterative ReAct cycle.

Add the following execution logic to the bottom of `./agent.py`:

```python
def main():
    # Initialize our LLM with high temperature for creativity, or low for deterministic tool use
    llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)

    # Pull the standard OpenAI Tools prompt from the community hub
    # This prompt tells the LLM how to format its thoughts and tool calls
    prompt = hub.pull("hwchase17/openai-tools-agent")

    # Construct the tools-based agent
    agent = create_openai_tools_agent(llm, tools, prompt)

    # Create the runner/executor that handles the observation-action loop
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        handle_parsing_errors=True
    )

    # Test the agent with a complex multi-step prompt
    query = "What is the result of 1529 multiplied by 42, and then divided by 7?"
    print(f"User Query: {query}\n")
    
    response = agent_executor.invoke({"input": query})
    print(f"\nAgent Response: {response['output']}")

if __name__ == "__main__":
    main()
```

When you run this script using `python ./agent.py` in your terminal, you will see the verbose output of the agent's thought process. It reads the query, realizes it cannot perform the math reliably on its own, calls the `calculate_expression` tool with the raw string `'1529 * 42 / 7'`, observes the output from your Python interpreter, and formulates a human-readable response. It is a stunning, beautiful cycle of automated reasoning.

```
+--------------------------------------------------------+
|  User: "What is 1529 multiplied by 42, divided by 7?" |
+--------------------------------------------------------+
                           |
                           v
+--------------------------------------------------------+
|  Agent Thought: I need to calculate 1529 * 42 / 7.     |
|  Action: Call tool `calculate_expression("1529*42/7")` |
+--------------------------------------------------------+
                           |
                           v
+--------------------------------------------------------+
|  Tool Output: "Result: 9174.0"                         |
+--------------------------------------------------------+
                           |
                           v
+--------------------------------------------------------+
|  Agent Output: "The result of 1529 multiplied by 42...|
+--------------------------------------------------------+
```

## Key Takeaways

- **Explicit Tooling**: LangChain agents utilize structural tool definitions with explicit docstrings to decide when and how to call external utilities.
- **Environment Management**: Configuration parameters must be stored securely inside `./.env` and loaded using packages like `python-dotenv` to ensure security.
- **Structured Reasoning**: The `AgentExecutor` orchestrates the cognitive action-observation loop, preventing language models from hallucinating factual data.
- **Separation of Concerns**: Building agents requires splitting logic into isolated modules: `./agent.py` for execution, `./requirements.txt` for libraries, and `./.env` for keys.

## Frequently Asked Questions

**Q: Why do we write tool descriptions inside Python docstrings?**
A: LangChain extracts the docstrings of functions decorated with `@tool` and injects them directly into the system prompt of the LLM. The LLM uses these descriptions to understand what the tool does and decide when to invoke it.

**Q: Can I run this script without setting up the `./.env` file?**
A: No. The `ChatOpenAI` class requires an active OpenAI API key to communicate with the model. Loading this key from `./.env` using `load_dotenv()` ensures that your secret credentials are never hardcoded into your source files.

**Q: How do I secure the `eval()` function in a production environment?**
A: Using `eval()` directly in Python can expose your system to code injection attacks. In a production environment, you should use a secure, isolated sandbox API, or parse and evaluate mathematical expressions using a non-evaluating parser library like `sympy` or `numexpr`.

---

*2024 is the year everything changed. Stay ahead. Subscribe.*

*— [Shantanu Vishwanadha](https://substack.com/@thecoderpanda)*
