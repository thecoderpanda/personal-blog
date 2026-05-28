---
title: "Building a Full-Stack DeFi App: From Smart Contract to React Frontend"
subtitle: "A complete step-by-step technical guide to writing Solidity and integrating Ethers.js."
date: "2021-07-08"
author: "Shantanu Vishwanadha"
authorUrl: "https://substack.com/@thecoderpanda"
tags: ["tutorials", "solidity", "react", "ethers-js"]
seoTitle: "Build a Full-Stack DeFi dApp: Solidity & React"
seoDescription: "Ready to go full-stack? Our developer tutorial walks through writing Solidity smart contracts, deploying with Hardhat, and building a React UI with Ethers.js."
featuredImage: "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
imageAlt: "A computer screen glowing with CSS and React code blocks"
category: "tutorials"
readingTime: "6 min read"
slug: "building-full-stack-defi-app-solidity-react"
---

# Building a Full-Stack DeFi App: From Smart Contract to React Frontend

> **TL;DR:** Transition from a smart contract observer to an active Web3 builder. This hands-on, end-to-end tutorial guides you through writing a secure Solidity staking contract, deploying it using Hardhat, and creating a modern React frontend wired up with Ethers.js.

If I see one more "What is a smart contract?" explainer on my feed, I am going to throw my mechanical keyboard out the window. It is mid-2021. The market is absolutely screaming, yield farms are offering quadruple-digit APYs of highly inflationary governance tokens, and the world does not need another high-level overview. We need builders. We need people who can actually write code, push it to a testnet, and build an interface that doesn't look like it was designed in 1998 by a developer on a sugar crash. 

Today, we are going to build a full-stack decentralized staking application (dApp). No hand-waving, no skipping the hard parts. We will write a Solidity smart contract that allows users to stake an ERC20 token and earn rewards, deploy it locally using Hardhat, and then build a React frontend that connects to MetaMask using Ethers.js. If you have been waiting for the perfect project to transition from a speculative observer to an active Web3 developer, this is your moment. Let's get our hands dirty.

## The Smart Contract: SimpleStaker.sol

First, let's write our smart contract. We will create a staking contract where users can deposit a mock token and earn rewards proportional to the duration of their stake. We will use the Hardhat development environment. 

