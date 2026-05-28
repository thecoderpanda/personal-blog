---
title: "Polygon (MATIC) Developer Guide: Scaling Ethereum Apps"
subtitle: "A hands-on tutorial for connecting Hardhat, deploying Solidity, and bypassing high gas fees."
date: "2021-04-16"
author: "Shantanu Vishwanadha"
authorUrl: "https://substack.com/@thecoderpanda"
tags: ["tutorials", "polygon", "ethereum", "solidity"]
seoTitle: "Polygon MATIC Developer Guide: Scaling Ethereum"
seoDescription: "Stop paying high gas fees. Learn how to write, compile, and deploy Solidity smart contracts directly on Polygon MATIC with our complete developer guide."
featuredImage: "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
imageAlt: "Developer IDE setup displaying JavaScript and Solidity code"
category: "tutorials"
readingTime: "6 min read"
slug: "polygon-matic-developer-guide-scaling-ethereum"
---

# Polygon (MATIC) Developer Guide: Scaling Ethereum Apps

> **TL;DR:** High Ethereum gas fees are strangling dApp usability, making simple transactions cost hundreds of dollars. This technical developer guide provides a step-by-step tutorial for deploying your Solidity smart contracts on Polygon (MATIC) using Hardhat, allowing you to bypass mainnet congestion while remaining fully EVM-compatible.

Let’s be brutally honest for a second: developing on Ethereum mainnet in April 2021 has become a luxury sport reserved for the ultra-wealthy. If you want to deploy a simple ERC-721 contract, congratulations, that will be $250 in gas fees. Want to swap some tokens on Uniswap? Prepare to sacrifice $80 to the miner gods. We are currently living through a gold-rush bull market where everyone wants to build DeFi dApps and mint NFTs, but the underlying infrastructure is buckling under the pressure. Mainnet congestion is so bad that if you are a developer building a decentralized application with frequent user interactions, you are essentially asking your users to pay a cover fee just to click a button.

But we can't wait around for Ethereum 2.0 and full sharding to save us in 2023. We need scalability right now, and that is why Polygon (formerly MATIC Network) has exploded onto the scene. Polygon provides an incredibly fast, highly secure, and almost gas-free Layer-2 scaling platform that is fully compatible with the Ethereum Virtual Machine (EVM). This means you don't have to learn a new programming language or rewrite your smart contracts. Your Solidity code, your Hardhat scripts, and your Web3 wallets will work on Polygon exactly as they do on Ethereum mainnet—except transactions take seconds and cost less than a fraction of a penny. Let’s roll up our sleeves and build a complete deployment pipeline for Polygon.

## The Scalability Solution: Understanding Polygon’s EVM Architecture
Before we dive into the terminal, let’s quickly unpack how Polygon achieves its magical speed and low fees. Polygon’s flagship scaling solution is the Polygon PoS (Proof-of-Stake) Chain. It is a commit chain that runs parallel to Ethereum mainnet, secured by its own set of professional validators and MATIC staking. 

Unlike a pure sidechain, Polygon regularly commits "checkpoints" to Ethereum mainnet, effectively anchoring its transaction history to the supreme security of Ethereum Layer 1. 

```
  +-------------------------------------------------------------+
  |                   POLYGON EVM ARCHITECTURE                  |
  |                                                             |
  |  [User App] ---> [Polygon PoS Chain (Gas: <$0.01, 2s Block)]|
  |                        |                                    |
  |                        v                                    |
  |             [EVM Execution (Solidity)]                      |
  |                        |                                    |
  |                        v (State Checkpoints)                |
  |             [Ethereum Mainnet (L1 Security)]                |
  +-------------------------------------------------------------+
```

Because Polygon’s PoS chain has a much higher gas limit per block and utilizing a consensus mechanism designed for speed, it can process up to 65,000 transactions per second (TPS).

For a developer, the ultimate selling point is full EVM compatibility. Polygon compiles your Solidity code using the exact same compilers, runs it on a modified EVM client, and supports standard JSON-RPC nodes. This means your existing development toolchain—Hardhat, Truffle, Remix, Ethers.js, and Metamask—is ready to roll out of the box. You do not need to rewrite your application logic; you simply point your deployment configuration to Polygon's network endpoints.

## Step 1: Setting Up the Hardhat Environment
Let’s start by setting up a fresh Hardhat project. In your terminal, initialize a new Node.js directory and install the necessary dependencies:

```bash
mkdir polygon-scaler && cd polygon-scaler
npm init -y
npm install --save-dev hardhat dotenv @nomiclabs/hardhat-waffle ethers
```

