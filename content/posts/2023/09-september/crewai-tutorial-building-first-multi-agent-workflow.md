---
title: "CrewAI Tutorial: Building Your First Multi-Agent Workflow"
subtitle: "Write a crew of researchers, writers, and editors to automate content pipeline execution. A code-heavy developer walkthrough."
date: "2023-09-08"
author: "Shantanu Vishwanadha"
authorUrl: "https://substack.com/@thecoderpanda"
tags: ["tutorials", "crewai", "python", "multi-agent-workflow"]
seoTitle: "CrewAI Tutorial: Multi-Agent Workflow Guide"
seoDescription: "A hands-on developer tutorial building a multi-agent system with CrewAI in Python. Define roles, configure tasks, and run tools in parallel."
featuredImage: "https://images.unsplash.com/photo-1498050108023-c5249f4df085?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
imageAlt: "Black MacBook with code on screen"
category: "tutorials"
readingTime: "10 min read"
slug: "crewai-tutorial-building-first-multi-agent-workflow"
---

In my last post, we explored the theory behind why multi-agent collaboration is eating monolithic prompts for breakfast. But let's be real: concepts are cheap. In this bear market, we don't live on concepts; we live on working code. 

Today, we are going to get our hands dirty. We are building a fully functioning, production-grade autonomous content generation pipeline using **CrewAI**. 

We will instantiate a three-agent editorial team:
1.  **The Tech Researcher**: Scours the web, sifts through the noise, and collects hard data.
2.  **The Technical Writer**: Takes that research and drafts a highly engaging, lucid article.
3.  **The Editorial Manager**: Critiques the draft, ensures accuracy, and polishes it to perfection.

By the end of this tutorial, you will have a Python script that orchestrates these three agents to execute a research and writing pipeline autonomously. Let’s build.

---

## 1. Setting Up the Environment

First, let's set up our virtual environment and install the required dependencies. We will need `crewai` and `duckduckgo-search` (which we'll use as a simple, free web search tool for our researcher).

Open your terminal and run:

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install CrewAI and search tools
pip install crewai duckduckgo-search langchain-openai
```

Next, set up your OpenAI API key in your environment. CrewAI works incredibly well with `gpt-4-turbo` or `gpt-3.5-turbo`. For this tutorial, we will use GPT-4 for the reasoning tasks to keep hallucinations to a minimum.

```bash
export OPENAI_API_KEY="your-actual-api-key-here"
```

---

## 2. Writing the Code: Importing Libraries and Initializing LLM

Create a new file named `blog_crew.py`. We will begin by importing the necessary classes from CrewAI and LangChain.

```python
import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from duckduckgo_search import DDGS

# Ensure the API key is present
if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

# Initialize the primary language model
# Using GPT-4 for high-quality logical reasoning and structured coordination
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.2
)
```

Notice the low temperature (`0.2`). When building agents that coordinate, high temperature leads to chaotic outputs. We want our agents focused and analytical.

---

## 3. Building a Custom Search Tool

Let’s give our Researcher a tool to search the live web. We will wrap DuckDuckGo Search in a LangChain `Tool` interface.

```python
def web_search(query: str) -> str:
    """Performs a web search using DuckDuckGo and returns top results."""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=5)]
            if not results:
                return "No relevant web search results found."
            
            formatted_results = []
            for r in results:
                formatted_results.append(
                    f"Title: {r['title']}\nLink: {r['href']}\nSnippet: {r['body']}\n---"
                )
            return "\n".join(formatted_results)
    except Exception as e:
        return f"An error occurred during search: {str(e)}"

# Define the LangChain Tool
search_tool = Tool(
    name="Web Search",
    func=web_search,
    description="Useful for searching the internet for current events, technology updates, and tech stack details."
)
```

---

## 4. Defining the Editorial Agents

Now, we define our team. Pay close attention to how the `backstory` and `goal` are framed. This is the "casting" process. We want distinct, contrasting personas.

```python
# Agent 1: The Cynical Tech Researcher
researcher = Agent(
    role="Principal Tech Researcher",
    goal="Discover and synthesize verifiable facts, benchmarks, and architectural designs on assigned topics.",
    backstory="""You are an elite, cynical technical analyst. You despise marketing hype,
    corporate buzzwords, and vague claims. You demand source links, hard metrics, and 
    architectural diagrams. If a claim lacks evidence, you call it out.""",
    tools=[search_tool],
    llm=llm,
    verbose=True,
    allow_delegation=True
)

# Agent 2: The Practical Technical Writer
writer = Agent(
    role="Senior Technical Writer",
    goal="Transform complex technical findings into crystal-clear, engaging, and highly informative developer guides.",
    backstory="""You are a veteran technical blogger who knows how to explain incredibly complex ideas 
    with ease. Your writing is witty, conversational, and direct. You avoid passive voice 
    and fluff. You write for developers who value their time.""",
    llm=llm,
    verbose=True,
    allow_delegation=False  # Writers don't delegate; they sit down and write!
)

