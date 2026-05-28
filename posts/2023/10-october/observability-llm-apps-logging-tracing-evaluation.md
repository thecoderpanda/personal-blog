---
title: "Observability for LLM Apps: Logging, Tracing, and Evaluation"
subtitle: "Debugging non-deterministic loops. A practical guide to implementing LangSmith, Phoenix, or LangFuse observability chains."
date: "2023-10-28"
author: "Shantanu Vishwanadha"
authorUrl: "https://substack.com/@thecoderpanda"
tags: ["tutorials", "observability", "llmops", "langsmith", "langfuse"]
seoTitle: "Observability for LLM Apps: Tracing & Eval"
seoDescription: "Learn how to build production monitoring for LLM applications. Set up telemetry, track prompts, examine token latency, and implement LangSmith."
featuredImage: "https://images.unsplash.com/photo-1516116216624-53e697fedbea?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
imageAlt: "High-contrast developer setup with complex code structures on multiple screens"
category: "tutorials"
readingTime: "9 min read"
slug: "observability-llm-apps-logging-tracing-evaluation"
---

Deploying traditional web applications is a solved science. When your Node or Python server fails in production, you check the logs, find the stack trace, locate the exact line of code that threw the unhandled exception, fix the syntax error, run your tests, and deploy a hotfix. 

Deterministic software is predictable. Input X leads to state Y, and if it doesn't, a compiler or a runtime tells you why.

But as soon as you deploy an **LLM-powered application** or an **autonomous agent** to production, you enter a strange, non-deterministic twilight zone. 

An agent doesn't throw a standard 500 error when it fails. Instead, it completes with a "200 OK" status, but outputted absolute garbage. Or it got stuck in a recursive loop, calling the same weather API tool 40 times until it hit your token rate limit. Or it decided to format its JSON response with trailing commas, completely breaking your parser downstream.

How do you debug a system where the primary processor (the LLM) is a black box of floating-point numbers?

The answer is **LLM Observability**. 

You cannot rely on simple console logging anymore. You need structured tracing, prompt telemetry, token latency tracking, and continuous evaluations. In this guide, we are going to look at how to implement production-grade observability chains using **LangSmith** and **LangFuse**.

---

## 1. The Three Pillars of LLM Observability

To see inside the execution of a non-deterministic application, we must capture metadata at three different levels:

### A. Logging (The Inputs and Outputs)
We must capture every raw prompt sent to the model and every raw completion returned. This includes:
*   The system instructions.
*   The raw human messages.
*   The model temperature, top-p, and custom hyperparameter settings.
*   The exact raw string returned, before any parsing or processing occurs.

### B. Tracing (The Execution Graph)
An LLM call is rarely isolated. It is usually part of a larger workflow—such as retrieving chunks from a vector database, evaluating a conditional router, executing a local bash tool, and compiling a final answer. 

A **trace** represents the entire journey of a single user request. Inside a trace are **spans** representing individual sub-tasks (e.g., a DB lookup span, an LLM execution span, a tool run span). Tracing tells you *where* in the chain things went wrong.

### C. Evaluation (The Quality Layer)
Since we can't write standard assertions (`assert output == expected`), we must build evaluation heuristics:
*   **Latency**: How long did each step take? Which tool is blocking the user experience?
*   **Cost**: How many prompt and completion tokens were consumed?
*   **Semantic Quality**: Using smaller, evaluator LLMs to grade the production outputs on criteria like *relevance*, *faithfulness*, and *toxicity*.

---

## 2. Implementing Tracing: A Practical Python Tutorial

Let's look at how to integrate production tracing into an agentic workflow using Python. We will explore both **LangSmith** (for LangChain-native apps) and **LangFuse** (an excellent, open-source, self-hostable alternative).

### Option A: Setting Up LangSmith (The Zero-Code Approach)

If you are already building your app with LangChain or LangGraph, LangSmith tracing is practically free. You don't even need to change your source code; you simply configure your system environment variables.

