---
title: "What I Got Wrong About AI (And What I Got Right)"
subtitle: "A brutal retro on my own predictions, mental models, and builds after seven years of shipping AI products."
date: "2026-06-09"
author: "Shantanu Vishwanadha"
authorUrl: "https://substack.com/@thecoderpanda"
tags: ["ai", "reflections", "software-engineering", "product-building"]
seoTitle: "What I Got Wrong About AI: A Seven-Year Retro | Shantanu"
seoDescription: "An honest retro of predictions, architectures, and mental models from shipping AI products since 2019. What held up vs. what shattered."
featuredImage: "https://images.unsplash.com/photo-1677442135703-1787eea5ce01?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
imageAlt: "Glowing purple AI circuit network visualization"
category: "ai-agents"
readingTime: "7 min read"
slug: "what-i-got-wrong-about-ai"
---

# What I Got Wrong About AI (And What I Got Right)

> **TL;DR:** I've been building with AI since 2019. I got the big structural stuff right — AI as a dev productivity multiplier, open-source models closing the gap, agents being genuinely hard. I got the timing and texture catastrophically wrong — enterprise adoption, prompt fragility, and inference economics all surprised me. Here's the full autopsy, with updated mental models that I'm actually building from in 2026.

---

Seven years. Enough time to have confidently said something wrong in public, shipped it, watched it crumble, and then rebuilt the mental model from scratch. I've done that cycle at least three times with AI.

This post isn't a victory lap. It's closer to a postmortem you do when the system didn't crash *completely* but definitely didn't behave as designed. Some of my predictions aged embarrassingly well. Others I'd like to quietly delete from the internet. You deserve the full picture.

---

## What I Got Right

### AI as a developer productivity multiplier

Back in 2019 I wrote that the primary near-term use case for large language models would be *augmenting developer workflows* — not replacing developers, not writing full applications autonomously, but making the individual developer loop dramatically faster. Specifically: faster context switching, faster first drafts of boilerplate, faster exploration of unfamiliar codebases.

This held up. If anything, I undersold it.

What I didn't fully model was *how* the productivity would compound. It's not just "generate some CRUD code." The real leverage shows up in the middle of debugging at 11pm when you've been staring at the same stack trace for two hours and you finally just describe the problem to a model. It gives you the one clue that reorients everything. That kind of unblocking — the cognitive rescue — is where I've watched developer velocity actually move.

### Open-source models catching up — eventually

In 2021, when GPT-3 dropped and everyone assumed OpenAI had a permanent moat, I made an unpopular argument: open-source would catch up on the capability curve, and the gap would compress faster than people expected. The reasoning was straightforward — the techniques weren't secret (attention mechanisms, RLHF, scaling laws), and once you had training recipes + compute access, talented teams could replicate results. The moat was temporary.

That call was right, but the timeline was off. I said "2–3 years." It took closer to four. Llama 3, Mistral, Qwen, DeepSeek — the open-source ecosystem in 2026 is genuinely competitive at most practical workloads. For inference at the edge, for fine-tuning on proprietary data, for cost-sensitive production pipelines, open-source is often the right call now.

### Agents being harder than they look

This one I got right, but for slightly the wrong reasons.

In 2022, I wrote that "autonomous AI agents are a systems engineering problem disguised as a model problem." I thought the hard part would be tool orchestration — getting reliable JSON out of a model, handling retries, building state machines for multi-step tasks. Those are genuinely hard. But the *harder* hard part turned out to be something more subtle: **error accumulation over long horizons**.

In short agentic loops (2–3 tool calls), current models are surprisingly reliable. Extend that to 10–15 steps with branching logic, and you're fighting a compounding error rate that no amount of prompt engineering fully solves. The architecture that actually works — and what I'm running in production today — involves aggressive human-in-the-loop checkpoints, deterministic rollback states, and treating agent confidence scores as first-class citizens in the control flow, not just metadata.

```python
if agent_confidence < 0.72 or step_count > HORIZON_THRESHOLD:
    return HumanCheckpoint(
        context=current_state,
        suggested_next=agent_output,
        requires_approval=True
    )
```

That's not "autonomous." But it ships and it doesn't hallucinate your customer's data into oblivion.

---

## What I Got Wrong

### The speed of enterprise adoption

I thought enterprise would be faster. Not naive-fast — I knew there'd be procurement cycles and security reviews and change management theater. But I genuinely believed that the productivity signal was so strong that by 2024, most engineering orgs would have meaningfully integrated AI into their dev workflows. I was off by 18 months at minimum, and the *reason* I was off is instructive.

I modeled enterprise adoption as a rational optimization problem. It's not. It's a political problem. In most large orgs, the blocker wasn't "does this work?" — it was "whose budget does this come from, who owns the liability if it goes wrong, and what happens to the team whose job looks adjacent to this?" Those questions don't have technical answers. I should have known better.