Here is our Solidity code. Note how we track staking balances and calculate rewards mathematically based on block timestamps:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC20 {
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    function transfer(address recipient, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

contract SimpleStaker {
    IERC20 public stakingToken;
    
    mapping(address => uint256) public stakedBalances;
    mapping(address => uint256) public stakingStartTimes;
    
    uint256 public constant REWARD_RATE_PER_SECOND = 100; // Mock rate

    event Staked(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount, uint256 reward);

    constructor(address _stakingToken) {
        stakingToken = IERC20(_stakingToken);
    }

    function stake(uint256 amount) external {
        require(amount > 0, "Cannot stake 0 tokens");
        
        if (stakedBalances[msg.sender] > 0) {
            uint256 pendingReward = calculateReward(msg.sender);
            require(stakingToken.transfer(msg.sender, pendingReward), "Reward transfer failed");
        }
        
        require(stakingToken.transferFrom(msg.sender, address(this), amount), "Token transfer failed");
        
        stakedBalances[msg.sender] += amount;
        stakingStartTimes[msg.sender] = block.timestamp;
        
        emit Staked(msg.sender, amount);
    }

    function withdraw() external {
        uint256 stakedAmount = stakedBalances[msg.sender];
        require(stakedAmount > 0, "No staked tokens to withdraw");
        
        uint256 reward = calculateReward(msg.sender);
        
        stakedBalances[msg.sender] = 0;
        stakingStartTimes[msg.sender] = 0;
        
        require(stakingToken.transfer(msg.sender, stakedAmount + reward), "Withdraw transfer failed");
        
        emit Withdrawn(msg.sender, stakedAmount, reward);
    }

    function calculateReward(address account) public view returns (uint256) {
        if (stakedBalances[account] == 0) return 0;
        uint256 duration = block.timestamp - stakingStartTimes[account];
        return stakedBalances[account] * duration * REWARD_RATE_PER_SECOND / 1e18;
    }
}
```

This contract is straightforward but introduces the fundamental concepts of state, mappings, safety checks, and external ERC20 token interactions.

## Deploying the Smart Contract with Hardhat

Hardhat is the gold standard for Ethereum development. It makes compilation, testing, and deployment incredibly fluid. To set up your Hardhat project, run `npx hardhat` in your terminal and select "Create an empty hardhat.config.js". 

Install your dependencies:
```bash
npm install --save-dev @nomiclabs/hardhat-wethers ethers
```

Next, write a clean deployment script. Save this file as `./scripts/deploy.js`:

```javascript
const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);

  // We assume an ERC20 token is already deployed or deploy a mock token first
  const MockToken = await hre.ethers.getContractFactory("MockERC20");
  const token = await MockToken.deploy(hre.ethers.utils.parseEther("1000000"));
  await token.deployed();
  console.log("MockToken deployed to:", token.address);

  const SimpleStaker = await hre.ethers.getContractFactory("SimpleStaker");
  const staker = await SimpleStaker.deploy(token.address);
  await staker.deployed();
  console.log("SimpleStaker deployed to:", staker.address);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

Run `npx hardhat run scripts/deploy.js --network localhost` to deploy your contracts locally. Make sure to copy the outputted contract addresses; we will need them for our frontend integration.

## Connecting the React Frontend with Ethers.js

With our contracts deployed, it's time to build the user interface. We will write a React component that establishes a connection with the browser's MetaMask extension, fetches the user's staking balance, and handles staking and withdrawing interactions.

Here is the complete implementation of our React component utilizing Ethers.js:

```jsx
import React, { useState, useEffect } from 'react';
import { ethers } from 'ethers';
import StakerABI from './SimpleStaker.json';

const STAKER_ADDRESS = "YOUR_DEPLOYED_CONTRACT_ADDRESS_HERE";

export default function StakingApp() {
  const [provider, setProvider] = useState(null);
  const [signer, setSigner] = useState(null);
  const [contract, setContract] = useState(null);
  const [account, setAccount] = useState("");
  const [stakedBalance, setStakedBalance] = useState("0");
  const [stakeAmount, setStakeAmount] = useState("");

  async function connectWallet() {
    if (window.ethereum) {
      try {
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        const tempProvider = new ethers.providers.Web3Provider(window.ethereum);
        const tempSigner = tempProvider.getSigner();
        const tempContract = new ethers.Contract(STAKER_ADDRESS, StakerABI.abi, tempSigner);

        setProvider(tempProvider);
        setSigner(tempSigner);
        setContract(tempContract);
        setAccount(accounts[0]);
      } catch (err) {
        console.error("Wallet connection failed", err);
      }
    } else {
      alert("Please install MetaMask!");
    }
  }

  async function fetchStakedBalance() {
    if (contract && account) {
      const balance = await contract.stakedBalances(account);
      setStakedBalance(ethers.utils.formatEther(balance));
    }
  }

  async function handleStake(e) {
    e.preventDefault();
    if (!contract || !stakeAmount) return;
    try {
      const tx = await contract.stake(ethers.utils.parseEther(stakeAmount));
      await tx.wait();
      fetchStakedBalance();
      setStakeAmount("");
    } catch (err) {
      console.error("Staking failed", err);
    }
  }

  async function handleWithdraw() {
    if (!contract) return;
    try {
      const tx = await contract.withdraw();
      await tx.wait();
      fetchStakedBalance();
    } catch (err) {
      console.error("Withdraw failed", err);
    }
  }

  useEffect(() => {
    if (account) {
      fetchStakedBalance();
    }
  }, [account, contract]);

  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h1>Simple Staking Portal</h1>
      {!account ? (
        <button onClick={connectWallet}>Connect MetaMask</button>
      ) : (
        <div>
          <p>Connected Account: {account}</p>
          <p>Your Staked Balance: {stakedBalance} STK</p>
          
          <form onSubmit={handleStake}>
            <input 
              type="number" 
              placeholder="Amount to stake" 
              value={stakeAmount}
              onChange={(e) => setStakeAmount(e.target.value)}
            />
            <button type="submit">Stake Tokens</button>
          </form>
          
          <button onClick={handleWithdraw} style={{ marginTop: '10px' }}>
            Claim Rewards & Withdraw All
          </button>
        </div>
      )}
    </div>
  );
}
```

This React app connects directly to the blockchain, monitors network confirmations, and provides real-time updates as transactions get mined.

## Key Takeaways
- **State Separation**: Clearly separate Solidity storage mapping mutations from read-only views to optimize contract execution gas costs.
- **Confirmations Loop**: Always await transaction confirmation block receipts on the frontend (`tx.wait()`) before triggering UI state updates.
- **Provider Pattern**: Utilize the Ethers.js `Web3Provider` wrapper to abstract complex JSON-RPC network requests behind clean JavaScript promises.
- **Mock Token Lifecycle**: When testing locally, always deploy a mock ERC20 token first and approve the staking contract to spend it before testing the stake function.

## Frequently Asked Questions

**Q: Why does my staking contract require an approval transaction before staking?**
A: Because of ERC20 safety guidelines. The user must first call `approve()` on the token contract itself, giving permission to the staking contract to spend their tokens, before the staking contract can execute the `transferFrom()` function.

**Q: How do I handle contract state updates in real-time in my UI?**
A: Listen to contract events. Ethers.js allows you to listen to events directly on your React frontend using `contract.on("Staked", (user, amount) => { ... })` and reactively update your states.

**Q: What is the difference between a Signer and a Provider in Ethers.js?**
A: A Provider is a read-only connection to the blockchain that allows you to query states. A Signer is a full wrapper around your private key that can sign messages and broadcast state-modifying transactions to the network.

---

*If this gave you even one useful insight, subscribe — I drop these every week.*

*— [Shantanu Vishwanadha](https://substack.com/@thecoderpanda)*
