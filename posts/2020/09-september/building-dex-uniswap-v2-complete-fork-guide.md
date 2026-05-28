---
title: "Building a DEX on Uniswap v2: The Complete Fork Guide"
subtitle: "A developer walkthrough of the Uniswap v2 core contracts, explaining factories, routers, and ERC-20 pair pools for builders."
date: "2020-09-21"
author: "Shantanu Vishwanadha"
authorUrl: "https://substack.com/@thecoderpanda"
tags: ["solidity", "uniswap", "dex", "tutorials"]
seoTitle: "Uniswap v2 Fork Tutorial: Build Your First DEX"
seoDescription: "A technical walkthrough for solidity developers on how to fork and deploy Uniswap v2 core and router smart contracts on a local Ethereum network."
featuredImage: "https://images.unsplash.com/photo-1516116216624-53e697fedbea?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
imageAlt: "Computer screen showing structured code editor with syntax highlighting, representing developer building smart contracts"
category: "tutorials"
readingTime: "7 min read"
slug: "building-dex-uniswap-v2-complete-fork-guide"
---

After SushiSwap’s hostile migration drained nearly a billion dollars of liquidity in a single day, every Solidity developer with a laptop and a caffeine addiction suddenly decided they wanted to build their own Decentralized Exchange (DEX). 

And why not? The code is completely open-source. There are no gatekeepers. 

But if you actually pull down the Uniswap v2 repositories, you’ll quickly realize that while the constant product formula ($x \cdot y = k$) is mathematically elegant in its simplicity, the actual multi-contract architecture is a masterclass in modularity, security, and gas-optimization. It can be incredibly intimidating if you don't know where to look.

In this tutorial, we are going to do a deep-dive walkthrough of the Uniswap v2 smart contract architecture. We’ll cover how Core and Periphery work together, how liquidity pools function under the hood, and we will walk through the notorious, hair-pulling compilation gotchas that have left many a developer crying into their keyboard at 3 AM.

## The Architectural Philosophy: Core vs. Periphery

Uniswap v2 is split into two distinct repositories: **Core** and **Periphery**. This separation is not arbitrary—it is a critical security and gas-efficiency design pattern.

1. **`uniswap-v2-core`**: This repository contains the fundamental, consensus-critical, and highly audited smart contracts. They are written to be as lightweight and minimal as possible to reduce gas costs and minimize the attack surface. They hold the actual ERC-20 tokens, enforce the math, and mint LP tokens. **Once deployed, you never change or upgrade these.**
2. **`uniswap-v2-periphery`**: This repository contains helper contracts that make it easy for users and frontend applications to interact with Core. The primary contract here is the Router. It handles safety checks, multi-hop swap routing (e.g., swapping BAT to DAI by routing through WETH), and handles complex transfers. Periphery contracts can be upgraded or replaced with newer, more optimized versions without affecting the underlying liquidity pools.

```mermaid
flowchart LR
    A[Frontend/User] -->|Calls swaps/liquidity| B[UniswapV2Router02 Periphery]
    B -->|Computes address & transfers| C[UniswapV2Factory Core]
    B -->|Calls swap() / mint()| D[UniswapV2Pair Core]
    C -->|Deploys via create2| D
```

## Deep-Diving the Core Contracts

Let’s look at the three main contracts that live inside Core:

### 1. `UniswapV2ERC20.sol`
Every liquidity pool in Uniswap v2 is itself an ERC-20 token. When you add liquidity to an ETH-USDC pool, the contract mints "ETH-USDC LP" tokens to your address to represent your share of that pool. This contract implements standard ERC-20 functionality but adds **EIP-2612 permit signatures**. This allows users to authorize LP token transfers via a cryptographic signature instead of having to submit a separate, gas-consuming `approve()` transaction first.

### 2. `UniswapV2Pair.sol`
This is the heart of the AMM. Each pair contract manages a single pool containing exactly two ERC-20 tokens (e.g., tokenA and tokenB). It implements the classic Constant Product Market Maker formula:

$$x \cdot y \ge k$$