### Prompt sensitivity persisting this long

I was confidently wrong here. In 2022, I told people that prompt fragility — the phenomenon where rewording a question slightly breaks your output — was a transitional problem. Better training, RLHF, instruction tuning: these would make models robust to natural language variation by late 2023, I said.

It's 2026. Prompt sensitivity is better. It is not solved.

You can still break a production RAG pipeline by changing "Summarize the following:" to "Please summarize:" in some edge cases. The consistency gap between GPT-4-class models in controlled evals versus *your actual data in production* remains one of the most frustrating operational realities of building AI products. I've burned entire sprint cycles on this. That time I spent four hours debugging why a contract extraction pipeline started hallucinating clause numbers — and the root cause was a single trailing newline in the system prompt — that's not a 2022 problem. That happened eight months ago.

The mental model update here: treat prompts like database schema. Version them. Test them with regression suites. Never change them informally in production.

### Inference cost as a lasting constraint

I fundamentally underestimated how expensive inference at scale would remain, and for how long.

My 2021 model was: as models become commodities and hardware gets cheaper, inference cost approaches zero, and the economics of AI-powered products become trivially favorable. That logic was correct in direction but wrong in timeline and magnitude. Moore's Law is real, but the demand curve for tokens has been running faster than the supply curve for compute. As model capabilities improve, people route *more* tokens through the pipeline, not fewer. A better model tempts you to build longer context windows, more sophisticated multi-agent chains, more retrieval passes.

The practical consequence: I've had to redesign architectures specifically around inference cost more times than I expected. Smart caching of embeddings, aggressive query routing to smaller models for simple tasks, batching strategies that sacrifice latency for throughput — this is real product engineering work that I didn't budget for in 2021.

---

## The Mental Model That Broke Down Completely

The biggest reframe I had to make wasn't about a specific prediction. It was about the fundamental frame I was using to think about AI.

For the first few years, I — like most people — was implicitly using the **replacement model**: AI is going to replace X type of work. The question was just *when* and *which X*. This frame made me think about AI as a threat to reason about and a capability to extract, but it made collaboration patterns invisible to me.

The frame that actually fits the reality I'm living in now is the **collaboration model**: AI is a new kind of *team member* with specific capabilities, specific failure modes, and specific requirements for how you structure work together. You wouldn't hand a junior engineer an ambiguous spec and expect a production-ready system. You'd pair with them, review their output, set up guardrails, give feedback loops. That's exactly how you get good output from AI systems.

This reframe changes everything about how you architect AI products. Instead of "how do I make the AI do this autonomously," the question becomes "where in this workflow does a human decision add the most value, and how do I design the handoff so it's fast and low-friction?"

That question has better answers. And it ships.

---

## My Updated Mental Models for 2026

Three things I'm building from now that I wasn't building from three years ago:

**Models as APIs, not products.** The underlying model layer is increasingly commodity. The value is in the product surface, the data flywheel, and the workflow integration — not in which foundation model you're calling.

**Eval-first development.** You cannot iterate on AI product quality without automated evals. This isn't optional. If you're shipping AI features without a regression suite for your prompts and outputs, you're flying blind and you will break things in production without knowing it. Build your evals before you build your features.

**Agentic architectures need human-in-the-loop as a design primitive, not an afterthought.** The systems that are actually working in production are not fully autonomous. They're partially autonomous with well-designed escalation points. Design for that from day one.

---

## Key Takeaways

- **AI as dev productivity multiplier** was the right bet — the compounding happens at the "unblocking" layer, not just code generation.
- **Enterprise adoption is a political problem** dressed in a technical problem's clothing — model it accordingly.
- **Prompts need version control and regression testing** — treat them like schema, not prose.
- **Inference cost is a real product constraint** that doesn't disappear with model improvements because demand scales with capability.
- **The collaboration frame beats the replacement frame** — design AI systems like you'd design workflows with a very capable but very specific team member.

---

## Frequently Asked Questions

**You've been doing this since 2019. What's the single biggest skill that's mattered most for building AI products?**

Intellectual honesty about failure modes. Not the failure modes of *other people's* architectures — your own. The builders who are shipping in 2026 are the ones who ran real evals, found where their system broke, and redesigned instead of rationalizing. The ones who shipped demos that became products without that rigor are, largely, stuck.

**Is the "AI replaces developers" narrative dead?**

No — but it's been substantially de-risked for the near term, and the path it takes will look different than the blunt displacement people feared. The realistic near-term future is a smaller number of developers shipping significantly more, with AI handling the predictable, codifiable work and humans focusing on architecture, judgment calls, and product decisions. That's a labor market shift, not a deletion event. It's still worth paying attention to, just on a different timeline than the 2023 discourse implied.

---

*Subscribe — I write about building with AI and startup strategy weekly.*

*— [Shantanu Vishwanadha](https://substack.com/@thecoderpanda)*
