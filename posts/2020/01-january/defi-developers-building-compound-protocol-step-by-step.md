---
title: "DeFi for Developers: Building on Compound Protocol Step by Step"
subtitle: "Learn how to programmatically supply assets and borrow tokens using the Compound cToken contracts."
date: "2020-01-12"
author: "Shantanu Vishwanadha"
authorUrl: "https://substack.com/@thecoderpanda"
tags: ["ethereum", "defi", "solidity", "compound-finance"]
seoTitle: "DeFi Developer Tutorial: Building on Compound Protocol"
seoDescription: "A comprehensive developer guide to integrating Compound Protocol. Learn to interact with cTokens, supply liquidity, and borrow with Solidity."
featuredImage: "https://images.unsplash.com/photo-1498050108023-c5249f4df085?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
imageAlt: "Computer screen showing software code with workspace environment setup"
category: "tutorials"
readingTime: "6 min read"
slug: "defi-developers-building-compound-protocol-step-by-step"
---

Welcome back, fellow code slingers. We’ve spent enough time philosophizing about the decentralized finance revolution. Today, we’re opening up our IDEs, firing up our local test environments, and writing some actual, battle-grade smart contracts. 

If you’re a web3 developer, understanding how to interact with the **Compound Protocol** is practically a requirement. It is the gold standard of liquidity pools. Its smart contracts are elegant, heavily audited, and act as the bedrock for dozens of yield-aggregating platforms.

Today, we are going to build a custom Solidity smart contract that programmatically supplies DAI to the Compound Protocol, mints cDAI to earn continuous interest, and then redeems those cDAI tokens back into standard DAI. 

Grab your Solidity hats (we’re using version `0.5.16` because it's early 2020 and we aren't completely ready to trust the compiler changes in `0.6.x` just yet). Let's dive in.

---

## The cToken Mental Model

Before we write code, we need to understand what we are interacting with. 

When you supply an asset like DAI to Compound, you are lending it to a pool. In return, the Compound smart contract mints **cTokens** (in this case, cDAI) and transfers them to you. 

Your cDAI represents your share of the lending pool. But here is the magic trick: **the exchange rate between DAI and cDAI is constantly increasing.** 

As borrowers pay interest on their loans, that interest is distributed to all lenders. Instead of sending DAI payments directly to your wallet, the protocol increases the value of your cDAI. 
When you redeem your cDAI back for DAI, you will get more DAI than you originally put in. 

$$ExchangeRate = \frac{UnderlyingBalance + TotalBorrow - Reserves}{cTokenSupply}$$

To programmatically supply liquidity, we need our contract to talk directly to the `cDAI` contract address. Let's look at the functions we need to call.

---

## Step 1: Defining the Interfaces

Because our smart contract is going to call external contracts, we need to declare the interfaces of the tokens we are interacting with. We need the standard `ERC20` interface (for DAI) and the Compound-specific `CErc20` interface (for cDAI).

Create a file named `CompoundSupplier.sol` and add the following interface declarations:

```solidity
pragma solidity ^0.5.16;

// Standard ERC20 interface for our underlying asset (DAI)
interface IERC20 {
    function transfer(address recipient, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

// Compound cERC20 interface for cDAI
interface CErc20 {
    function mint(uint256 mintAmount) external returns (uint256);
    function redeem(uint256 redeemTokens) external returns (uint256);
    function redeemUnderlying(uint256 redeemAmount) external returns (uint256);
    function balanceOf(address owner) external view returns (uint256);
    function balanceOfUnderlying(address owner) external returns (uint256);
    function exchangeRateStored() external view returns (uint256);
}
```

### A Critical Warning about Compound's API Design
If you are used to modern Ethereum development, you probably expect smart contracts to `revert()` when something goes wrong. 

**Compound does not do this.** 

Instead, most functions on Compound contracts return an `uint256` representing an error code. A return value of `0` means success. Any non-zero value means failure (for example, `3` represents `NO_ERROR` rules violation, or `9` represents `TOKEN_INSUFFICIENT_CASH`). 

As developers, we **must** explicitly check these return values. If you ignore them, your transactions might silently fail while your contract keeps executing, which is a fantastic way to lose sleep and capital.

---

## Step 2: The Core Contract Setup

Now let's build the skeleton of our contract. We will store the addresses of the DAI token and the cDAI contract. For this tutorial, we will use the Mainnet addresses (DAI: `0x6B175474E89094C44Da98b954EedeAC495271d0F`, cDAI: `0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643`).

```solidity
contract CompoundSupplier {
    
    IERC20 public dai;
    CErc20 public cDai;
    
    constructor(address _dai, address _cDai) public {
        dai = IERC20(_dai);
        cDai = CErc20(_cDai);
    }
}
```

---

## Step 3: Programmatically Supplying DAI

