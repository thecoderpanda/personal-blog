---
title: "Building with Llama 2: Running Open Source LLMs Locally"
subtitle: "Step-by-step developer tutorial on compiling llama.cpp, running inference on local silicon, and setting up a private OpenAI-compatible API endpoint."
date: "2023-08-12"
author: "Shantanu Vishwanadha"
authorUrl: "https://substack.com/@thecoderpanda"
tags: ["tutorials", "llama-2", "llama-cpp", "local-llms"]
seoTitle: "Run Llama 2 Locally: Complete Developer Guide"
seoDescription: "A step-by-step developer tutorial on running Meta's Llama 2 locally using llama.cpp, Python wrappers, and model quantization."
featuredImage: "https://images.unsplash.com/photo-1516116216624-53e697fedbea?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
imageAlt: "High-contrast developer setup with complex code structures on multiple screens"
category: "tutorials"
readingTime: "9 min read"
slug: "building-with-llama-2-running-open-source-locally"
---

When Meta announced Llama 2 last week, they showed benchmarks running on multi-million dollar data centers packed with high-end Nvidia A100s. And the immediate reaction from developers was: *"That is awesome, but I don't have a GPU farm in my guest bedroom. Can I actually run this on my own hardware?"*

The short answer is: **Yes, you can.** And not just run it—you can run it at near-production speeds on a standard Apple Silicon MacBook or a mid-range consumer gaming GPU.

This is made possible by a brilliant Bulgarian engineer named Georgi Gerganov, who wrote **`llama.cpp`**—a pure C/C++ implementation of LLaMA inference optimized for local CPU and GPU execution. 

In this tutorial, we are going to compile `llama.cpp`, configure local quantization to compress the model weights, and boot up an OpenAI-compatible local API server. By the end of this guide, you will be able to swap out your paid OpenAI API calls with a completely private, local Llama 2 endpoint by changing a single line of config code.

Let’s get our hands dirty.

---

## Step 1: The Magic of Quantization

First, let's address the elephant in the room: RAM.
In standard FP16 (16-bit floating point precision), model parameters require 2 bytes of memory per parameter:
*   A **7B model** requires **14 GB of VRAM/RAM** just to load, plus extra for context memory.
*   A **13B model** requires **26 GB**.
*   A **70B model** requires a staggering **140 GB**.

Most of us don’t have 140 GB of VRAM laying around. This is where **quantization** comes in.

Quantization compresses the model weights by representing the floating-point values as smaller data types, such as 8-bit or 4-bit integers. 

```
FP16 Weight (2 bytes) ----[ Quantization ]----> INT4 Weight (0.5 bytes)
                                                (75% RAM reduction!)
```

When we compress a 7B model from 16-bit to 4-bit (specifically the `Q4_K_M` format), the memory requirement drops from **14 GB to roughly 4.1 GB**. It fits easily on a standard laptop. Best of all, thanks to advanced quantization techniques, the loss in accuracy (measured by perplexity) is practically unnoticeable in real-world applications.

---

## Step 2: Compiling `llama.cpp`

We need to build `llama.cpp` directly from source to ensure it is perfectly optimized for your specific hardware.

First, clone the repository:

```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
```

### Option A: For Apple Silicon (M1/M2 MacBooks)
Apple Silicon chips have a unified memory architecture and a powerful GPU-equivalent engine called Metal. To compile `llama.cpp` with Metal support:

```bash
# This activates Apple Metal acceleration automatically
make LLAMA_METAL=1
```

### Option B: For Nvidia CUDA GPUs (Windows/Linux)
If you are running an Nvidia card (like an RTX 3080 or 4090), you want CUDA acceleration to offload processing to your GPU:

```bash
# Build with CUDA support
make LLAMA_CUDA=1
```

Once compilation is complete, you will see several binary files in the root directory, including the executable `./main` and `./server`.

---

## Step 3: Downloading and Converting Weights

