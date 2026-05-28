---
title: "The Developer Evangelist's Handbook: Speaking at Conferences"
subtitle: "How to stand on stage in front of hundreds of highly skeptical, sleep-deprived engineers and deliver massive value without getting booed off the stage."
date: "2019-04-24"
author: "Shantanu Vishwanadha"
authorUrl: "https://substack.com/@thecoderpanda"
tags: ["devrel", "developer-relations", "public-speaking", "tech-conferences", "developer-marketing"]
seoTitle: "Developer Evangelist's Guide: Speaking at Tech Conferences"
seoDescription: "The ultimate developer relations guide to speaking at tech conferences. Learn how to craft technical presentations, survive live demos, and win over developers."
featuredImage: "https://images.unsplash.com/photo-1515187029135-18ee286d815b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
imageAlt: "A group of software developers and professionals collaborating in a highly focused workspace or conference workshop."
category: "developer-relations"
readingTime: "6 min read"
slug: "developer-evangelists-handbook-speaking-at-conferences"
---

# The Developer Evangelist's Handbook: Speaking at Conferences

> **TL;DR:** Speaking at developer conferences is one of the most high-leverage ways to build trust and drive product adoption—but it is also a minefield of potential disasters. If you want to connect with highly skeptical developers, you need to ditch the marketing pitch, embrace live coding failures, and focus entirely on solving real, practical problems.

Let’s set the scene. You are standing backstage at a massive tech conference in San Francisco. The air is thick with the scent of lukewarm catering coffee, dry ice, and the collective anxiety of eight hundred software engineers waiting in the main auditorium. Your chest is tight, your hands are slightly damp, and you are clutching a clicker like it’s a life preserver. In exactly three minutes, you are going to walk out under the blinding stage lights to talk about your company’s new developer tool.

Here is the cold, hard truth: developers are quite possibly the hardest audience on the planet to speak to. They are notoriously cynical, highly skeptical of authority, and possess built-in, military-grade ad-blockers in their brains. They don’t care about your company’s Series B funding round, they don't care about your "synergistic ecosystem paradigms," and they certainly do not care about your marketing slide deck. If you stand up there and try to sell them a polished corporate pitch, they will immediately open their laptops, log onto Hacker News, and systematically rip your presentation to shreds on Twitter before you've even cleared your throat. To win over a room full of sleep-deprived developers, you have to play by a completely different set of rules.

## Rule #1: Ditch the Pitch and Show the Code

If you are a developer advocate, developer evangelist, or a technical founder, your currency is not slides—your currency is code. 

The single biggest mistake I see DevRel professionals make is spending the first fifteen minutes of their talk pitching the "corporate vision." They show market cap charts, list logos of Fortune 500 customers, and explain how their cloud-native platform is going to revolutionize global enterprise synergy. It’s a total snooze fest. The moment you show a slide that looks like it was designed by a marketing committee, you lose the room.

If your tool has an API, show the curl requests. If your tool has an SDK, open an editor and write some functions. Walk them through the actual imports, the initialization, the error handling, and the response payloads. Developers think in terms of logic and execution; they want to see what the developer experience (DX) actually feels like. 

```javascript
// This is what they want to see: actual implementation
import { ZenClient } from '@zencoder/sdk';

const client = new ZenClient({ apiKey: process.env.ZEN_API_KEY });

async function runDemo() {
  // Real code, clean imports, direct error handling
  try {
    const result = await client.pipelines.deploy('main-production');
    console.log(`🚀 Deployment active: ${result.url}`);
  } catch (error) {
    console.error('😭 The demo gods have struck again:', error.message);
  }
}
```

Show them how your tool fits into their existing stack. If you are showing how to integrate your API, don't show it in isolation. Show how it hooks into an Express app, how it manages state in a React component, or how it runs inside a Docker container. Connect your product to the tools they already use and love. That is how you build real, lasting technical credibility.

## Rule #2: The Terrifying Art of Live Coding

There is a running joke in DevRel circles that live coding is a great way to shave five years off your life expectancy. It is terrifying, highly unpredictable, and is a surefire way to summon the mischievous demo gods of conference Wi-Fi failures. 

But here is the secret: **you should do it anyway.**

Live coding is the ultimate badge of authenticity. When you stand on stage and write code from scratch in front of an audience, you are showing them that you aren't just reading a script written by a copywriter. You are showing them that you are a real builder who knows how to use the tool in real-time. It creates a sense of shared tension and excitement in the room. The audience is rooting for you to succeed.

And if (and when) the demo breaks? That is actually where the real magic happens. 

