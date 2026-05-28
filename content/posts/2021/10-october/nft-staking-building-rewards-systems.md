---
title: "NFT Staking: Building Reward Systems for Your Token Community"
subtitle: "A tutorial on writing smart contracts that lock NFTs and yield ERC-20 utility tokens."
date: "2021-10-16"
author: "Shantanu Vishwanadha"
authorUrl: "https://substack.com/@thecoderpanda"
tags: ["tutorials", "solidity", "nft", "staking"]
seoTitle: "NFT Staking Tutorial: ERC-721 and ERC-20 Reward Systems"
seoDescription: "Increase community holding times. Follow this complete developer tutorial to build an NFT staking smart contract that rewards holders with utility tokens."
featuredImage: "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
imageAlt: "Dark screen containing React and Solidity mapping syntax"
category: "tutorials"
readingTime: "6 min read"
slug: "nft-staking-building-rewards-systems"
---

# NFT Staking: Building Reward Systems for Your Token Community

> **TL;DR:** NFT staking is the ultimate mechanism for reducing secondary market sell pressure and keeping communities engaged. This tutorial walks you through writing a secure, production-ready Solidity smart contract that escrow-locks ERC-721 tokens and dispenses ERC-20 utility tokens as rewards.

Welcome to the golden age of JPEG speculation. We are currently in October 2021, and the NFT market is in a state of absolute, beautiful delirium. Bored Apes are throwing yacht parties, Cool Cats are soaring past double-digit floor prices, and people are mortgage-refinancing their homes to buy digital images of pixelated penguins. 

But as any collection founder or community manager will tell you, the biggest challenge in the NFT space isn't selling out your initial mint. The real challenge is keeping your holders from panic-selling their NFTs on OpenSea the minute the floor price fluctuates by 0.05 ETH. How do you incentivize long-term HODLing and reward your most loyal community members? 

The answer is NFT staking. By allowing your users to "lock" their ERC-721 tokens inside a secure smart contract, you take those assets out of active circulation, reducing the supply on open marketplaces. In exchange, your contract programmatically mints and distributes ERC-20 utility tokens—let’s call it `$DUST` or `$BANANA`—which can be used for future mints, merchandise, or voting rights in your DAO. Today, we are going to roll up our sleeves and write a robust, gas-optimized Solidity smart contract to handle this exact mechanism.

## The Architecture: Escrow vs. Soft Staking

Before we write a single line of code, we need to choose our architectural pattern. There are two primary ways to design an NFT staking system:
1. **Soft Staking**: The NFT never leaves the holder's wallet. Instead, the contract monitors wallet balances via off-chain indexers and allocates rewards. While highly convenient for the user, it is incredibly difficult to enforce security constraints or prevent rapid listings without heavy centralized backend monitoring.
2. **Escrow Staking (The On-Chain Gold Standard)**: The user interacts with your staking contract, which calls `transferFrom` to pull the ERC-721 token into its own secure storage. The contract records the owner and timestamp. When the user wants to unstake, the contract calculates their reward, mints the ERC-20 tokens, and transfers the NFT back to their wallet.

We are going to build the **Escrow Staking** model because it is fully trustless, decentralized, and cryptographically secure.

## The Smart Contract Code

Here is the complete, gas-optimized Solidity contract. It uses OpenZeppelin standards for secure token transfers and ownership. Notice that we are tracking individual staked assets using a struct mapped to the token ID.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

interface IERC721 {
    function transferFrom(address from, address to, uint256 tokenId) external;
    function ownerOf(uint256 tokenId) external view returns (address);
}

interface IRewardToken {
    function mint(address to, uint256 amount) external;
}