Where $x$ and $y$ are the reserves of tokenA and tokenB, and $k$ must remain constant (or increase due to the 0.3% trading fee).
The swap function is incredibly low-level and does not perform safety routing; it expects the caller (the Router) to have already transferred the input tokens to its address before calling `swap()`. It then performs an optimistic transfer of the output tokens and asserts that the constant product invariant holds true at the end of the execution block.

### 3. `UniswapV2Factory.sol`
The Factory is a registry. Its sole job is to deploy new `UniswapV2Pair` contracts for any two tokens and to keep track of their addresses. It uses the EVM's `create2` opcode to deploy pair contracts, which ensures that a specific token pair (tokenA, tokenB) will always resolve to the exact same contract address, regardless of when or where it is deployed.

## The Router: The Developer’s Best Friend

If you tried to interact with `UniswapV2Pair` directly, you’d probably lose all your money. It does not protect you from slippage, it does not refund excess tokens, and it cannot handle multi-hop swaps. 

That's where `UniswapV2Router02.sol` comes in. It provides user-friendly functions like `addLiquidityETH` and `swapExactTokensForTokens`. 

When you want to swap, the Router calculates the expected output reserves, performs safety checks to ensure your transaction won't suffer massive front-running or slippage, pulls the tokens from your wallet, transfers them to the correct `Pair` contract, and triggers the raw, low-level swap.

## The Notorious Gotcha: The `INIT_CODE_HASH`

If you try to compile Uniswap v2 from scratch, you are guaranteed to hit the dreaded **Router-Pair Address Mismatch** bug. 

To save gas, the `UniswapV2Library.sol` (which is compiled inside the Router) calculates the address of a pair contract off-chain using the `create2` formula instead of calling the Factory's `getPair()` storage map. 

The library uses a hardcoded hash representing the creation bytecode of the `UniswapV2Pair` contract. It looks like this in the library:

```solidity
// UniswapV2Library.sol - Conceptual Pair Address derivation
function pairFor(address factory, address tokenA, address tokenB) internal pure returns (address pair) {
    (address token0, address token1) = sortTokens(tokenA, tokenB);
    pair = address(uint(keccak256(abi.encodePacked(
        hex'ff',
        factory,
        keccak256(abi.encodePacked(token0, token1)),
        hex'96e8ac4277198ff8b6f785478aa9a39f403cb768dd02cbee326c3e7da348845f' // <--- THE INIT CODE HASH
    ))));
}
```

Here is the kicker: **If you modify even a single character of comment in `UniswapV2Pair.sol`, or compile it with a different Solidity compiler version, or change the optimizer settings, the bytecode of your Pair contract changes.**

If the bytecode changes, its `keccak256` hash changes. If you do not update the hardcoded hex string in your library to match your new `INIT_CODE_HASH`, your Router will calculate the wrong pair addresses. It will try to send swaps to contracts that do not exist, and every transaction will revert with no helpful error message.

### How to solve this:
Before deploying your Router, compile your `UniswapV2Pair` contract. Write a script to fetch the deployed runtime bytecode or compute the hash of the contract's creation bytecode. 

Here is a quick script to find your exact hash:

```javascript
const { ethers } = require("hardhat");

async function main() {
  const UniswapV2Pair = await ethers.getContractFactory("UniswapV2Pair");
  const bytecode = UniswapV2Pair.bytecode;
  const initCodeHash = ethers.utils.keccak256(bytecode);
  console.log("Your INIT_CODE_HASH is:", initCodeHash);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
```

Take that resulting hash (remove the `0x` prefix if necessary) and copy-paste it directly into your `UniswapV2Library.sol` file *before* compiling and deploying your Router.

## Deployment Order

When you are ready to launch your DEX on a local testnet or mainnet, you must deploy the contracts in this exact order:

1. **Deploy your WETH (Wrapped Ether) contract** (if it doesn't already exist on your target network).
2. **Deploy the `UniswapV2Factory`** passing your fee-to-setter governance address.
3. **Compute your `UniswapV2Pair` init code hash** using the script above.
4. **Update the hash in `UniswapV2Library.sol`**.
5. **Deploy the `UniswapV2Router02`** contract, passing the Factory address and the WETH address as constructor arguments.

Congratulations. You have just deployed a fully functional, highly secure, decentralized exchange. Go build a beautiful front-end interface, bootstrap some liquidity, and watch out for those vampires!