If your demo fails because of a typo or a configuration issue, don't panic or try to cover it up. Take a deep breath, laugh at yourself, and debug it live on screen. Explain your thought process as you look at the error log. When developers see how you approach a bug, how your tool’s error messages actually help you resolve the issue, and how you get things back on track, they learn more about your product than they ever would from a perfect, sterile, pre-recorded video. A beautifully recovered failure builds ten times more trust than a flawless, fake demo.

## Rule #3: Respect the Attention Economy

Most developers at a conference are running on four hours of sleep, three energy drinks, and a severe case of cognitive overload. Their attention is an incredibly scarce resource. Respect it.

This means keeping your slides clean, simple, and high-contrast. Ditch the white backgrounds that blind people in dark auditoriums; use dark mode (always!). Keep your code snippets large enough to be read from the back row. If someone has to squint to read your font size, they will look down at their phone instead. Use syntax highlighting that actually highlights the exact lines of code you are talking about, rather than dumping a massive wall of unformatted text onto a slide.

Furthermore, get straight to the point. Don’t start with a ten-minute autobiography of your life story. Nobody cares that you started coding on a Commodore 64 or that you love IPAs and hiking with your dog. Start with the **pain**. 

Define the exact, annoying, frustrating problem that they have likely stayed up until 3:00 AM trying to fix. Once you have established solidarity through shared developer suffering—like configuring Webpack, fighting with CORS headers, or trying to scale a database cluster—only then should you introduce your tool as the elegant solution to that pain.

## The Perfect 45-Minute Presentation Blueprint

Over the years of speaking at events ranging from local meetups to major global keynotes, I have developed a highly reliable structure for technical presentations. Here is the exact blueprint:

1. **The Hook (0 - 5 minutes)**: Present the painful, relatable problem. Make a joke about it. Establish solidarity.
2. **The High-Level Architecture (5 - 15 minutes)**: Explain how the problem is typically solved and why those current solutions are broken or inefficient. Use clean diagrams, not walls of text.
3. **The Meaty Live Demo (15 - 35 minutes)**: Open the terminal, write the code, run the build, and show the working result. Keep the code minimal but functional.
4. **The Gotchas and Limitations (35 - 40 minutes)**: Be brutally honest. Tell the audience where your tool *isn't* a good fit, what its limitations are, and what the scaling bottlenecks look like. This level of transparency is incredibly rare and builds massive trust.
5. **The Call to Action (40 - 45 minutes)**: Give them a single, clean URL where they can clone the GitHub repo, read the quickstart guide, and get started in under five minutes.

## Your Job is Education, Not Conversion

As a developer evangelist, you are not a salesperson. Your ultimate goal is not to close a contract or hit a sales quota on stage; your goal is to educate, inspire, and build trust. 

If people walk out of your presentation thinking, "Wow, that speaker really understood my problems and showed me a genuinely cool way to solve them," you have won. They will remember your name, they will remember your company, and the next time they are building a project that needs your specific capability, they will type your URL into their browser. Ditch the corporate script, embrace the beautiful chaos of live code, and always keep it real.

## Key Takeaways

- **[Lead with the code]**: Skip the corporate marketing slides and get straight to the code snippets, terminal commands, and architecture diagrams.
- **[Authenticity over perfection]**: Live coding builds unmatched trust and credibility, even when things break and you have to debug them live.
- **[Shared suffering builds bonds]**: Anchor your presentation around a real, frustrating pain point that your audience has personally experienced.
- **[Radical transparency wins]**: Discussing your product's limitations and edge cases makes your overall presentation infinitely more believable and respected.

## Frequently Asked Questions

**Q: What is the absolute best way to prepare for a live coding demo?**
A: Practice it until it is in your muscle memory, then practice it three more times. Create step-by-step git branches (e.g., `step-1-start`, `step-2-complete`) so that if the network completely dies or you get stuck, you can easily checkout the next branch and keep the presentation moving.

**Q: How do I handle Q&A sessions when someone asks a highly specific or confrontational question?**
A: Never get defensive. If someone points out a flaw or asks an incredibly niche question, say: "That's a fantastic point. I haven't tested that specific edge case yet. Let’s meet at the speaker pavilion right after this talk so we can pull up the repo and look at it together." It defuses the tension and moves the conversation to a productive 1-on-1 setting.

**Q: How do I get my talk proposals accepted by major tech conference committees?**
A: Focus your proposal on educational value, not your product. Conference organizers hate product pitches. Write a title and abstract that promises to teach the audience a specific, highly useful skill or architectural pattern (e.g., "Scaling WebSockets to 100k Concurrent Users" rather than "How to use OurSocketCompany's API").

---

*If this made you think, it'll do even more when shared. Hit that subscribe button — I write about developer relations and software engineering every week and I promise to keep it real.*

*— [Shantanu Vishwanadha](https://substack.com/@thecoderpanda)*