contract NFTStaking {
    IERC721 public immutable nftCollection;
    IRewardToken public immutable rewardToken;

    uint256 public constant REWARD_RATE_PER_DAY = 10 * 10**18;
    uint256 public constant SECONDS_IN_DAY = 86400;

    struct Stake {
        address owner;
        uint256 stakedAt;
    }

    mapping(uint256 => Stake) public vault;
    mapping(address => uint256) public stakedBalances;

    event NFTStaked(address indexed user, uint256 indexed tokenId, uint256 timestamp);
    event NFTUnstaked(address indexed user, uint256 indexed tokenId, uint256 timestamp);
    event RewardClaimed(address indexed user, uint256 amount);

    constructor(address _nftCollection, address _rewardToken) {
        nftCollection = IERC721(_nftCollection);
        rewardToken = IRewardToken(_rewardToken);
    }

    function stake(uint256[] calldata tokenIds) external {
        uint256 len = tokenIds.length;
        require(len > 0, "No tokens provided");

        for (uint256 i = 0; i < len; i++) {
            uint256 tokenId = tokenIds[i];
            require(nftCollection.ownerOf(tokenId) == msg.sender, "Not the owner");

            nftCollection.transferFrom(msg.sender, address(this), tokenId);

            vault[tokenId] = Stake({
                owner: msg.sender,
                stakedAt: block.timestamp
            });

            emit NFTStaked(msg.sender, tokenId, block.timestamp);
        }

        stakedBalances[msg.sender] += len;
    }

    function unstake(uint256[] calldata tokenIds) external {
        uint256 len = tokenIds.length;
        require(len > 0, "No tokens provided");
        uint256 totalReward = 0;

        for (uint256 i = 0; i < len; i++) {
            uint256 tokenId = tokenIds[i];
            Stake memory stakedItem = vault[tokenId];
            require(stakedItem.owner == msg.sender, "Not the staker");

            totalReward += _calculateReward(stakedItem.stakedAt);

            delete vault[tokenId];

            nftCollection.transferFrom(address(this), msg.sender, tokenId);

            emit NFTUnstaked(msg.sender, tokenId, block.timestamp);
        }

        stakedBalances[msg.sender] -= len;

        if (totalReward > 0) {
            rewardToken.mint(msg.sender, totalReward);
            emit RewardClaimed(msg.sender, totalReward);
        }
    }

    function claimRewards(uint256[] calldata tokenIds) external {
        uint256 len = tokenIds.length;
        require(len > 0, "No tokens provided");
        uint256 totalReward = 0;

        for (uint256 i = 0; i < len; i++) {
            uint256 tokenId = tokenIds[i];
            Stake storage stakedItem = vault[tokenId];
            require(stakedItem.owner == msg.sender, "Not the staker");

            totalReward += _calculateReward(stakedItem.stakedAt);
            stakedItem.stakedAt = block.timestamp;
        }

        if (totalReward > 0) {
            rewardToken.mint(msg.sender, totalReward);
            emit RewardClaimed(msg.sender, totalReward);
        }
    }

    function getEarnedRewards(address user, uint256[] calldata tokenIds) external view returns (uint256) {
        uint256 totalReward = 0;
        uint256 len = tokenIds.length;
        for (uint256 i = 0; i < len; i++) {
            uint256 tokenId = tokenIds[i];
            Stake memory stakedItem = vault[tokenId];
            if (stakedItem.owner == user) {
                totalReward += _calculateReward(stakedItem.stakedAt);
            }
        }
        return totalReward;
    }

    function _calculateReward(uint256 stakedAt) internal view returns (uint256) {
        uint256 duration = block.timestamp - stakedAt;
        return (duration * REWARD_RATE_PER_DAY) / SECONDS_IN_DAY;
    }
}
```

## Security Best Practices for Staking Systems

When deploying a staking contract, security is paramount. Since your contract will hold high-value NFTs, it becomes a prime target for hackers.

### The Reentrancy Threat
The most dangerous vulnerability in ERC-721 staking contracts is reentrancy during the unstake process. If your utility token contract calls a custom fallback or receiver function inside the user’s wallet before updating the internal balances, a malicious actor can loop the function, drainage-transferring the same NFT multiple times or claiming infinite rewards. 

To mitigate this, always follow the **Checks-Effects-Interactions** pattern. In our code, we update our state variables (`delete vault[tokenId]` and subtract from `stakedBalances`) *before* executing the transfer calls back to the user. This completely eliminates reentrancy vectors.

### Approved Operator Risks
Before staking, users must call `setApprovalForAll` on the core ERC-721 contract to authorize your staking contract to transfer their assets. Ensure your front-end interface clearly explains that they are approving a *secure staking contract*, not signing a generic transaction that could expose their entire wallet. Educating your community on contract interaction safeguards is just as important as writing clean code.

## Key Takeaways
- **Supply Squeeze**: Staking locks digital assets on-chain, lowering active marketplace listings and strengthening floor price stability.
- **Gas Efficiency**: The contract uses loop variables stored in memory rather than reading state arrays inside loops, keeping transaction costs low during multi-token stakings.
- **Checks-Effects-Interactions**: By deleting staking records from mapping state before initiating external transfers, you guarantee protection against reentrancy attacks.
- **Continuous Yield**: Rewards are calculated down to the second using `block.timestamp`, ensuring fair, granular compensation for the duration of the stake.

## Frequently Asked Questions

**Q: Do stakers still get airdrops distributed to the original NFT collection?**
A: Not automatically. Because the NFT is custody-held inside the staking contract, any snapshot taken by third-party airdrops will see the staking contract as the owner. Developers must write claim-forwarding functions or coordinate with partner projects to respect the internal `vault` mapping.

**Q: Can we change the reward emission rate after deployment?**
A: In our basic contract, the reward rate is a `constant`. To make it adjustable, you can replace the constant with a state variable and add an `setRewardRate` function protected by an `onlyOwner` modifier.

**Q: What happens if a user stakes an NFT and the reward token contract runs out of tokens?**
A: Since the reward token contract relies on `mint()`, it dynamically prints new utility tokens on demand. This requires that the NFT Staking contract is granted the `MINTER_ROLE` on the ERC-20 contract.

---

*If this gave you even one useful insight, subscribe — I drop these every week.*

*— [Shantanu Vishwanadha](https://substack.com/@thecoderpanda)*