---
title: "Bitcoin Ordinals: NFTs on Bitcoin Are Real and Here's Why That Matters"
subtitle: "Inscriptions have arrived on the Bitcoin mainnet. Why Bitcoiners are split, and why this is a massive design space shift."
date: "2023-04-28"
author: "Shantanu Vishwanadha"
authorUrl: "https://substack.com/@thecoderpanda"
tags: ["blockchain", "bitcoin", "ordinals", "inscriptions"]
seoTitle: "Bitcoin Ordinals: NFTs on Bitcoin Explained"
seoDescription: "Understand Bitcoin Ordinals and inscriptions. The mechanics of writing digital artifacts directly to satoshis and its impact on miners."
featuredImage: "https://images.unsplash.com/photo-1621416894569-0f39ed31d247?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
imageAlt: "Golden representation of various cryptocurrencies scattered"
category: "blockchain"
readingTime: "8 min read"
slug: "bitcoin-ordinals-nfts-on-bitcoin"
---

If you had told a hardcore Bitcoin maximalist in 2021 that within two years, the Bitcoin blockchain would be flooded with JPEG images of pixelated punks, wizard drawings, and fully playable clones of Doom, they probably would have laughed you out of the room. They might have accused you of being a "shitcoiner" or suffering from severe Ethereum-induced hallucinations.

Bitcoin, after all, was supposed to be the fortress of digital gold. It was a serious, ultra-secure, conservative monetary network designed for peer-to-peer transactions and long-term wealth preservation. It didn't do smart contracts, it didn't do decentralized finance, and it certainly did not do "expensive JPEG profile pictures." 

That was Ethereum's playground.

But in early 2023, a developer named Casey Rodarmor dropped a technical hand grenade into the Bitcoin ecosystem. He introduced **Ordinals** and **Inscriptions**.

Suddenly, "NFTs on Bitcoin" went from an ideological heresy to an undeniable, high-throughput reality. The mainnet is experiencing an unprecedented gold rush, transactions fees are spiking, and the Bitcoin developer community has been fractured into a state of civil war.

Let’s dive into the technical mechanics of Ordinals, understand how Casey Rodarmor hacked the Bitcoin design space, and analyze why this is one of the most critical structural shifts in Bitcoin's history.

---

## The Technical Hack: How Ordinals and Inscriptions Work

To understand Bitcoin Ordinals, you have to understand a fundamental mathematical reality of Bitcoin. 

There will only ever be 21 million Bitcoin. But each Bitcoin is divisible into 100 million smaller units called **satoshis** (or "sats"). This means there are a total of 2.1 quadrillion satoshis in existence.

### 1. Ordinal Theory
Casey Rodarmor’s first breakthrough was **Ordinal Theory**. 

It is a voluntary, off-chain numbering system that tracks individual satoshis from the moment they are mined, across transactions, and through different wallets. By applying a deterministic numbering system (based on the order in which they were minted in coinbase transactions), every single satoshi in existence gets a unique serial number (e.g., `1°0′0″0‴`).

```
                    ┌─────────────────────────┐
                    │  Coinbase Transaction   │
                    └────────────┬────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
   [Satoshi #1]            [Satoshi #2]            [Satoshi #3]
  (Serial: 1°0′0″0‴)      (Serial: 1°0′0″1‴)      (Serial: 1°0′0″2‴)
         │                       │                       │
         ▼                       ▼                       ▼
    Inscribed!               Inscribed!               Standard
    (PNG Image)             (HTML Script)            (Money Sat)
```

Suddenly, satoshis are no longer fungible, interchangeable blobs of digital cash. They are individual, trackable, numismatic artifacts. You can have a "common" sat, a "rare" sat (mined in the first block after a halving), or an "ancient" sat (from the Genesis block).

### 2. Inscriptions
But tracking individual sats is only half the magic. The real game-changer is **Inscriptions**—the process of writing arbitrary data directly onto an individual satoshi.

How do you store a 200KB PNG image or a 1MB file inside a Bitcoin transaction when the traditional OP_RETURN data limit is only 80 bytes?

You leverage two massive, historical Bitcoin upgrades: **SegWit** (2017) and **Taproot** (2021).

* **SegWit** introduced the concept of "witness data," separating the transaction signature and cryptographic proofs from the main transaction data block. Crucially, SegWit offered a 75% fee discount on this witness data.
* **Taproot** relaxed the constraints on witness scripts, allowing developers to write complex smart contracts and store arbitrary data of virtually any size within the witness section of a transaction, as long as the entire transaction fits within the 4MB block size limit.