To prevent licensing headaches, we will download pre-quantized weights directly in the **GGUF** format (the official file format optimized for `llama.cpp` released recently to replace GGML). 

The legendary developer **TheBloke** has already quantized and hosted almost every Llama 2 variation on Hugging Face. Let’s download the **Llama-2-13B-Chat-GGUF** model using the `Q4_K_M` quantization (which balances speed and performance beautifully):

```bash
# Install huggingface-hub CLI if you haven't
pip install huggingface_hub

# Download the specific quantized model file
huggingface-cli download TheBloke/Llama-2-13B-Chat-GGUF llama-2-13b-chat.Q4_K_M.gguf --local-dir . --local-dir-use-symlinks False
```

This will download a single `llama-2-13b-chat.Q4_K_M.gguf` file (roughly 7.8 GB) directly into your folder.

---

## Step 4: Running Local Inference

Now we can test if our build works by running a simple command-line generation prompt. 

```bash
./main -m llama-2-13b-chat.Q4_K_M.gguf \
       -p "[INST] <<SYS>> You are a witty, helpful coding assistant. <</SYS>> What is the difference between a process and a thread? [/INST]" \
       -n 512 \
       -ngl 32
```

Let's break down those flags:
*   `-m`: Specifies the path to our downloaded model weights.
*   `-p`: The prompt, styled using Llama 2’s unique `[INST]` chat prompt format.
*   `-n 512`: The maximum number of tokens to generate.
*   `-ngl 32`: **Number of layers to offload to the GPU**. If you are on an Apple Silicon Mac or Nvidia GPU, setting this to `32` (or higher) moves the model layers off the CPU and into ultra-fast GPU memory, boosting tokens-per-second dramatically.

You should see the text stream into your terminal at a lightning-fast pace. On an M2 MacBook Pro, you’ll easily pull **25-30 tokens per second** on a 13B model.

---

## Step 5: Setting Up an OpenAI-Compatible API Server

The absolute killer feature of `llama.cpp` is its built-in local server. It comes with a web server binary that mimics the official OpenAI chat completions endpoint structure.

Let's launch the local server:

```bash
./server -m llama-2-13b-chat.Q4_K_M.gguf -c 4096 --port 8000 -ngl 32
```

Now, your server is listening on `http://localhost:8000`. It is ready to accept standard REST requests.

Let's test it with a simple `curl` request:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a witty tech lead."},
      {"role": "user", "content": "Why should I learn Rust?"}
    ]
  }'
```

The response returns a JSON payload styled exactly like OpenAI’s API response.

---

## Step 6: Swapping Out Your Codebase Config

Because the server mimics the OpenAI API format, you can swap out OpenAI’s service in your existing application codebase with zero code restructuring. 

Here is how you do it in Python using the official `openai` SDK:

```python
import openai

# 1. Point the client to your local server instead of OpenAI's servers
openai.api_base = "http://localhost:8000/v1"
openai.api_key = "local-llama-no-key-required"  # Any dummy string works!

# 2. Call the chat completion just like you normally would
response = openai.ChatCompletion.create(
    model="llama-2-13b-chat", # This parameter is ignored by llama.cpp server
    messages=[
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "Write a fast Fibonacci function in Go."}
    ],
    temperature=0.7
)

# 3. Print the result
print(response.choices[0].message['content'])
```

Run this script. It connects directly to your local machine’s RAM/GPU, compiles the answer, and returns it.

No network requests, no subscription fees, no data sharing. 

---

## The Power of Local Sovereignty

You are now running a world-class large language model locally. 

This is more than just a cool developer trick—it represents a fundamental shift in user sovereignty. You are no longer reliant on the goodwill, pricing changes, or content moderation policies of a single corporate giant. Your software can run in an offline environment, on remote edges, or on secure air-gapped local intranets.

The code is compiled, the model weights are on your disk, and the API is ready. 

Go build something incredible.

*Keep hacking.*