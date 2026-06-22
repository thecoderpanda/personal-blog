---
title: "LangChain Complete Tutorial: Chains, Memory, and Agents from Scratch"
subtitle: "Master LangChain core components by building a conversational assistant equipped with custom web search and math tools."
date: "2023-04-12"
author: "Shantanu Vishwanadha"
authorUrl: "https://substack.com/@thecoderpanda"
tags: ["tutorials", "langchain", "python", "agent-building"]
seoTitle: "LangChain Tutorial: Chains, Memory & Agents"
seoDescription: "A comprehensive developer tutorial on LangChain. Build custom chains, implement chat memory buffers, and run tools-enabled agents from scratch."
featuredImage: "https://images.unsplash.com/photo-1555066931-4365d14bab8c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
imageAlt: "Dark terminal with colorful code syntax"
category: "tutorials"
readingTime: "10 min read"
slug: "langchain-complete-tutorial-chains-memory-agents"
---

The hype around LLMs is exciting, but as software engineers, we don't build businesses on hype. We build them on code, architecture, and reliable, reproducible execution. 

If you have tried building anything beyond a basic wrapper around the OpenAI chat API, you have quickly run into the classic developer bottlenecks: how do you manage state across a conversation? How do you run structured operations where one model’s output is another model’s input? And how do you safely give your model the power to run terminal commands, write SQL queries, or browse the live web?

Today, we are going to build a production-ready conversational assistant from scratch. We will cover the three pillars of the LangChain framework: **Chains**, **Memory**, and **Agents**. 

Open up your terminal, pull up your favorite IDE, and let's get our hands dirty.

---

## Step 1: Setting Up the Environment

First, let's configure our virtual environment and install the required dependencies. We will need `langchain`, the `openai` SDK, and `google-search-results` (for the search tool).

```bash
pip install langchain openai google-search-results
export OPENAI_API_KEY="your-openai-api-key"
export SERPAPI_API_KEY="your-serpapi-api-key"
```

With our dependencies locked in, let’s boot up Python and start building.

---

## Step 2: The Foundation — Prompts and Chains

In LangChain, a **Chain** is an abstraction that combines a model and a prompt template into a single, executable pipeline. 

Instead of manually constructing strings and passing them to the API, we define reusable prompt layouts with dynamic input variables.

Here is how you build a standard `LLMChain` that generates technical summaries of complex topics:

```python
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain

llm = OpenAI(temperature=0.7)

summary_template = """
You are a highly experienced software architect. 
Summarize the following technology in three bullet points. 
Make it concise, direct, and slightly cynical.

Technology: {technology}
Summary:"""

prompt = PromptTemplate(
    input_variables=["technology"],
    template=summary_template
)

chain = LLMChain(llm=llm, prompt=prompt)
result = chain.run(technology="Kubernetes")
print(result)
```

By decoupling the prompt layout from the execution logic, your code remains clean, maintainable, and structured. If you want to modify your system persona later, you only edit the template string.

---

## Step 3: Giving the Model a Brain — Adding Memory

Large language models are inherently stateless. Every request to the completion API is treated as a completely isolated event. To build a conversational interface, you have to manually collect, format, and pass the entire history of the chat back to the model with every new prompt.

LangChain provides **Memory** classes to automate this exact flow. The most direct approach is `ConversationBufferMemory`, which stores every interaction in an in-memory list.

Let’s build a stateful conversational chain:

```python
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

llm = OpenAI(temperature=0.5)
memory = ConversationBufferMemory()

conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

response_1 = conversation.predict(input="Hi! My name is Shantanu and I am a software engineer.")
print(response_1)

response_2 = conversation.predict(input="What is my profession and name?")
print(response_2)
```

When you run this with `verbose=True`, you will see exactly what LangChain does under the hood. It automatically intercepts your input, queries the internal memory buffer, wraps the historical context in a system prompt, and sends the unified payload to the model.

