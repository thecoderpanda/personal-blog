---
title: "Web3.js vs Ethers.js: Which Library Should You Use in 2019?"
subtitle: "One is the battle-tested giant we all love to complain about. The other is the lean, typed challenger taking over the ecosystem."
date: "2019-04-12"
author: "Shantanu Vishwanadha"
authorUrl: "https://substack.com/@thecoderpanda"
tags: ["tutorials", "ethereum", "web3js", "ethersjs", "javascript"]
seoTitle: "Web3.js vs Ethers.js: 2019 Ethereum Developer Guide"
seoDescription: "An in-depth technical comparison of Web3.js and Ethers.js for Ethereum developers in 2019. Compare bundle sizes, architecture, and code syntax."
featuredImage: "https://images.unsplash.com/photo-1555066931-4365d14bab8c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
imageAlt: "Computer screen showing code in a dark environment representing developer workspace"
category: "tutorials"
readingTime: "7 min read"
slug: "web3js-vs-ethersjs-which-library-should-you-use"
---

If you have spent any time building decentralized applications (dApps) on Ethereum, you have undoubtedly wrestled with Web3.js. It is the undisputed veteran of the ecosystem. It has been around since 2015, shipping with early browser extensions and forming the foundation of almost every Ethereum tutorial, boilerplate, and stack-overflow answer in existence. 

But let’s be honest. Web3.js has also been the source of some of the most spectacular developer meltdowns in history. 

Between the endless "Web3 1.0.0-beta.x" breaking changes, the mysterious callback errors, the massive bundle sizes, and TypeScript definitions that feel like they were written by a random number generator, building with Web3.js can feel like trying to assemble a Lego set while wearing oven mitts.

Fortunately, the JavaScript ecosystem doesn’t stay static for long. 

Over the last year, a lean, highly polished alternative has been quietly stealing the hearts of dApp developers: **Ethers.js**, created by Richard Moore. It’s small, it’s written from scratch in TypeScript, and it introduces an entirely different mental model for interacting with the blockchain.

If you are spinning up a new Ethereum project in 2019, you face a critical architectural decision: do you stick with the legacy giant, or do you migrate to the modern challenger? 

Let’s put both libraries in the ring, dissect their architectures, look at some code, and see which one deserves a place in your package.json.

---

## 1. The Tale of the Tape

Before we dive into the code, let’s look at the raw metrics.

| Metric | Web3.js (v1.0.0-beta.55) | Ethers.js (v4.0.0) |
| :--- | :--- | :--- |
| **Bundle Size (Minified + Gzipped)** | ~300 KB | ~88 KB |
| **Primary Language** | JavaScript | TypeScript |
| **License** | LGPLv3 | MIT |
| **Dependencies** | 30+ nested packages | Zero (all modular/in-house) |
| **ENS Support** | Manual resolution | Native, out-of-the-box |

The first thing that hits you is the bundle size. Web3.js is an absolute unit. It brings along a massive tree of dependencies, including heavy cryptographic utilities that can bloated your frontend bundle. Ethers.js, on the other hand, is an elegant, modular package that clocks in at less than a third of Web3's footprint. If you care about loading times on mobile devices or slow network connections, Ethers.js starts with a massive lead.

---

## 2. Architectural Philosophies: Unified vs. Separated

The biggest difference between these two libraries is their conceptual approach to blockchain interaction.

### The Web3.js Model: The Omnipresent Instance
Web3.js assumes there is a single, unified `web3` object that handles everything. This object represents both your connection to the node, your account state, and your cryptographic utilities. If you want to change the network, or swap out a private key, you mutate the state of this main web3 instance. This tightly coupled approach makes testing difficult and leads to confusing state bugs when dealing with multiple networks or wallets.

### The Ethers.js Model: Separation of Concerns
Ethers.js splits the world into three highly focused, logical components:
1.  **Provider**: A read-only connection to the Ethereum blockchain. It allows you to query blocks, look up transaction history, and read state. It has absolutely no access to private keys or signing capabilities.
2.  **Signer**: An abstraction of an Ethereum account. It has access to a private key (or a hardware wallet/extension) and can sign transactions and messages.
3.  **Contract**: An abstraction of a deployed smart contract, allowing you to easily call read methods (via a Provider) or send write transactions (via a Signer).

