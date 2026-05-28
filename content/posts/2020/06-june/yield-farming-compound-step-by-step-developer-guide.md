---
title: "Yield Farming on Compound: A Step-by-Step Guide for Developers"
subtitle: "Write smart contracts to automate the supply, borrow, and claim cycle to maximize COMP yield programmatically."
date: "2020-06-18"
author: "Shantanu Vishwanadha"
authorUrl: "https://substack.com/@thecoderpanda"
tags: ["solidity", "defi", "compound-finance", "tutorials"]
seoTitle: "Yield Farming Compound: Developer Smart Contract Guide"
seoDescription: "A technical guide on yield farming on Compound Finance. Code Solidity contracts to supply assets, borrow recursively, and claim COMP tokens."
featuredImage: "https://images.unsplash.com/photo-1555066931-4365d14bab8c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
imageAlt: "A clean developer setup with code on screen and professional accessories, representing Solidity smart contract coding"
category: "tutorials"
readingTime: "6 min read"
slug: "yield-farming-compound-step-by-step-developer-guide"
---

Farming COMP tokens through the Compound web interface is fine if you're a retail user playing with a few hundred dollars. But if you are a developer looking to deploy capital efficiently, coordinate gas expenditures, and build optimized yield strategies, you don't use a browser extension. You write smart contracts.

The launch of the COMP token has created a unique programmatic opportunity: recursive leverage farming. By supplying an asset, borrowing against it, and re-supplying the borrowed asset, you can multiply your share of the daily COMP distribution. 

In this tutorial, we will write a Solidity smart contract to automate the supply, borrow, and claim cycle on Compound. Grab some coffee, fire up your favorite editor, and let's dive into some Solidity.

## The Compound Architecture

To interact with Compound programmatically, you need to understand three core components:
1. **cTokens**: These are self-contained yield-bearing ERC-20 tokens. When you supply DAI to Compound, you receive cDAI in return. The exchange rate of cDAI to DAI increases over time as interest accumulates.
2. **The Comptroller**: This is the brain of Compound. It determines how much collateral factor an asset has, checks account liquidity, and handles the distribution of COMP rewards.
3. **The Price Oracle**: Keeps track of asset prices so the Comptroller knows if your account is healthy enough to borrow or if you are ripe for liquidation.

To execute our strategy, we need our contract to approve the underlying token, mint cTokens, register the cToken market with the Comptroller, borrow the token, and recursively repeat.

## Setting Up the Interfaces

First, we need to define the ERC-20, cToken, and Comptroller interfaces in Solidity. We will use Solidity version `0.8.0` for safety and modern features.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.0;

interface IERC20 {
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address recipient, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
}

interface ICERC20 {
    function mint(uint256 mintAmount) external returns (uint256);
    function redeem(uint256 redeemTokens) external returns (uint256);
    function redeemUnderlying(uint256 redeemAmount) external returns (uint256);
    function borrow(uint256 borrowAmount) external returns (uint256);
    function repayBorrow(uint256 repayAmount) external returns (uint256);
    function borrowBalanceCurrent(address account) external returns (uint256);
    function balanceOf(address owner) external view returns (uint256);
    function underlying() external view returns (address);
}