---

## Step 4: Building an Agent with Custom Tools

Chains are powerful, but they are completely deterministic. The execution path is hardcoded into your Python script. 

An **Agent**, however, uses the LLM as a router. You equip the agent with a suite of **Tools** (which can be web APIs, database connections, local scripts, or other chains) and let the model dynamically decide which tool to call based on the user's intent.

Let’s build a custom mathematical tool and wire up an agent that can browse the web and perform precise calculations.

First, we will write a custom Python function to calculate Fibonacci numbers and wrap it in a LangChain `Tool` abstraction:

```python
from langchain.agents import Tool, initialize_agent, AgentType
from langchain.utilities import SerpAPIWrapper

def calculate_fibonacci(n_str):
    n = int(float(n_str))
    if n < 0:
        return "Invalid input"
    a, b = 0, b = 1
    for _ in range(n):
        a, b = b, a + b
    return str(a)

search = SerpAPIWrapper()

fibonacci_tool = Tool(
    name="Fibonacci Calculator",
    func=calculate_fibonacci,
    description="Useful for when you need to calculate the N-th Fibonacci number. Input must be an integer."
)

search_tool = Tool(
    name="Web Search",
    func=search.run,
    description="Useful for when you need to answer questions about current events, news, or live information."
)

tools = [search_tool, fibonacci_tool]
```

Notice the `description` fields on each tool. This is not for human documentation; **the LLM reads these descriptions to determine which tool to execute.** If the user asks for current news, the model sees that `Web Search` is "useful for current events" and selects it. If the user asks for a math computation, it selects the `Fibonacci Calculator`.

Now, let's initialize the agent using the `ZERO_SHOT_REACT_DESCRIPTION` pattern:

```python
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(temperature=0, model_name="gpt-4")

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

prompt = """
Find out who won the Academy Award for Best Actor in 2023. 
Then, take the number of letters in their first name, and calculate that Fibonacci number.
"""

response = agent.run(prompt)
print(response)
```

---

## Deconstructing the Agent Logs

When you execute this script, watch your terminal logs. The agent’s step-by-step reasoning cycle is laid bare:

1. **Thought**: The model realizes it needs to know who won the Best Actor award in 2023.
2. **Action**: It selects the `Web Search` tool with the action input `Academy Award Best Actor 2023`.
3. **Observation**: The search tool returns the name (e.g., "Brendan Fraser").
4. **Thought**: The model reads the output, counts the letters in "Brendan" (7 letters), and realizes it needs to find the 7th Fibonacci number.
5. **Action**: It selects the `Fibonacci Calculator` tool with the action input `7`.
6. **Observation**: The custom Python tool executes and returns `13`.
7. **Thought**: The model synthesizes the search observation and mathematical result into its final answer.
8. **Final Answer**: "Brendan Fraser won the Best Actor award in 2023. His first name has 7 letters, and the 7th Fibonacci number is 13."

---

## Bear Market Engineering: Moving to Production

When building agentic software in the real world, you must guard against non-deterministic failures. Here are three architectural rules for running agents in production:

1. **Enforce Timeouts**: Autonomous loops can hang or get trapped. Always set max iterations or maximum execution time limits:
   ```python
   agent = initialize_agent(
       tools, 
       llm, 
       agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
       max_iterations=5,
       early_stopping_method="generate"
   )
   ```
2. **Handle Parsing Errors Gracefully**: Sometimes the LLM fails to format its output in the exact ReAct format. Use `handle_parsing_errors=True` to catch these exceptions and feed them back to the model as self-correction prompts.
3. **Pin Your Dependencies**: LangChain is moving at a breakneck speed, with multiple releases every single day. Pin your exact version in your `requirements.txt` to prevent breaking API changes from taking down your production backend.

You now have the core blueprints for orchestrating models, handling state, and executing custom tools. Build something incredible, keep your code clean, and let's construct the future of software.
