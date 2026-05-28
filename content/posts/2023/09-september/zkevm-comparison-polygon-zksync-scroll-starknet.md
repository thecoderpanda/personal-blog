---
title: "zkEVM Comparison: Polygon zkEVM vs zkSync vs Scroll vs Starknet"
subtitle: "The layer-2 scaling wars are heating up. Deconstructing the architecture, EVM compatibility levels, and performance proof generation pipelines."
date: "2023-09-12"
author: "Shantanu Vishwanadha"
authorUrl: "https://substack.com/@thecoderpanda"
tags: ["blockchain", "layer-2", "zkevm", "polygon", "zksync", "scroll", "starknet"]
seoTitle: "zkEVM Comparison: Polygon vs zkSync vs Scroll"
seoDescription: "An in-depth technical comparison of Polygon zkEVM, zkSync, Scroll, and Starknet. Examine compiler levels, gas efficiencies, and proof velocities."
featuredImage: "https://images.unsplash.com/photo-1609921212029-bb5a28e60960?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
imageAlt: "A dark Bitcoin and physical crypto coin on a dark textured surface"
category: "blockchain"
readingTime: "8 min read"
slug: "zkevm-comparison-polygon-zksync-scroll-starknet"
---

The Ethereum scaling roadmap has undergone a fascinating evolution. We’ve drifted away from the optimistic rollup hegemony—where Arbitrum and Optimism ruled the TVL charts—straight into the zero-knowledge (zk) promised land. Everyone and their mother is launching a zkEVM. 

If you spent any part of the 2022–2023 bear market writing Solidity, you’ve probably heard that zkEVMs are the "holy grail" of blockchain scaling. They promise the security of zero-knowledge proofs combined with the friction-free developer experience of the Ethereum Virtual Machine (EVM).

But here's the catch: **not all zkEVMs are created equal**. 

Some are bytecode-equivalent; others are language-compatible. Some use compilers to transpile Solidity into zk-friendly instruction sets; others attempt to prove the raw EVM execution trace directly. If you try to deploy a complex Hardhat project with custom assembly opcodes onto one network, it might work flawlessly. On another, it will blow up in your face.

Let’s take off the marketing goggles, dive into the actual compilers, proof systems, and state models, and compare the four heavyweights of the L2 scaling wars: **Polygon zkEVM**, **zkSync Era**, **Scroll**, and **Starknet**.

---

## The Compatibility Spectrum: Vitalik’s Classification

To make sense of these architectures, we have to refer to Vitalik Buterin’s famous classification of zkEVMs. The core tradeoff is simple: **Developer Compatibility vs. Prover Speed**.

*   **Type 1 (Fully Ethereum-equivalent)**: Identical to Ethereum mainnet, down to the hash function and state tree. (Extreme prover overhead).
*   **Type 2 (Fully EVM-equivalent)**: Identical at the bytecode level, but changes external structures like block structures or gas fees to make proving faster.
*   **Type 3 (Almost EVM-equivalent)**: Removes features that are incredibly hard to prove (like certain precompiles or gas-intensive opcodes).
*   **Type 4 (High-level-language equivalent)**: Compiles Solidity directly to a completely different, zk-friendly VM. (Fastest proving times, but highest compatibility friction).

Let’s see where our contestants land on this spectrum.

```
Compatibility (EVM Parity)
    ▲
    │   [Type 2]  Scroll (marching to Type 1)
    │   [Type 2.5] Polygon zkEVM
    │
    │   [Type 4]  zkSync Era (LLVM compilation)
    │   [Custom]  Starknet (Cairo native, Kakarot zkEVM)
    └────────────────────────────────────────────────► Prover Efficiency
```

---

## 1. Scroll: The Dev-First Purist (Type 2)

Scroll has made a name for itself as the most ideologically pure zkEVM. They are not looking to cut corners. Their goal from day one was to build a Type 2 zkEVM that eventually matures into Type 1.

### The Architecture
Scroll parses raw EVM bytecode and generates zero-knowledge proofs for every single opcode execution. They don’t use a middleman transpiler. If you write Solidity, Scroll executes it just like an Ethereum node would, utilizing a custom-designed **Halo2 proof system** over a KZG-based commitment scheme.

### Developer Experience (DX)
Scroll’s DX is outstanding. Because it operates at the bytecode level, you don't need any special compiler plug-ins. Your Hardhat, Foundry, and Truffle configurations work out of the box. Debuggers like `forge test -vvvv` output exact execution traces matching Mainnet.

### The Tradeoff
Prover latency is Scroll’s Achilles' heel. Proving raw EVM opcodes like `KECCAK256` or `SSTORE` (which were never designed with math-based cryptosystems in mind) is mathematically grueling. While Scroll is making strides in hardware acceleration (using GPUs/ASICs), their proof generation costs remain relatively high compared to compiler-based systems.

---

## 2. Polygon zkEVM: The Pragmatic Bytecode Rollup (Type 2.5)

Polygon took a slightly different path. They acquired Hermez in 2021 for $250M, rebranded it, and built a highly efficient bytecode-level zkEVM that operates as a Type 2.5 rollup.

### The Architecture
Instead of proving EVM opcodes directly on Halo2, Polygon zkEVM translates EVM bytecode into a custom intermediate language called **micro-opcodes**. These run on a highly optimized, custom virtual machine (the ROM). 