Casey Rodarmor realized that by wrapping data inside a conditional Taproot script (using an envelope of non-executable Bitcoin opcodes like `OP_FALSE`, `OP_IF`, and `OP_ENDIF`), you could write raw data—binary files, HTML, text, SVG—directly into the witness section.

Here is a conceptual look at how an inscription is structured inside a Bitcoin transaction witness script:

```
OP_FALSE
OP_IF
  OP_PUSH "ord"
  OP_1
  OP_PUSH "image/png"
  OP_0
  OP_PUSH [RAW_IMAGE_BINARY_DATA]
OP_ENDIF
```

Because this script is wrapped in `OP_FALSE OP_IF`, the Bitcoin virtual machine ignores the block during transaction execution. The data doesn't execute as code—it just sits there in the witness section, permanently and immutably written into the distributed ledger of the Bitcoin blockchain.

---

## Ethereum NFTs vs. Bitcoin Inscriptions: The Real On-Chain Difference

To the average user, a Bitcoin Inscription looks exactly like an Ethereum NFT. You open a marketplace, you see a picture, you click buy, and it moves to your wallet.

But under the hood, the engineering philosophy is completely different.

Most Ethereum NFTs are **pointers**. When you buy an ERC-721 token on Ethereum, the smart contract doesn't store your actual image on the Ethereum blockchain (doing so would cost thousands of dollars in gas fees). Instead, the contract contains a `tokenURI` metadata string that points to an external server, a cloud bucket, or a decentralized file storage network like IPFS. 

If the IPFS gateway goes down, or the company hosting the metadata server goes bankrupt, your expensive NFT turns into a broken 404 link.

Bitcoin Inscriptions, on the other hand, are **complete, self-contained, digital artifacts**. 

The raw image bytes, the HTML code, the SVG vector, or the text file is written **directly onto the Bitcoin mainnet**. It does not point to an external server. It does not rely on IPFS. As long as the Bitcoin network exists, your digital artifact will exist on thousands of nodes globally, exactly as you inscribed it. 

It is 100% on-chain, highly secure, fully immutable, and completely resistant to censorship or platform decay.

---

## The Great Maximalist Civil War

The rise of Ordinals has triggered an intense, ideological debate within the Bitcoin community, dividing it into two distinct camps:

### The Purists (The "Spam" Camp)
The classic Bitcoin maximalists view Ordinals as a parasitic attack on the network. 

They argue that Bitcoin’s primary mandate is to be peer-to-peer electronic cash for global financial sovereignty. Storing JPEGs and games on the blockchain is a frivolous waste of precious block space. 

By filling blocks with "spam data," Ordinals are driving up transaction fees, making it too expensive for normal users in developing nations to send monetary transactions. They fear that this block bloat will make it harder for individuals to run full nodes on consumer hardware, compromising Bitcoin's core decentralization.

### The Builders (The "Sovereign Fee" Camp)
The progressive builders and miners view Ordinals as a massive structural victory.

For years, a silent crisis has been looming over Bitcoin: **the long-term security budget.** Every four years, the block reward of newly minted Bitcoin is cut in half. Eventually, the block reward will go to zero, and miners will rely *entirely* on transaction fees to fund their incredibly capital-intensive mining operations. 

If transaction fees are too low, miners will turn off their rigs, the network's hash rate will plummet, and Bitcoin’s security model will fail.

Ordinals have solved this security budget problem overnight. By creating a massive, non-monetary demand for block space, Ordinals are driving up transaction fee revenues for miners. 

In April 2023, miners are experiencing some of their most profitable days in years, purely from transaction fees. 

Furthermore, builders argue that Ordinals make Bitcoin "fun" again. It is bringing a wave of highly creative developers, designers, and capital back from altcoin networks to the most secure, decentralized platform in the world.

---

## Hard-Earned Wisdom: Navigating the New Design Space

As a developer who survived multiple bear markets, I look at Ordinals through a pragmatic lens. 

Whether you love them or hate them, **Inscriptions cannot be censored.** The Bitcoin protocol has no mechanism to distinguish a "serious" monetary transaction from an "unserious" JPEG inscription without introducing subjective centralized filtering, which would destroy the network’s neutral, permissionless architecture.

For developers, Ordinals represent a massive, fresh playground:
* **Writing on-chain applications**: Because you can inscribe HTML, CSS, and Javascript, you can run entire interactive web apps directly from a satoshi.
* **Recursive Inscriptions**: By letting one inscription reference the data of another past inscription (e.g., loading a library like Three.js that has already been inscribed on-chain), you can build complex 3D games and systems while keeping transaction sizes tiny and cheap.

The design space of the world’s oldest blockchain has just experienced a major tectonic shift. The rules of the game are being rewritten in real-time. 

Get your wallets configured, understand the math, and keep building on the most secure ledger on the planet.
