---
title: "Solidity Fundamentals: State Variables, Functions, and Events Explained"
subtitle: "A crash course in writing smart contracts that actually make sense, complete with code you can compile today."
date: "2019-03-28"
author: "Shantanu Vishwanadha"
authorUrl: "https://substack.com/@thecoderpanda"
tags: ["solidity", "smart-contracts", "ethereum", "tutorials", "programming"]
seoTitle: "Solidity Fundamentals: State, Functions & Events Guide"
seoDescription: "Master Solidity smart contract fundamentals in 2019. A developer's guide to state variables, functions, and events with functional code examples."
featuredImage: "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
imageAlt: "A laptop screen showing lines of code in a programming environment with glowing colors."
category: "tutorials"
readingTime: "8 min read"
slug: "solidity-fundamentals-state-variables-functions-events"
---

# Solidity Fundamentals: State Variables, Functions, and Events Explained

> **TL;DR:** Learning Solidity can be a surreal experience. It looks deceptively like JavaScript, but behaves like a hyper-secure financial mainframe that will ruthlessly burn real money if you miss a single semicolon. To build secure, efficient Ethereum smart contracts, you must understand how to manage state, structure functions correctly, and emit events for off-chain logging without wasting precious gas.

If you are a web developer transitioning into Web3, your first glance at Solidity probably felt reassuring. \"Ah, curly braces! It has mappings and arrays! It looks just like JavaScript or TypeScript!\" you said, confidently opening an editor. But then you compile your first contract, look at the gas costs, and realize that you are no longer in the comfortable world of infinite cloud computing. 

Writing smart contracts is not like writing web applications. On the Ethereum Virtual Machine (EVM), every single computation, memory allocation, and database write is executed by thousands of computers worldwide simultaneously. And they charge you for it. In actual, real-world cash. 

To prevent your contracts from becoming incredibly expensive or catastrophically insecure, you have to throw out your traditional programming assumptions. You need to master the three pillars of basic smart contract architecture: state variables, functions, and events. Let’s break them down.

## State Variables: The Blockchain’s Permanent Memory

In a traditional application, your database lives on a separate server, and your code queries it. In Solidity, your smart contract *is* the database. The variables you declare at the contract level are called **State Variables**, and they are permanently written to the blockchain’s storage.

State storage is the most expensive resource on Ethereum. Writing a single 256-bit word to storage costs 20,000 gas, while modifying an existing one costs 5,000 gas. In early 2019, with gas fees fluctuating, a poorly optimized loop writing to a state variable can easily cost more than the value of the transaction itself.