# Agent 3: The Editorial Manager
editor = Agent(
    role="Lead Editorial Manager",
    goal="Review written drafts for clarity, style, technical accuracy, and structural flow.",
    backstory="""You are a ruthless editorial director. You ensure that the final piece meets the 
    highest standards of developer relations. You check formatting, make sure all code blocks 
    are properly written, and verify that the writer accurately reflected the researcher's findings.""",
    llm=llm,
    verbose=True,
    allow_delegation=True
)
```

---

## 5. Configuring the Tasks

Tasks represent the work packages. Crucially, we can pass context from one task to another, building a logical chain of inputs and outputs.

```python
# Task 1: Comprehensive Research
research_task = Task(
    description="""Conduct deep research on the following topic: {topic}.
    Your focus should be to find actual architectural details, concrete developer trade-offs, 
    and at least three verified metrics or benchmarks. 
    You must provide your final research in a highly structured, bulleted markdown report 
    with all relevant source links included.""",
    expected_output="A detailed, bulleted markdown research report full of technical specs, metrics, and links.",
    agent=researcher
)

# Task 2: Crafting the Draft
writing_task = Task(
    description="""Using the markdown report produced by the Principal Tech Researcher, 
    write a deep-dive developer blog post about {topic}. 
    The post must be 800 to 1200 words, starting with a catchy introduction, 
    broken down with clear H2 and H3 headings, and including at least one valid code snippet 
    or configuration example. The tone must be conversational, sharp, and highly technical.""",
    expected_output="A complete, publication-ready technical blog post in markdown format.",
    agent=writer
)

# Task 3: The Ruthless Edit
editing_task = Task(
    description="""Review the technical blog post draft generated by the writer. 
    Check for:
    1. Grammatical flaws and passive voice.
    2. Alignment with the researcher's original facts.
    3. Proper formatting of code blocks.
    If the draft is sub-par, send it back with detailed feedback. 
    If it is excellent, apply final polish and deliver the completed markdown text.""",
    expected_output="A polished, masterfully written technical blog post in markdown, fully corrected.",
    agent=editor
)
```

---

## 6. Assembling the Crew and Running the Pipeline

Now, we tie it all together into a `Crew`. We will run this sequentially: the researcher compiles the raw facts, passes them to the writer to draft, and the editor performs the final review.

```python
# Instantiate the Crew
editorial_crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, writing_task, editing_task],
    process=Process.sequential,  # The outputs flow from task to task in order
    verbose=2  # High verbosity so we can watch the agents think in the terminal
)

# Run the crew on a specific topic
if __name__ == "__main__":
    target_topic = "Implementing Semantic Chunking in Vector Databases"
    print(f"🚀 Launching the Crew to tackle: '{target_topic}'...\n")
    
    result = editorial_crew.kickoff(inputs={"topic": target_topic})
    
    print("\n\n🏆 Pipeline Completed! Here is your final polished post:\n")
    print("========================================================\n")
    print(result)
```

---

## Running the Script and Observing the Output

Save the file and run it in your terminal:

```bash
python3 blog_crew.py
```

When you hit Enter, you'll see a beautiful, chaotic dance in your console:
1.  The **Researcher** will analyze the prompt, call the `Web Search` tool with queries like `"Semantic Chunking in vector databases benchmark metrics"`, extract the data, and compile a structured Markdown report.
2.  The **Writer** will ingest that report, translate the concepts of embedding distances, chunk boundaries, and token costs into highly readable, witty prose, and insert code blocks (e.g., using `langchain_experimental.text_splitter`).
3.  The **Editor** will step in, review the draft, perhaps ask the researcher a clarifying question about the vector database benchmarks, and then print the final output.

---

## Hard-Learned Lessons from Production

When you start running this in production, you’ll quickly hit three problems:
1.  **Rate Limits**: If you run parallel search tools, you will trigger rate limits on your API. Introduce backoffs or use robust search APIs like Serper or Tavily.
2.  **Context Window Bloat**: If you have too many agent interactions, the context grows fast. Keep your backstories tight and instruct agents to keep their intermediate responses concise.
3.  **Looping**: Sometimes agents get stuck asking each other the same question in a loop. To prevent this, set `max_iter` on your `Agent` classes (e.g., `max_iter=15`).

Agentic workflows are the next frontier. Stop writing single prompts, start writing pipelines.

---

*Did you get your first crew running? Let's discuss optimization strategies over on Twitter [@thecoderpanda](https://twitter.com/thecoderpanda)!*
