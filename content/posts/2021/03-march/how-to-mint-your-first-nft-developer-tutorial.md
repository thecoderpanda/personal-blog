---
title: "How to Mint Your First NFT: A Complete Developer Tutorial"
subtitle: "Step-by-step code tutorial to write, deploy, and mint an ERC-721 token on Ethereum."
date: "2021-03-12"
author: "Shantanu Vishwanadha"
authorUrl: "https://substack.com/@thecoderpanda"
tags: ["tutorials", "solidity", "ethereum", "nft"]
seoTitle: "How to Mint an NFT: Solidity Developer Tutorial"
seoDescription: "Want to code your own NFT? Follow this complete, step-by-step developer guide to writing and deploying an ERC-721 smart contract on Ethereum."
featuredImage: "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
imageAlt: "A computer screen with developer code in an IDE"
category: "tutorials"
readingTime: "6 min read"
slug: "how-to-mint-your-first-nft-developer-tutorial"
---

# How to Mint Your First NFT: A Complete Developer Tutorial

> **TL;DR:** Stop buying other people's overpriced JPEGs and start coding your own. In this complete, step-by-step developer tutorial, we will write, compile, and deploy a custom, gas-optimized ERC-721 smart contract on Ethereum using Solidity, Hardhat, and OpenZeppelin.

While the rest of the world is busy chasing speculative trends, changing their avatars, and getting rugged on sketchy Discord channels, we are going to do what builders do: we are going to open our IDE, write some code, and understand the technical mechanics of the non-fungible token standard from first principles. If you can write basic Javascript or have a passing familiarity with object-oriented programming, you can write an Ethereum smart contract.

The Ethereum developer ecosystem has improved dramatically over the last year. Gone are the days of manually dealing with raw bytecode, fighting with early-stage compilers, and praying that your deployment script doesn't swallow your entire life savings in gas fees. Today, tools like Hardhat and libraries like OpenZeppelin allow us to spin up secure, industry-standard smart contracts in minutes. Let’s build a production-grade ERC-721 contract, deploy it to a test network, and mint an NFT.

## Setting Up Your Development Environment

Before we write our first line of Solidity, we need to set up our workstation. We will use Hardhat, an advanced development environment for compiling, deploying, testing, and debugging Ethereum software. Open your terminal, create a new directory for your project, and initialize a Node.js project.

Run these shell commands to initialize your environment:
```bash
mkdir my-first-nft && cd my-first-nft
npm init -y
npm install --save-dev hardhat
```

Once Hardhat is installed, run `npx hardhat` in your directory. Select "create an empty hardhat.config.js" from the interactive menu. Next, we need to install the OpenZeppelin contracts library. This library is the absolute gold standard for secure, battle-tested smart contract implementations, saving us from writing standard ERC-721 boilerplate code from scratch.

Run this command to install the OpenZeppelin contracts:
```bash
npm install @openzeppelin/contracts dotenv
```

## Writing the Smart Contract in Solidity

Now, let's write our contract. Under a new directory named `./contracts`, create a file named `PandaNFT.sol`. We will write a modern Solidity contract using version `0.8.0`. We will inherit from OpenZeppelin's `ERC721URIStorage` contract, which includes standard ERC-721 functions alongside utilities to manage the token's metadata URI.

Here is the complete contract. Note how clean and concise it is when leveraging inheritance:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract PandaNFT is ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;

    constructor() ERC721("PandaNFT", "PANDA") {}

    function mintNFT(address recipient, string memory tokenURI)
        public
        onlyOwner
        returns (uint256)
    {
        _tokenIds.increment();

        uint256 newItemId = _tokenIds.current();
        _mint(recipient, newItemId);
        _setTokenURI(newItemId, tokenURI);

        return newItemId;
    }
}
```

This contract initializes our NFT collection with the name "PandaNFT" and the symbol "PANDA". The `mintNFT` function is restricted to the contract owner via the `onlyOwner` modifier. When called, it increments our auto-managing counter, mints a new unique token ID to the recipient's address, associates that token ID with its decentralized metadata link via `_setTokenURI`, and returns the minted token ID.

## Deploying Your Contract to Rinkeby Testnet

Deploying directly to the Ethereum mainnet right now is incredibly expensive. Instead, we will deploy our contract to the Rinkeby test network, which mirrors the mainnet without using real money. First, we need to write our deployment script. Create a folder named `./scripts` and write the following code into `./scripts/deploy.js`:

```javascript
const hre = require("hardhat");

async function main() {
  const PandaNFT = await hre.ethers.getContractFactory("PandaNFT");
  const pandaNFT = await PandaNFT.deploy();

  await pandaNFT.deployed();

  console.log("PandaNFT contract deployed to:", pandaNFT.address);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

To connect to Rinkeby, we will use Alchemy, a powerful Web3 node provider. Sign up for a free account, create an app on Rinkeby, and copy your HTTP API URL. You will also need a MetaMask wallet with some test ETH, which you can request for free from a Rinkeby faucet. Store your credentials in a `.env` file at the root of your project:

```env
RINKEBY_URL="https://eth-rinkeby.alchemyapi.io/v2/YOUR_API_KEY"
PRIVATE_KEY="YOUR_METAMASK_PRIVATE_KEY"
```

Update your `hardhat.config.js` to read these variables and configure the Rinkeby network:

```javascript
require("@nomiclabs/hardhat-waffle");
require("dotenv").config();

module.exports = {
  solidity: "0.8.0",
  networks: {
    rinkeby: {
      url: process.env.RINKEBY_URL || "",
      accounts: process.env.PRIVATE_KEY !== undefined ? [process.env.PRIVATE_KEY] : [],
    },
  },
};
```

Run the deployment task using Hardhat:
```bash
npx hardhat run scripts/deploy.js --network rinkeby
```

In a few seconds, the terminal will output your live smart contract address on the Rinkeby testnet. You can copy this address, paste it into Rinkeby Etherscan, and watch your deployed bytecode sitting on the blockchain in real-time.

## Key Takeaways
- **Modern Hardhat Tooling**: Hardhat simplifies the entire smart contract lifecyle, automating compilation, script testing, and network deployment.
- **OpenZeppelin Standards**: Utilizing OpenZeppelin's inherited contracts ensures your tokens are fully compliant with marketplace specifications like OpenSea.
- **Auto-Counter Management**: Cryptographic counters must be carefully managed in Solidity to prevent collision and secure deterministic token IDs.
- **Secure Secret Handling**: Never hardcode private keys in your deployment configuration files; always leverage environment variables via `.env`.

## Frequently Asked Questions

**Q: Can anyone call the mintNFT function on my contract?**
A: No. We inherited the `Ownable` contract from OpenZeppelin and attached the `onlyOwner` modifier to the `mintNFT` function. This restricts execution exclusively to the deployer's wallet address.

**Q: What is Rinkeby testnet and why shouldn't I deploy to Ethereum Mainnet?**
A: Testnets are sandboxed simulations of the Ethereum network designed for development. Mainnet gas fees are currently extremely high, and deploying buggy, untested contracts with real money is an easy way to lose thousands of dollars.

**Q: Where should my NFT metadata JSON and image be hosted?**
A: You should host them on decentralized storage platforms like IPFS. Centralized hosting services can suffer from server outages or ownership changes, which would break the link in your contract and make your NFT's media disappear forever.

---

*If this gave you even one useful insight, subscribe — I drop these every week.*

*— [Shantanu Vishwanadha](https://substack.com/@thecoderpanda)*