When you declare state variables, you must specify their visibility. Solidity gives you four choices, though only three apply to state variables:
- `public`: Anyone can read this variable. Solidity automatically generates a getter function behind the scenes, so off-chain clients can query it without writing custom code.
- `private`: Only code inside this specific contract can access the variable. (Warning: \"private\" does not mean \"hidden.\" All data on a public blockchain is visible to anyone who inspects the chain history. It only restricts other smart contracts from reading it).
- `internal`: Only this contract and any contracts that inherit from it can access the variable. This is the default visibility if you don't specify one.

Keep your state variables as compact as possible. Group them together, use appropriate types (like `uint256` instead of smaller sizes unless you are packing variables into a single storage slot), and never use them for temporary calculations. If you need to manipulate data inside a loop, do it in a temporary memory variable and write the final result to the state variable at the very end.

## Functions: The Gates of State Mutation

Functions are the executable blocks of code that let users read or modify your contract's state. When designing functions, you have to be explicit about what the function is allowed to do. 

This is done using **mutability specifiers**:

First, we have standard, state-changing functions. These do not have a specifier. If your function modifies a state variable—such as updating a balance or incrementing a counter—it mutates the state. Executing these functions requires a transaction, costs gas, and must be mined.

Second, we have `view` functions. These functions read data from the contract's state but are guaranteed not to modify it. If a user calls a `view` function directly from their wallet (without sending a transaction), it is completely free and executes instantly.

Third, we have `pure` functions. These are even more restrictive: they do not read from state, and they do not write to state. They perform purely algorithmic operations based solely on the input parameters provided to them. Like `view` functions, they cost zero gas when called off-chain.

Understanding when to use `view` and `pure` is essential for gas optimization. If your frontend dashboard needs to read a user's balance, it should call a `view` function. By keeping read-only operations gas-free, you create a much better, cheaper user experience.

## Events: The Developer's Logging System

If you are used to debugging code with `console.log()` or tracking user actions with server logs, you are in for a shock. The EVM does not have a standard terminal output, and storing transaction histories inside state variables to keep track of user actions is prohibitively expensive.

This is where **Events** come in. 

Events are the logging mechanism of the Ethereum blockchain. When a contract emits an event, the parameters are written to the transaction logs—a separate, cheaper storage area that is associated with the block but is not accessible by the smart contracts themselves. 

Because events are stored in logs rather than state storage, they are incredibly cheap. Emitting an event costs only 375 gas plus 8 gas per byte of data. This makes them the perfect tool for tracking changes, alerting off-chain applications, and storing historical data.

When you emit an event, decentralization tools (like Web3.js, Ethers.js, or indexing protocols like The Graph) can listen for those events in real-time. If a user transfers tokens, your smart contract emits a `Transfer` event. Your frontend React app, which is listening for that event, instantly sees it and updates the UI to show the completed transaction. Without events, your frontend would have to constantly poll the blockchain to detect changes, which is slow and highly inefficient.

## Putting it Together: The Simple Ledger Contract

Let’s look at a functional, compiling smart contract written for Solidity `0.5.0` that brings all three of these pillars together:

```solidity
pragma solidity ^0.5.0;

contract SimpleLedger {
    address public owner;
    mapping(address => uint256) private balances;

    event Deposit(address indexed user, uint256 amount);
    event Transfer(address indexed from, address indexed to, uint256 amount);

    constructor() public {
        owner = msg.sender;
    }

    function deposit() public payable {
        require(msg.value > 0, "Zero deposit");
        balances[msg.sender] += msg.value;
        emit Deposit(msg.sender, msg.value);
    }

    function transfer(address to, uint256 amount) public {
        require(to != address(0), "Invalid address");
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        balances[to] += amount;
        emit Transfer(msg.sender, to, amount);
    }

    function getBalance(address user) public view returns (uint256) {
        return balances[user];
    }

    function calculateFee(uint256 value, uint256 rate) public pure returns (uint256) {
        return (value * rate) / 10000;
    }
}
```

Notice how clean the architecture is. The `balances` mapping and the `owner` address are state variables. The `deposit` and `transfer` functions modify state and emit events (`Deposit` and `Transfer`) so our off-chain web application can track user activity. The `getBalance` function is a `view` function that lets anyone query balances for free, while `calculateFee` is a pure mathematical calculation requiring no blockchain interaction at all.

By designing your contracts around these core concepts, you'll write code that is clean, secure, and highly optimized for gas consumption. Stop treating the blockchain like a generic server, and start embracing the unique constraints of the EVM. Happy coding!

## Key Takeaways

- **[State is premium real estate]**: State variables are permanently stored on-chain. Design your data structures to minimize storage operations to avoid massive gas fees.
- **[Define function mutability]**: Use `view` and `pure` modifiers whenever a function does not need to write to the ledger. This saves gas and speeds up read operations.
- **[Log with events]**: Use events for communication, debugging, and off-chain frontend integrations instead of saving transaction histories to state storage.
- **[Keep private access local]**: Use `private` or `internal` visibilities for critical states, but remember that all data is physically readable on a public ledger.

## Frequently Asked Questions

**Q: Can we access events from inside other smart contracts?**
A: No. Smart contracts cannot access event logs, neither their own nor those emitted by other contracts. Event logs are write-only from the EVM's perspective and are designed strictly for off-chain clients and indexers.

**Q: What happens if a transaction reverts after an event has been emitted?**
A: If a transaction reverts (fails) at any point during its execution, all state changes made during that transaction are rolled back, and all emitted events within that transaction are cancelled as if they never happened.

**Q: Is there any limit to how many state variables we can have in a single contract?**
A: While there is no strict limit on the number of state variables, you are limited by the overall block gas limit when deploying a contract. Extremely large contracts with hundreds of state variables will exceed the block deployment limit and fail to deploy.

---

*If this made you think, it'll do even more when shared. Hit that subscribe button — I write about blockchain and software development every week and I promise to keep it real.*

*— [Shantanu Vishwanadha](https://substack.com/@thecoderpanda)*