interface IComptroller {
    function enterMarkets(address[] calldata cTokens) external returns (uint256[] memory);
    function exitMarket(address cToken) external returns (uint256);
    function claimComp(address holder) external;
    function getAccountLiquidity(address account) external view returns (uint256, uint256, uint256);
}
```

## Designing the Farming Contract

Our contract, `CompoundYieldFarmer`, will be owned by us and will allow us to supply an underlying asset (like DAI), enter the market, borrow, and leverage up.

Here is the complete implementation of our yield farming contract. Notice how clean it is, with no unnecessary bloat:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.0;

contract CompoundYieldFarmer {
    address public owner;
    IComptroller public comptroller;
    address public compToken;

    modifier onlyOwner() {
        require(msg.sender == owner, "caller is not the owner");
        _;
    }

    constructor(address _comptroller, address _compToken) {
        owner = msg.sender;
        comptroller = IComptroller(_comptroller);
        compToken = _compToken;
    }

    function executeLeverage(
        address _cTokenAddress,
        uint256 _initialAmount,
        uint256 _borrowAmount
    ) external onlyOwner {
        ICERC20 cToken = ICERC20(_cTokenAddress);
        address underlyingAddress = cToken.underlying();
        IERC20 underlying = IERC20(underlyingAddress);

        underlying.transferFrom(msg.sender, address(this), _initialAmount);
        underlying.approve(_cTokenAddress, _initialAmount);

        uint256 mintResult = cToken.mint(_initialAmount);
        require(mintResult == 0, "mint failed");

        address[] memory markets = new address[](1);
        markets[0] = _cTokenAddress;
        uint256[] memory errors = comptroller.enterMarkets(markets);
        require(errors[0] == 0, "enter market failed");

        uint256 borrowResult = cToken.borrow(_borrowAmount);
        require(borrowResult == 0, "borrow failed");

        underlying.approve(_cTokenAddress, _borrowAmount);
        uint256 reDepositResult = cToken.mint(_borrowAmount);
        require(reDepositResult == 0, "re-deposit failed");
    }

    function claimRewards() external onlyOwner {
        comptroller.claimComp(address(this));
        IERC20 comp = IERC20(compToken);
        uint256 balance = comp.balanceOf(address(this));
        if (balance > 0) {
            comp.transfer(owner, balance);
        }
    }

    function unwindLeverage(
        address _cTokenAddress,
        uint256 _repayAmount,
        uint256 _redeemTokens
    ) external onlyOwner {
        ICERC20 cToken = ICERC20(_cTokenAddress);
        address underlyingAddress = cToken.underlying();
        IERC20 underlying = IERC20(underlyingAddress);

        underlying.transferFrom(msg.sender, address(this), _repayAmount);
        underlying.approve(_cTokenAddress, _repayAmount);

        uint256 repayResult = cToken.repayBorrow(_repayAmount);
        require(repayResult == 0, "repay failed");

        uint256 redeemResult = cToken.redeem(_redeemTokens);
        require(redeemResult == 0, "redeem failed");

        uint256 currentBalance = underlying.balanceOf(address(this));
        underlying.transfer(owner, currentBalance);
    }

    function withdrawToken(address _token) external onlyOwner {
        IERC20 token = IERC20(_token);
        uint256 balance = token.balanceOf(address(this));
        if (balance > 0) {
            token.transfer(owner, balance);
        }
    }
}
```

## Anatomy of the Farming Steps

Let’s walk through the core function `executeLeverage` to understand how the plumbing works.

### 1. Funding and Approval
The contract pulls the initial supply asset (for example, DAI) from your wallet via `transferFrom`. For this to work, you must call `approve` on the DAI ERC-20 contract from your external wallet, granting authorization to the `CompoundYieldFarmer` contract.

Once the contract holds the DAI, it approves the corresponding `cToken` contract (`cDAI`) to spend the DAI.

### 2. Minting cTokens
By calling `cToken.mint(_initialAmount)`, our contract locks up the underlying DAI and receives cDAI in return. The returned value is checked against `0`, which in Compound land represents success. Any other number is an error code.

### 3. Entering the Market
Crucially, supplying assets doesn't automatically mean you can borrow against them. You must explicitly tell the Comptroller that you intend to use your newly minted cDAI as collateral. We achieve this by invoking:

```solidity
comptroller.enterMarkets(markets);
```

Without entering the market, any subsequent `borrow` call will fail with a boring, unhelpful error code.

### 4. Borrowing and Re-depositing
Now that we have collateral registered, we execute `cToken.borrow(_borrowAmount)`. The amount of assets you can borrow depends on the cToken's **Collateral Factor** (usually between 60% to 75% for stablecoins).

Once the borrowed DAI hits our contract's balance, we approve the cToken contract again and call `mint` with the borrowed funds. 

Now, our contract has executed a single-loop yield farm. We have supplied, borrowed, and re-supplied. We are earning COMP rewards on both the supply side and the borrow side.

## Claiming Rewards and Unwinding

To claim the farmed COMP, the contract calls `comptroller.claimComp(address(this))`. This instructs the Comptroller to calculate all outstanding COMP rewards accumulated by the contract, mint them, and transfer them directly to the contract. The contract then immediately forwards those COMP tokens to your personal wallet.

Unwinding is the reverse process. You must supply enough underlying asset to pay off the outstanding debt via `repayBorrow`, and then you are free to redeem your cTokens back into underlying assets.

## The Golden Rules of Programmatic Farming

While writing the contract is straightforward, managing it in production during DeFi Summer is a different animal. Keep these three rules in mind:

1. **Collateral Factor and Liquidation**: Never borrow up to your theoretical maximum. If the collateral factor of your asset is lowered by governance, or if the asset you borrowed undergoes price volatility, you will be instantly liquidated, losing up to 8% of your collateral to liquidation penalties. Keep a healthy cushion.
2. **Gas Optimization**: When gas sits at 300 gwei, executing multiple transactions to loop assets is incredibly expensive. Programmatic flash loans (using dYdX or Aave) are often used to execute multi-loop leverage in a single transaction, saving massive amounts of gas.
3. **Emergency Safeguards**: Always build explicit withdrawal and recovery functions (like `withdrawToken`) to retrieve stuck ERC-20 tokens or handle edge-case failures.

Write some tests on a hardhat or dapptools local fork, practice on Goerli, and always check the return values of Compound's functions. Happy farming, and may the yields be ever in your favor.