To define their mathematical constraints, they designed **PIL (Polynomial Identity Language)**. They use a combination of STARK proofs for fast execution proving, which are then compressed into a final SNARK (using Groth16) for cheap verification on L1.

### Developer Experience (DX)
Excellent. Like Scroll, it is bytecode-compatible. Almost all Solidity features, libraries, and tooling work perfectly.

### The Tradeoff
While Polygon’s hybrid STARK-to-SNARK pipeline drastically reduces proof generation costs compared to raw SNARKs, Polygon zkEVM still has to deal with the overhead of replicating the EVM state structure (which uses Merkle Patricia Trees instead of more zk-friendly Sparse Merkle Trees).

---

## 3. zkSync Era: The High-Throughput Pragmatist (Type 4)

zkSync Era (by Matter Labs) took a radically different architectural approach. They decided that replicating the EVM’s legacy baggage inside zero-knowledge math was a sucker’s game. Instead, they built a highly optimized Type 4 zkEVM.

### The Architecture
zkSync Era does **not** interpret EVM bytecode. Instead, they take your Solidity or Yul code and compile it using custom **LLVM-based compilers** (`zksolc`) down to their own custom instruction set called **VM Bytecode**, which runs on the **zkSync Era VM**.

### Developer Experience (DX)
This compilation step introduces some friction. For example:
*   You cannot run raw EVM bytecode. If you use third-party libraries that distribute pre-compiled bytecode, you're out of luck.
*   Addresses behave differently. `CREATE2` salts use different hashing methods, which can break deterministic deployments.
*   You must use their custom compiler plug-ins in Foundry or Hardhat.

However, zkSync compensates for this with groundbreaking native features. Because they aren't bound by EVM legacy constraints, they implemented **native Account Abstraction (EIP-712)** directly into the VM. Every account is a smart contract. Paymasters (which let users pay gas in stablecoins or sponsors pay for gas entirely) work natively without complex ERC-4337 wrappers.

### The Tradeoff
Massive throughput and ultra-cheap proving costs, but at the cost of strict EVM equivalence.

---

## 4. Starknet: The Provable Computing Sovereign (Custom L2)

Let’s get one thing straight: **Starknet is NOT a zkEVM**. 

Starknet is a ZK-Rollup that utilizes STARKs, but it does not use the EVM. Instead, it runs on its own virtual machine (the Starknet OS) and uses **Cairo**, a programming language designed specifically for generating STARK proofs for general computation.

### The Architecture
Starknet compiles Cairo code down to **CASM (Cairo Assembly)**, which executes on the Starknet VM. 

Wait, so why is it in a zkEVM comparison? Because of **Kakarot**. Kakarot is an EVM interpreter written *in* Cairo. When deployed as a smart contract on Starknet, it effectively allows Starknet to act as an EVM-compatible L2. Alternatively, developers can use **Warp**, a transpiler developed by Nethermind that attempts to convert Solidity code directly into Cairo code.

### Developer Experience (DX)
The steepest learning curve in L2. If you deploy natively on Starknet, you have to throw away your Hardhat/Foundry setups, learn Cairo 1.0 (a Rust-like language), and use Starknet-specific tools like Starkli and Scarb. 

If you use Warp or Kakarot, you get EVM compatibility, but with added layers of abstraction and potential edge-case bugs.

### The Tradeoff
Starknet has unparalleled performance, cheap proofs, and native AA. But it represents a complete departure from the Ethereum tooling ecosystem.

---

## Summary Matrix: Making Your Choice

| Metric | Scroll | Polygon zkEVM | zkSync Era | Starknet |
| :--- | :--- | :--- | :--- | :--- |
| **EVM Equivalence** | Type 2 | Type 2.5 | Type 4 | None (Cairo Native) |
| **Proof System** | Halo2 (SNARK) | SNARK + STARK | PLONK (SNARK) | STARK |
| **Tooling Parity** | Out-of-the-box | Out-of-the-box | Requires Compiler | Starknet Ecosystem |
| **Account Abstraction** | ERC-4337 | ERC-4337 | **Native (Built-in)** | **Native (Built-in)** |
| **Prover Latency** | High | Medium | Low | Very Low |
| **State Tree** | Binary Merkle | Sparse Merkle | State Diffs (SMT) | Patricia Trie |

---

## The Verdict: Which Rollup Wins?

If you are a developer and you have a complex, battle-tested DeFi protocol with lots of low-level Solidity assembly and custom contract dependencies, **Scroll** or **Polygon zkEVM** are your safest bets. You can copy-paste your code, run your tests, and deploy in five minutes.

If you are building a consumer-facing app, a Web3 game, or a retail-focused wallet where transaction throughput is critical and user experience (seamless onboarding, gasless transactions via Account Abstraction) is your highest priority, **zkSync Era** is an absolute powerhouse.

If you want to step completely outside the EVM box to leverage maximum mathematical scalability and you aren't afraid of learning Rust-like syntaxes, **Starknet** offers capabilities that standard EVM structures can't touch.

The scaling wars are far from over, but one thing is clear: the zk-rollup landscape is no longer a monolithic block of research papers. It is a highly practical, fragmented, and competitive arena where developers are the ultimate winners.

---

*What is your L2 of choice for this cycle? Drop your arguments on Twitter [@thecoderpanda](https://twitter.com/thecoderpanda) or let me know in the comments below!*