Now we write the `supplyDAI` function. This function will transfer DAI from the user into our contract, approve the Compound cDAI contract to spend that DAI, and then call the `mint` function to receive cDAI.

```solidity
    /**
     * @notice Supplies DAI to Compound to earn interest
     * @param _amount The amount of DAI to supply
     */
    function supplyDAI(uint256 _amount) external returns (bool) {
        // 1. Transfer DAI from the sender to this contract
        require(
            dai.transferFrom(msg.sender, address(this), _amount),
            "Transfer of DAI from sender failed"
        );
        
        // 2. Approve cDAI contract to spend our DAI
        require(
            dai.approve(address(cDai), _amount),
            "Approve of DAI to Compound failed"
        );
        
        // 3. Call cDAI's mint function to supply our DAI
        uint256 result = cDai.mint(_amount);
        
        // 4. Validate that the mint was successful (result 0 = success)
        require(result == 0, "Compound mint failed");
        
        return true;
    }
```

---

## Step 4: Programmatically Redeeming Assets

To withdraw our funds, we have two options:
1.  **`redeem(uint256 _cTokenAmount)`**: Redeem a specific number of cTokens back into DAI.
2.  **`redeemUnderlying(uint256 _underlyingAmount)`**: Redeem enough cTokens to get a specific amount of underlying DAI back.

Let's implement both so you can choose which one fits your application's logic.

```solidity
    /**
     * @notice Redeems a specific amount of cDAI tokens for underlying DAI
     * @param _cTokenAmount The amount of cDAI to redeem
     */
    function redeemBycTokens(uint256 _cTokenAmount) external returns (bool) {
        // 1. Call cDAI's redeem function
        uint256 result = cDai.redeem(_cTokenAmount);
        
        // 2. Validate return code (0 = success)
        require(result == 0, "Compound redeem failed");
        
        // 3. Send the recovered DAI back to the caller
        uint256 daiBalance = dai.balanceOf(address(this));
        require(dai.transfer(msg.sender, daiBalance), "DAI transfer to caller failed");
        
        return true;
    }

    /**
     * @notice Redeems a specific amount of underlying DAI from Compound
     * @param _daiAmount The exact amount of DAI to withdraw
     */
    function redeemByUnderlyingAmount(uint256 _daiAmount) external returns (bool) {
        // 1. Call cDAI's redeemUnderlying function
        uint256 result = cDai.redeemUnderlying(_daiAmount);
        
        // 2. Validate return code (0 = success)
        require(result == 0, "Compound redeem underlying failed");
        
        // 3. Send the requested DAI back to the caller
        require(dai.transfer(msg.sender, _daiAmount), "DAI transfer to caller failed");
        
        return true;
    }
```

---

## Step 5: Helper Functions (Reading Balances)

To make our contract useful, we should write view functions to query our balance. Note that `balanceOf` on the cDAI contract returns your cToken balance, whereas `balanceOfUnderlying` computes your current DAI balance (including your accumulated interest). 

*Note: `balanceOfUnderlying` is NOT a view function in the Compound contract because it internally updates interest index metrics on-chain. Therefore, we call it on-chain dynamically.*

```solidity
    /**
     * @notice Returns the contract's current cDAI token balance
     */
    function getcDaiBalance() external view returns (uint256) {
        return cDai.balanceOf(address(this));
    }

    /**
     * @notice Calculates the total amount of DAI (including interest) owned by this contract
     */
    function getDAIBalanceWithInterest() external returns (uint256) {
        // This updates the exchange rate and returns the underlying balance
        return cDai.balanceOfUnderlying(address(this));
    }
    
    /**
     * @notice Returns the exchange rate stored of DAI to cDAI
     */
    function getStoredExchangeRate() external view returns (uint256) {
        return cDai.exchangeRateStored();
    }
```

---

## Putting It All Together: local Testing

To test this on your local machine:
1.  Set up a local mainnet fork using Truffle and Ganache:
    `ganache-cli --fork https://mainnet.infura.io/v3/YOUR_INFURA_KEY`
2.  Deploy your `CompoundSupplier` contract passing the Mainnet DAI and cDAI addresses to the constructor.
3.  Impersonate a large DAI holder (a "whale") to send DAI to your test account.
4.  Call `approve` on the DAI contract for your deployed `CompoundSupplier` address.
5.  Call `supplyDAI` with 1,000 DAI.
6.  Advance your local blockchain mining blocks (`evm_mine`) to simulate time passing.
7.  Call `getDAIBalanceWithInterest()` and marvel at the fact that your 1,000 DAI balance has increased!

You are now officially a DeFi engineer. You have bypassed the traditional banking sector, automated interest-bearing liquidity deposits via self-executing code, and set up your own sovereign finance pipeline. 

Next time, we will explore how to use these cTokens as collateral to programmatically borrow other assets (like ETH or USDC) from the Compound pools. 

Until then, keep your compilers optimized and your private keys offline.

*Happy coding!*