Once installed, initialize Hardhat by running `npx hardhat` in your terminal and choose "Create an empty hardhat.config.js" (or choose a basic sample project). We will use a custom Solidity contract for our deployment. Create a folder named `./contracts` and add a new file called `./contracts/SuperToken.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SuperToken {
    string public name = "Super Scalable Token";
    string public symbol = "SUPER";
    uint256 public totalSupply = 1000000 * 10**18;
    mapping(address => uint256) public balances;

    constructor() {
        balances[msg.sender] = totalSupply;
    }

    function transfer(address to, uint256 amount) public returns (bool) {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        balances[to] += amount;
        return true;
    }
}
```

This is a dead-simple, gas-efficient ERC-like token contract. Now we need to configure our Hardhat deployment environment to support both the Polygon Mumbai Testnet and Polygon Mainnet.

## Step 2: Configuring `hardhat.config.js` for Polygon
To deploy to Polygon, we need access to a node. While you can use public RPC endpoints, they are often rate-limited during high-traffic periods. For production, it is highly recommended to use a dedicated provider like Alchemy or Infura to get a free API key.

Create a `./.env` file in your root folder to securely store your private keys and node URLs:

```env
PRIVATE_KEY="your-wallet-private-key"
ALCHEMY_MUMBAI_URL="https://polygon-mumbai.g.alchemy.com/v2/your-api-key"
ALCHEMY_MAINNET_URL="https://polygon-mainnet.g.alchemy.com/v2/your-api-key"
```

Now, update your `./hardhat.config.js` file to parse these environmental variables and map out our target networks:

```javascript
require("@nomiclabs/hardhat-waffle");
require("dotenv").config();

const { PRIVATE_KEY, ALCHEMY_MUMBAI_URL, ALCHEMY_MAINNET_URL } = process.env;

module.exports = {
  solidity: "0.8.4",
  networks: {
    hardhat: {},
    mumbai: {
      url: ALCHEMY_MUMBAI_URL || "https://rpc-mumbai.maticvigil.com",
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
      gasPrice: 8000000000, // 8 Gwei
    },
    polygon: {
      url: ALCHEMY_MAINNET_URL || "https://polygon-rpc.com",
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
      gasPrice: 30000000000, // 30 Gwei
    }
  }
};
```

By adding these network configurations, Hardhat now knows exactly how to sign deployment transactions and where to broadcast them.

## Step 3: Writing the Deployment Script and Going Live
Now let's write a deployment script. Create a directory named `./scripts` and add `./scripts/deploy.js`:

```javascript
const hre = require("hardhat");

async function main() {
  console.log("Starting deployment on network:", hre.network.name);

  const SuperToken = await hre.ethers.getContractFactory("SuperToken");
  const token = await SuperToken.deploy();

  await token.deployed();

  console.log("SuperToken successfully deployed to:", token.address);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

Before we deploy to the live testnet, let’s compile our Solidity code to ensure everything is grammatically correct and syntactically sound:

```bash
npx hardhat compile
```

If compilation succeeds, let's execute our deploy script directly on the Polygon Mumbai Testnet:

```bash
npx hardhat run scripts/deploy.js --network mumbai
```

Within a couple of seconds, you will see a success message in your terminal displaying your freshly minted contract address! You can copy that address, head over to the Mumbai Polygonscan block explorer, and see your transaction confirmed on-chain. Deploying to Polygon Mainnet is exactly the same—simply swap `--network mumbai` with `--network polygon`.

## Key Takeaways
- **EVM Compatibility Moat**: Polygon PoS chain is fully EVM compatible, enabling you to use your existing Solidity contracts, Hardhat scripts, and tooling without code changes.
- **Drastic Cost Reductions**: Transaction fees on Polygon are generally lower than $0.01, making interactive consumer and gaming dApps economically viable.
- **Fast Confirmation Speeds**: With typical block times of roughly 2 seconds, Polygon matches the high-speed execution expectations of modern web applications.
- **Seamless Developer Onboarding**: Standard developer setups like Hardhat require only simple network RPC updates and a wallet private key in `.env` to deploy to Polygon.

## Frequently Asked Questions

**Q: Do I need to buy MATIC to deploy smart contracts on Polygon?**
A: Yes. Just like Ethereum uses ETH for gas, Polygon uses MATIC. However, because gas fees are so low, even 1 MATIC is more than enough to fund dozens of contract deployments and hundreds of subsequent transactions.

**Q: What is the difference between Mumbai and Mainnet?**
A: Mumbai is Polygon's official test network, which mirrors the environment of the live mainnet. You can obtain free test MATIC from public faucets to deploy and test your contracts before spending real money on the live mainnet.

**Q: If I scale with Polygon, do I lose Ethereum's security?**
A: Polygon PoS uses a hybrid security model. While transactions are executed on its own PoS chain, validators submit regular checkpoints of the state to Ethereum Layer 1, providing a solid cryptographic anchor to mainnet.

---

*If this gave you even one useful insight, subscribe — I drop these every week.*

*— [Shantanu Vishwanadha](https://substack.com/@thecoderpanda)*