---
title: "JPMorgan Just Built a Blockchain. Here's Why That's Complicated."
subtitle: "Jamie Dimon once called Bitcoin a fraud. Now his bank has its own coin. Let's talk about Quorum, JPM Coin, and the comedy of enterprise ledgers."
date: "2019-03-04"
author: "Shantanu Vishwanadha"
authorUrl: "https://substack.com/@thecoderpanda"
tags: ["blockchain", "cryptocurrency", "jpmorgan", "finance", "quorum"]
seoTitle: "JPMorgan JPM Coin & Blockchain: Why It's Complicated"
seoDescription: "Jamie Dimon called Bitcoin a fraud, but JPMorgan just built its own blockchain. An in-depth, witty look at Quorum, JPM Coin, and permissioned blockchains."
featuredImage: "https://images.unsplash.com/photo-1518546305927-5a555bb7020d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
imageAlt: "A gold Bitcoin coin on a dark reflective surface"
category: "blockchain"
readingTime: "6 min read"
slug: "jpmorgan-built-blockchain-why-thats-complicated"
---

Life comes at you fast. But if you’re a legacy banking executive, life comes at you at the speed of a high-frequency trading algorithm running on a microwave link.

Let’s rewind to 2017. The crypto markets were in a state of absolute, unhinged euphoria. People were mortgaging their homes to buy digital cats, and initial coin offerings (ICOs) were raising $50 million based on a whitepaper written on a napkin. In the middle of this chaos stood Jamie Dimon, the formidable CEO of JPMorgan Chase. He didn't mince words. He famously declared Bitcoin a "fraud" that would "blow up," adding that he’d fire any JPMorgan trader caught dealing in it for being "stupid."

Fast forward to early 2019. The market is cold, the "crypto winter" is in full swing, and my portfolio looks like a crime scene. Yet, what does JPMorgan Chase do? They announce the launch of **JPM Coin**, running on their very own, custom-built blockchain platform called **Quorum**.

You honestly can’t make this stuff up. The corporate pivot is a beautiful, hilarious thing to witness. But behind the ironies and the easy Twitter dunking lies a deeply fascinating, technically complex, and somewhat frustrating development. JPMorgan has actually built something real, but it is about as far from the Cypherpunk dream as a corporate PowerPoint presentation is from a rave.

Let’s unpack what JPM Coin and Quorum actually are, why enterprise blockchain is such a contradictory beast, and what this means for developers who are actually building in this space.

---

## The Glorified Excel Sheet: JPM Coin vs. Real Crypto

First, let’s clear up the massive pile of marketing hype. JPM Coin is not "cryptocurrency" in any sense that a normal human being would understand it. You can't buy it on Coinbase, you can't stake it for 20% APY, and you certainly can't use it to buy a coffee or a digital piece of art. 

In reality, JPM Coin is a **digital token representing USD held in designated JPMorgan accounts**. 

Think of it as a closed-loop settlement system. If Corporate Client A in Tokyo wants to send $100 million to Corporate Client B in New York, they don't use the ancient, creaking SWIFT network, which takes three days, a mountain of paperwork, and an exorbitant fee. Instead, they deposit USD with JPM, get JPM Coins on the Quorum ledger, transfer those coins instantly to Client B's wallet, and Client B redeems those coins back into actual greenbacks with JPM. 

It's instant. It's cheap. It runs 24/7/365. 

But here’s the kicker: it’s entirely centralized. JPMorgan is the issuer, the operator, the validator, and the police. If they don't like your transaction, they hit `Ctrl+Z` and it’s gone. It is a blockchain where the "trustless" element has been replaced by "Trust Us, We're a 200-Year-Old Global Megabank." 

To a pure crypto enthusiast, this is heresy. It’s an expensive, over-engineered database. Why not just use a centralized PostgreSQL database with a fast API?

The answer is both simple and complicated: **multi-party coordination**. Large enterprises don't trust each other, and they definitely don't want to run their businesses on a database owned and operated by a single competitor. A shared, cryptographically verified ledger allows them to interact without a single shared point of failure, even if that ledger is completely closed to the general public.

---

## Under the Hood: The Weird World of Quorum