1.  Sign up at [smith.langchain.com](https://smith.langchain.com) and generate an API key.
2.  Set the following environment variables in your production container:

```bash
export LANGCHAIN_TRACING_V2="true"
export LANGCHAIN_API_KEY="your-langsmith-api-key"
export LANGCHAIN_PROJECT="my-production-agent"
```

Once these variables are set, LangChain will automatically intercept every LLM execution, vector store retrieval, and tool run, streaming the entire trace graph directly to your LangSmith dashboard in real-time. You can immediately see the exact prompt templates used, the raw embeddings retrieved, and the exact latency of each model run.

---

### Option B: Setting Up LangFuse (The Open-Source, Non-SDK Approach)

If you aren't using LangChain, or you prefer a lightweight, self-hostable open-source tracer, **LangFuse** is the gold standard. 

Here is how you manually wrap a custom OpenAI tool-calling loop with LangFuse tracing:

```bash
pip install langfuse openai
```

```python
from langfuse import Langfuse
from openai import OpenAI
import os

# Initialize the Langfuse client
langfuse = Langfuse(
    public_key=os.environ.get("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.environ.get("LANGFUSE_SECRET_KEY"),
    host="https://cloud.langfuse.com"
)

openai_client = OpenAI()

def run_agentic_task(user_query: str):
    # 1. Start a root Trace
    trace = langfuse.trace(
        name="agent-task-execution",
        user_id="user_12345",
        input={"query": user_query}
    )
    
    # 2. Start a Span for the vector retrieval step
    retrieval_span = trace.span(name="vector-db-retrieval", input={"query": user_query})
    
    # Simulate database retrieval
    retrieved_context = "Production Server URL is 'https://api.internal/v1'"
    
    # Update and resolve the retrieval span
    retrieval_span.end(output={"context": retrieved_context})
    
    # 3. Start a Generation step for the LLM execution
    generation = trace.generation(
        name="openai-completion",
        model="gpt-4",
        model_parameters={"temperature": 0.2},
        input=[{"role": "user", "content": user_query}]
    )
    
    # Execute the actual model call
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Use this context to help: {retrieved_context}"},
            {"role": "user", "content": user_query}
        ],
        temperature=0.2
    )
    
    completion_text = response.choices[0].message.content
    
    # End the generation span and track actual token consumption
    generation.end(
        output={"completion": completion_text},
        usage={
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens
        }
    )
    
    # End the root trace
    trace.end(output={"final_response": completion_text})
    return completion_text

if __name__ == "__main__":
    result = run_agentic_task("Where should I send server requests?")
    print(f"Agent Output: {result}")
    
    # Flush trace queue to ensure logs are sent to the cloud
    langfuse.flush()
```

---

## 3. Designing Continuous Evaluations

Once your traces are flowing into your dashboard, the next step is setting up **Evals**. 

In an AI-native stack, you can’t wait for users to report bugs. You must proactively evaluate your production logs. The most common pattern is **Model-graded Evals**:

1.  **Extract Samples**: Set up a pipeline to capture a random 5% sample of your production trace outputs.
2.  **Define a Rubric**: Write a highly precise system prompt for an evaluator model (like GPT-4-turbo) that instructs it to grade the agent's output:
    ```
    Evaluate the assistant's answer based on the retrieved context.
    Is the answer fully factual and backed by the context? 
    Output a score from 1 (completely fabricated) to 5 (fully faithful).
    Provide your reasoning, followed by the raw score.
    ```
3.  **Run Asynchronous Evals**: Execute this evaluation asynchronously in the background. If a trace receives a score lower than 3, trigger an alert in your team's Slack channel or create a debugging ticket with the trace link attached.

---

## The Observatory Advantage

Building LLM applications without observability is like sailing a ship without a compass. You might navigate the shallow waters of local testing, but you will wreck your ship on the reefs of production scale.

By implementing structured tracing, token tracking, and model-graded evaluations, you turn your erratic, non-deterministic agent into a highly measurable, continuously optimizable software asset.

Stop guessing why your prompts are failing. Log, trace, evaluate, and build with absolute clarity.

*Let's make our software observable.*
