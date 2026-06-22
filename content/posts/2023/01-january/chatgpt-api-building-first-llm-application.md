---
title: "ChatGPT API: Building Your First LLM-Powered Application"
subtitle: "Step-by-step tutorial to transition from prompt tinkering to programmatic LLM orchestration."
date: "2023-01-16"
author: "Shantanu Vishwanadha"
authorUrl: "https://substack.com/@thecoderpanda"
tags: ["tutorials", "chatgpt-api", "openai", "python"]
seoTitle: "ChatGPT API Tutorial: Building Your First LLM Application"
seoDescription: "A hands-on developer tutorial on building with the OpenAI ChatGPT API. Implement API connections, state management, and basic context."
featuredImage: "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
imageAlt: "Productive home office with monitor and plants"
category: "tutorials"
readingTime: "8 min read"
slug: "chatgpt-api-building-first-llm-application"
---

# ChatGPT API: Building Your First LLM-Powered Application

> **TL;DR:** Prompting ChatGPT in the browser is fun, but programmatic orchestration is where real software is built. Today, we will build a complete, stateful conversational console agent in Python using OpenAI's standard completion API, managing chat state and memory manually like a pro.

If you are like most developers right now, you have spent the last month copy-pasting code, logs, and prompt instructions into the ChatGPT web interface. It feels magical. But copy-pasting is not software engineering. To build real products, we must interact with these models programmatically.

In January 2023, while we wait for an official conversational-optimized API endpoint, developers are building stateful applications on top of OpenAI’s robust text completion models—primarily `text-davinci-003`. 

But here is the engineering puzzle: **these API endpoints are completely stateless.**

When you send a prompt to `text-davinci-003`, the model has zero memory of any previous API calls you made. It is a mathematical function that processes a single block of input text and predicts the most likely continuation. If you want a conversational experience, you—the developer—must manage, format, and feed the historical conversational state back into the model on every single turn.

Today, we are going to write a complete, robust, and stateful conversational agent in Python. We will manage memory, handle token limits, implement safety fallbacks, and build an interactive console loop.

Let's dive into the code.

---

## The Conversational Architecture

To build a stateful chat on a stateless API, we must format our text payload as a structured transcript. We will define:
1. **A System Prompt**: Setting the assistant's persona, boundaries, and formatting instructions.
2. **Conversation History**: An ordered log of alternating user messages and assistant responses.
3. **The Stop Sequences**: Standard characters (like `Human:` and `AI:`) that tell the model when to stop generating text and hand execution control back to our code.

```
+-------------------------------------------------------------+
| System Prompt: "You are a helpful coding assistant..."       |
+-------------------------------------------------------------+
| Chat History:                                               |
| Human: How do I reverse a string in Python?                 |
| AI: You can use slicing: `string[::-1]`.                    |
+-------------------------------------------------------------+
| Active Prompt:                                              |
| Human: Can you explain how that slicing works?              |
| AI: [MODEL GENERATES RESPONSE HERE AND STOPS AT "Human:"]   |
+-------------------------------------------------------------+
```

If we do not include explicit stop sequences, the model will hallucinate both sides of the conversation, generating text for the user, replying to itself, and burning through your API tokens in seconds.

---

## Step-by-Step Code Walkthrough

Let’s write our stateful client. We will use a sliding memory window to ensure we don't exceed the model's 4,097 token limit. If the history gets too long, we will truncate the oldest messages, keeping the system prompt intact.

Create a file named `assistant.py` and implement the following logic:

```python
import os
import openai

# Step 1: Configuration and Key Initialization
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("System Error: OPENAI_API_KEY environment variable is not set.")

class ConversationAgent:
    def __init__(self, system_instruction: str, max_history_turns: int = 5):
        self.system_instruction = system_instruction
        self.max_history_turns = max_history_turns
        self.history = [] # Stores list of tuples: (sender, message)

    def add_message(self, sender: str, text: str):
        """Appends a message to the active history log."""
        self.history.append((sender, text))
        # Keep memory bounds safe by evicting older turns
        if len(self.history) > self.max_history_turns * 2:
            self.history = self.history[-self.max_history_turns * 2:]

    def _build_full_prompt(self, new_user_input: str) -> str:
        """Assembles the system instructions, historical log, and active prompt."""
        prompt_parts = [self.system_instruction, "\n"]
        
        # Format historical turns
        for sender, message in self.history:
            prompt_parts.append(f"{sender}: {message}")
            
        # Append the current active prompt
        prompt_parts.append(f"Human: {new_user_input}")
        prompt_parts.append("AI:")
        
        return "\n".join(prompt_parts)

    def send_prompt(self, user_input: str) -> str:
        """Sends the compiled conversational prompt to the Completion API."""
        full_prompt = self._build_full_prompt(user_input)
        
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=full_prompt,
                max_tokens=250,
                temperature=0.7,        # Balanced creativity and coherence
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.6,    # Encourages conversation flow
                stop=["Human:", "AI:"]   # Stops model from talking to itself!
            )
            
            ai_response = response.choices[0].text.strip()
            
            # Commit the active turn to our internal history
            self.add_message("Human", user_input)
            self.add_message("AI", ai_response)
            
            return ai_response
            
        except Exception as e:
            return f"Error communicating with OpenAI API: {str(e)}"

# Step 3: The Interactive Console Execution Loop
if __name__ == "__main__":
    system_persona = (
        "You are a sarcastic but highly competent software architect named Jarvis. "
        "You give direct, code-heavy answers, and you hate long introductions or fluff."
    )
    
    # Initialize the stateful conversational agent
    agent = ConversationAgent(system_persona, max_history_turns=4)
    
    print("====================================================")
    print(" Jarvis: Conversational Client Initialized. Go ahead.")
    print("====================================================\n")
    
    while True:
        try:
            user_msg = input("You: ")
            if user_msg.strip().lower() in ["exit", "quit", "q"]:
                print("Jarvis: Fine. Back to sleep then.")
                break
                
            if not user_msg.strip():
                continue
                
            reply = agent.send_prompt(user_msg)
            print(f"\nJarvis: {reply}\n")
            
        except (KeyboardInterrupt, EOFError):
            print("\nJarvis: Terminated abruptly. Goodbye.")
            break
```

---

## Deconstructing the Magic Parameters

To make this script run reliably, there are three critical parameters you must understand:

### 1. The `stop` Sequence
This is our execution guardrail. By passing `stop=["Human:", "AI:"]`, we tell the model: *"If you are about to output the characters 'Human:' or 'AI:', stop generating instantly."* Without this, the model will output its reply, write `Human: How do I do X?`, generate a reply to *that* mock question, and keep going until the token window is filled.

### 2. The `presence_penalty`
We set this to `0.6`. Presence penalty penalizes new tokens based on whether they have already appeared in the output history. A positive value prevents the model from repeating the same phrases, encouraging a more diverse, natural-sounding dialogue.

### 3. The `temperature`
Set to `0.7` for standard conversational applications. If you are building a tool that needs to write factual configurations or strictly format files, dial this down to `0.0` or `0.1` to make the outputs as deterministic and accurate as possible.

---

## Production Security: API Key Hygiene

When writing software with LLM integrations, **never** hardcode your API keys directly into your source code. If you commit that file to GitHub, bot scripts will scrape your key within seconds, run up thousands of dollars of API charges, and leave you with the bill.

Always use environment variables:
```bash
# On Mac/Linux:
export OPENAI_API_KEY="your-secret-key-here"

# On Windows:
set OPENAI_API_KEY="your-secret-key-here"
```

---

## Key Takeaways

- **Memory Management**: Completion APIs are completely stateless. You must format and pass the entire message history on every call.
- **Stop Guards**: Always declare explicit stop sequences to prevent runaway text generation and excessive API costs.
- **Sliding History**: Implement sliding context limits to evict old conversational logs and stay within token bounds.
- **Sanitize Environment**: Keep API keys strictly separated from your source code using system environment variables.

---

## Frequently Asked Questions

**Q: What happens if our chat history exceeds the model's token limit?**
A: The API will throw a 400 error indicating that the token limit has been exceeded. In production systems, you should use libraries like `tiktoken` to count tokens precisely. If the prompt is too close to the limit, truncate the oldest message pairs until the prompt size fits within the allowed bounds.

**Q: Can we store conversation history in a database like Redis instead of in-memory lists?**
A: Yes! For multi-user web applications, storing conversation logs in a fast key-value store like Redis is standard. Use the user's session ID as the key and retrieve/update their chat history array on every API request.

**Q: How do we handle streaming responses so users see characters generate in real-time?**
A: To implement streaming, pass `stream=True` in the API call parameters. This changes the response return type to a generator that yields chunks of text as they are computed by OpenAI's servers. You can then stream these chunks straight to your client frontend using Server-Sent Events.

---

*If this gave you even one useful insight, subscribe — I drop these every week.*

*— [Shantanu Vishwanadha](https://substack.com/@thecoderpanda)*