This separation of concerns makes Ethers.js incredibly clean to work with. It mirrors the actual physical separation between node providers (like Infura) and user wallets (like MetaMask).

---

## 3. Code Duel: Fetching a Balance

Let’s see how this architectural difference translates into real-world code. Here is how we connect to MetaMask and retrieve an account's Ether balance.

### Fetching Balance with Web3.js
```javascript
const web3 = new Web3(window.ethereum);
const fetchBalanceWeb3 = async (address) => {
  const balanceWei = await web3.eth.getBalance(address);
  const balanceEth = web3.utils.fromWei(balanceWei, "ether");
  return balanceEth;
};
```

### Fetching Balance with Ethers.js
```javascript
const provider = new ethers.providers.Web3Provider(window.ethereum);
const fetchBalanceEthers = async (address) => {
  const balanceWei = await provider.getBalance(address);
  const balanceEth = ethers.utils.formatEther(balanceWei);
  return balanceEth;
};
```

Both approaches are fairly concise, but notice how Ethers.js uses the explicit `Web3Provider` to wrap MetaMask’s injected RPC provider, keeping the read operations cleanly bound to the `provider` instance.

---

## 4. Code Duel: Interacting with a Smart Contract

Now let’s look at a more complex scenario: instantiating a smart contract and executing a transaction that modifies state on-chain.

### Contract Interaction with Web3.js
```javascript
const web3 = new Web3(window.ethereum);
const contract = new web3.eth.Contract(abi, contractAddress);
const executeTransactionWeb3 = async (newValue) => {
  const accounts = await web3.eth.getAccounts();
  const tx = await contract.methods.setValue(newValue).send({
    from: accounts[0],
    gasPrice: "20000000000"
  });
  return tx.transactionHash;
};
```

### Contract Interaction with Ethers.js
```javascript
const provider = new ethers.providers.Web3Provider(window.ethereum);
const signer = provider.getSigner();
const contract = new ethers.Contract(contractAddress, abi, signer);
const executeTransactionEthers = async (newValue) => {
  const tx = await contract.setValue(newValue, {
    gasPrice: ethers.utils.parseUnits("20", "gwei")
  });
  const receipt = await tx.wait();
  return receipt.transactionHash;
};
```

The difference here highlights the power of Ethers' architecture. In Ethers.js, we instantiate the contract with a `signer` directly. The library understands that any call to a state-changing method (like `setValue`) requires a signature, so it automatically signs and broadcasts the transaction using that signer. 

In Web3.js, you have to manually fetch the user's accounts, pass the sender address explicitly in the transaction options, and execute it through the nested `methods.methodName().send()` chain. Ethers' syntax feels native, while Web3 feels like an RPC wrapper.

---

## 5. First-Class Features in Ethers.js

Beyond cleaner syntax, Ethers.js includes several features that make it feel like a modern library built for actual dApp development in 2019:

*   **Native ENS Support**: In Ethers.js, ENS is treated as a first-class citizen. Wherever a method accepts an Ethereum address, you can pass an ENS name (e.g. `thecoderpanda.eth`) instead, and Ethers will automatically resolve it behind the scenes.
*   **Built-in Mnemonic Wallet**: Ethers has incredibly robust utilities for generating, importing, and exporting BIP-39 mnemonic phrases and HD wallets natively, without requiring external libraries like `bip39` or `hdkey`.
*   **Flawless TypeScript Support**: Because the library is written in TypeScript, you get autocomplete, hover-documentation, and compile-time type-safety right inside your IDE without installing external, broken typings.

---

## The Verdict

In 2019, the verdict is clear. 

If you are building a **brand new dApp**, choose **Ethers.js**. Its smaller bundle size, robust separation of concerns, native TypeScript support, and elegant API will save you hours of development friction and keep your application fast and responsive.

The only scenario where you should stick with **Web3.js** is if you are maintaining a massive, complex legacy codebase that is heavily tied to Web3’s specific patterns, or if you are using frameworks (like Truffle) that do not yet fully support Ethers out-of-the-box.

The era of having to settle for a bloated, buggy Ethereum frontend library is over. Ethers.js has raised the bar for developer experience in the Web3 space. Do yourself a favor: open up your terminal, type `npm install ethers`, and don’t look back.
