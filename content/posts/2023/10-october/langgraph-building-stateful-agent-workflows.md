---
title: "LangGraph: Building Stateful Agent Workflows with LangChain"
subtitle: "Move past single chain-of-thought execution. Learn how to construct cyclical agent flows, state machines, and human-in-the-loop steps."
date: "2023-10-08"
author: "Shantanu Vishwanadha"
authorUrl: "https://substack.com/@thecoderpanda"
tags: ["tutorials", "langgraph", "langchain", "state-machines", "python"]
seoTitle: "LangGraph Tutorial: Cyclic Agent Workflows"
seoDescription: "A deep hands-on developer tutorial building stateful cyclic agent workflows in Python with LangGraph, managing conversation state tables."
featuredImage: "https://images.unsplash.com/photo-1516116216624-53e697fedbea?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
imageAlt: "Multiple monitors with code in dark office"
category: "tutorials"
readingTime: "10 min read"
slug: "langgraph-building-stateful-agent-workflows"
---

Let’s be completely honest: the classic "chain" abstraction in AI engineering has run its course. 

We all started our LLM journeys by chaining prompts together: Input $\rightarrow$ Prompt A $\rightarrow$ Model A $\rightarrow$ Prompt B $\rightarrow$ Model B $\rightarrow$ Output. It’s neat, it’s deterministic, and it looks great in a documentation diagram. But as soon as you try to build a real agent that can search the web, write code, run it, find an error, and *fix its own mistakes*, a linear chain completely falls apart.

Why? Because real agent workflows are not linear. They are **cyclical**. They require loops, branching logic, conditional transitions, and state persistence. 

If you try to implement a cyclic loop in classic LangChain, you quickly find yourself trapped in a spaghetti-code nightmare of custom while-loops, hand-rolled state dictionary management, and fragile exception handling.

Enter **LangGraph**.

LangGraph is a library designed to build stateful, multi-actor applications with LLMs. It lets us construct agents as **state machines** where every node is a step (like an LLM call or a tool execution), and every edge is a transition rule (which can be conditional). 

In this tutorial, we are going to build a fully functional, stateful, cyclic agent with a human-in-the-loop approval step using Python and LangGraph.

---

## The Core Concepts of LangGraph

Before we write code, let’s look at the three core pillars of LangGraph:
1.  **State**: A shared database or data structure that represents the current state of your graph. Every node can read from and write to this state.
2.  **Nodes**: Python functions that perform actions. They take the current `State` as input, do some work (like calling an LLM or running a SQL query), and return an updated dictionary that merges into the state.
3.  **Edges**: Define how we move from one node to another. These can be simple direct edges or conditional edges based on the current state (e.g., if the LLM output contains tool calls, go to the "tools" node; otherwise, go to the "end" node).

---

## Step-by-Step Implementation: Building a Research & Code Agent

We will build an agent that researches a coding topic, drafts a script, and asks a human for approval before saving it.

Let's start by installing the dependencies:

```bash
pip install langgraph langchain langchain-openai
```

### 1. Defining the Graph State

First, we define our graph state. We will use Python's `TypedDict` to represent our state table. We want to track the user query, the generated code, any execution errors, and a list of messages.

```python
from typing import TypedDict, List, Dict, Any, Annotated
import operator

class AgentState(TypedDict):
    query: str
    code: str
    errors: str
    messages: Annotated[List[Dict[str, Any]], operator.add]
    approved: bool
```

The `Annotated[..., operator.add]` syntax is crucial. It tells LangGraph that instead of overwriting the `messages` list when a node returns a value, it should append the new messages to the existing list.

### 2. Setting Up Node Functions

Next, let’s define our nodes. We'll set up two primary nodes: a **Generator** node that writes Python code, and a **Validator** node that simulates a human checking the script.

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

model = ChatOpenAI(model="gpt-4", temperature=0)

def generator_node(state: AgentState):
    print("🤖 Node: Generator")
    query = state["query"]
    errors = state.get("errors", "")
    
    system_prompt = (
        "You are an expert Python engineer. Write a clean Python script based on the request. "
        "Return ONLY the raw executable Python code. Do not wrap it in markdown code blocks."
    )
    
    prompt = f"Write Python code to solve: {query}"
    if errors:
        prompt += f"\n\nPrevious attempt failed with error: {errors}\nPlease fix the code."
        
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt)
    ]
    
    response = model.invoke(messages)
    return {
        "code": response.content,
        "messages": [{"role": "assistant", "content": response.content}]
    }
```

Now let's add a **Human Approval** node. In LangGraph, we can pause execution and wait for input by setting up a human-in-the-loop node.

```python
def human_approval_node(state: AgentState):
    print("\n👥 Node: Human Approval")
    print("--- GENERATED CODE ---")
    print(state["code"])
    print("----------------------")
    
    user_input = input("Approve this code? (yes/no): ").strip().lower()
    
    if user_input == "yes":
        return {"approved": True}
    else:
        return {"approved": False, "errors": "Human feedback: Code style or logic rejected. Rewrite requested."}
```

### 3. Assembling the State Machine Graph

Now, let's wire everything together using `StateGraph`. We will define the flow, compile it, and add a conditional edge that decides whether to end the graph or route back to the generator based on the human's approval.

```python
from langgraph.graph import StateGraph, END

# Initialize the graph with our state definition
workflow = StateGraph(AgentState)

# Add our nodes to the graph
workflow.add_node("generator", generator_node)
workflow.add_node("approver", human_approval_node)

# Set the entry point of the graph
workflow.set_entry_point("generator")

# Generator goes directly to human approval step
workflow.add_edge("generator", "approver")

# We define a routing function for the conditional edge
def route_approval(state: AgentState):
    if state["approved"]:
        return "end"
    else:
        return "retry"

# Add conditional edge from the approver node
workflow.add_conditional_edges(
    "approver",
    route_approval,
    {
        "end": END,
        "retry": "generator"
    }
)

# Compile the graph
app = workflow.compile()
```

### 4. Running the Agent

Let's test our stateful agent by executing the compiled application with a starting query.

```python
if __name__ == "__main__":
    initial_state = {
        "query": "Write a function that calculates the fibonacci sequence up to N elements.",
        "code": "",
        "errors": "",
        "messages": [],
        "approved": False
    }
    
    print("Starting LangGraph execution loop...")
    final_output = app.invoke(initial_state)
    
    print("\n✅ Execution Finished!")
    print("Final Approved Code:")
    print(final_output["code"])
```

---

## Why This Architecture Wins in Production

By moving our agent logic into a LangGraph state machine, we gain three massive structural advantages:
1.  **Fault Tolerance**: If a tool fails, we don't crash our program. The state graph simply updates its "errors" state key and routes the transaction back to the generator node for correction.
2.  **Interruptibility**: The human approval node can easily be adapted for web APIs. You can save the state to a Postgres table, suspend the graph run, expose a UI button for the user, and resume the graph run using the saved thread ID once the button is clicked.
3.  **Clean Debugging**: Since every state update is logged, you can trace exactly how many retries your agent needed before arriving at the final approved state.

Stop vibes-coding brittle recursive functions. Use state machines to build deterministic control flows around your non-deterministic AI agents.

*Let's make some robust agent software.*