If you are a developer, this is where it gets interesting. JPMorgan didn’t hire a bunch of PhDs to invent a brand-new consensus mechanism from scratch. They did what any sensible engineer does when faced with a tight deadline: they went to GitHub and clicked "Fork."

Specifically, they forked **Go-Ethereum (geth)**, the primary client for the Ethereum network. 

Yes, JPMorgan's cutting-edge blockchain is literally a modified version of Ethereum. They took the EVM (Ethereum Virtual Machine) and made some drastic, highly corporate modifications.

1. **Consensus Replacement**: Ethereum currently runs on Proof of Work (PoW) and is planning a move to Proof of Stake (PoS). Both require miners or validators spending capital and energy to secure the network. JPMorgan has no interest in paying gas fees to random teenage miners in Russia. So, they ripped out PoW and replaced it with **IBFT (Istanbul Byzantine Fault Tolerance)** and **Raft** consensus mechanisms. In these models, blocks are minted instantly by a set of pre-approved, authorized nodes. There are no mining rewards, no gas market, and zero latency. 

2. **The Tessera Privacy Engine**: In public Ethereum, every single transaction is visible to the entire world. If a bank did that, they would be shut down by regulators within ten seconds. To solve this, Quorum uses a companion engine called **Tessera** (written in Java, because of course banks love Java). Tessera encrypts transaction payloads and only shares them with the specific nodes involved in that transaction. Other nodes on the network merely validate the block hashes without seeing the underlying financial data.

It’s an impressive piece of engineering, but it creates a strange paradox. They’ve built a highly secure, private, instant transaction engine by stripping out almost everything that makes a blockchain decentralized. 

It is "blockchain" in name, but "distributed enterprise software" in practice.

---

## The True Alpha: Capital Efficiency and SWIFT Killers

So, if it’s just a glorified database with an EVM wrapper, why is JPMorgan spending millions of dollars developing and promoting it? Are they just trying to look cool for the tech media?

Not quite. There is a massive, multi-billion-dollar incentive here, and it’s all about **liquidity and settlement times**.

In the traditional banking world, moving money internationally is a nightmare. When a bank sends a cross-border wire, the money doesn’t actually fly through the air. It moves through a series of "correspondent banks." Each bank along the chain has to manually reconcile their ledgers, which takes days. Because of this lag, banks have to hold billions of dollars of idle capital in "nostro/vostro" accounts all over the world just to guarantee liquidity.

That is dead capital. It just sits there, earning next to nothing, waiting for settlements to clear.

If JPMorgan can move those transactions onto an instant ledger like Quorum, that settlement lag drops from three days to three seconds. Suddenly, those billions of dollars of locked-up capital are freed up. They can be loaned out, invested, or used to generate actual yield. 

To a bank that handles over $5 trillion in transactions every single day, even a tiny optimization in settlement speed translates into hundreds of millions of dollars in pure profit annually. They are not doing this to support the decentralized revolution; they are doing this because SWIFT is an ancient dinosaur, and they want to own the gun that shoots it.

---

## What This Means for Developers: EVM is the Standard

If you are a developer sitting in your room, drinking cold brew, and wondering whether you should learn Solidity or stick to building React frontends, JPMorgan’s announcement is actually a massive buy signal.

It proves that the **Ethereum Virtual Machine (EVM)** is rapidly becoming the industry standard for smart contract execution. 

By building Quorum on top of Geth, JPMorgan has implicitly acknowledged that Ethereum has won the developer mindshare. A smart contract developer writing Solidity for public Ethereum can jump over to Quorum with almost zero learning curve. They use the same compilers, the same libraries (like web3.js or ethers.js), and the same mental models.

Enterprise blockchain might be a centralized, sanitized version of the crypto dream, but it uses the exact same tools. 

So don't roll your eyes too hard when you see Jamie Dimon bragging about JPM Coin. Sure, it's corporate theater, and yes, it’s highly ironic. But it’s also a massive validation of the open-source developer ecosystem. The suits are playing catch-up, and they are using our code to do it.

Now, if you’ll excuse me, I’m going to go check if my MetaMask wallet has miraculously recovered. (Spoiler alert: it hasn't).
