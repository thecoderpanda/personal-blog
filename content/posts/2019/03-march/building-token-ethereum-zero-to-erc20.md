---
title: "Building a Token on Ethereum: From Zero to ERC-20 in One Afternoon"
subtitle: "Forget the academic theories and market hype. Here is a practical, step-by-step developer's guide to deploying your first Solidity smart contract."
date: "2019-03-08"
author: "Shantanu Vishwanadha"
authorUrl: "https://substack.com/@thecoderpanda"
tags: ["ethereum", "solidity", "tutorials", "smart-contracts", "erc20"]
seoTitle: "How to Build an ERC-20 Token on Ethereum: Step-by-Step"
seoDescription: "A complete, hands-on, witty tutorial for developers looking to build and deploy their first ERC-20 smart contract using Solidity, Remix, and MetaMask."
featuredImage: "https://images.unsplash.com/photo-1555066931-4365d14bab8c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
imageAlt: "A computer monitor displaying colorful code lines in a dark room"
category: "tutorials"
readingTime: "8 min read"
slug: "building-token-ethereum-zero-to-erc20"
---

In the physical world, launching your own currency is incredibly difficult. You need an army, a treasury department, a central bank, a couple of printing presses, and probably a few international trade agreements to make sure people don’t throw you in prison for counterfeiting.

In the Web3 world, you just need a laptop, some stale coffee, and about thirty lines of Solidity.

Welcome to the magic of the Ethereum Virtual Machine (EVM). Today, we’re going to strip away the complex academic jargon, the economic theories, and the sheer noise of the crypto speculation machine. We are going to do some honest-to-god engineering. By the end of this afternoon, you will have designed, written, compiled, and deployed your very own ERC-20 token onto an Ethereum test network.

Will this token make you a billionaire? Almost certainly not. But will it make you understand the underlying technology far better than 99% of the self-proclaimed "crypto experts" on Twitter? Absolutely.

Let’s get coding.

---

## What Actually is an ERC-20 Token?

Before we open our IDE, let’s demystify what we’re actually building. 

When people think of a "token," they often imagine some sort of digital coin floating around in a decentralized cloud. They think MetaMask is a physical wallet holding these little digital tokens.

It isn't.

At its core, an ERC-20 token is **nothing more than a smart contract containing an Excel-like ledger**. This ledger maps wallet addresses to numbers. 

```
Address 0x123... -> Balance: 1,000
Address 0xabc... -> Balance: 250
```

When you "transfer" a token to someone, you aren't sending them a file. You are sending a transaction to the smart contract that says: *"Hey, deduct 50 from my balance, and add 50 to this other address."* The smart contract checks if you have enough balance, updates its internal state, and emits an event. That’s it.

The **ERC-20** designation simply refers to a standard—a checklist of functions and events that your smart contract must implement. Because everyone agrees to use this exact checklist, external tools like MetaMask, Etherscan, and Uniswap know exactly how to interact with your token without having to read your custom code.

Here is the checklist of core functions we need to implement:
*   `totalSupply()`: Returns the total number of tokens in existence.
*   `balanceOf(address owner)`: Returns the balance of a specific wallet.
*   `transfer(address to, uint256 value)`: Moves tokens from the sender to another wallet.
*   `approve(address spender, uint256 value)`: Grants permission to another wallet to spend a certain amount of your tokens.
*   `transferFrom(address from, address to, uint256 value)`: Allows an approved spender to move tokens on your behalf.
*   `allowance(address owner, address spender)`: Checks how much a spender is still allowed to withdraw from an owner's wallet.

---

## The Sandbox: Our Developer Environment

To build this, we don’t need to install a heavy command-line toolchain like Truffle or Hardhat just yet. We’re going to use **Remix IDE**, Ethereum’s browser-based development environment. It’s essentially a web app that comes pre-packaged with a Solidity compiler, a code editor, and a virtual blockchain environment.

Here is your pre-flight checklist:
1.  Open your browser and navigate to **[remix.ethereum.org](https://remix.ethereum.org/)**.
2.  Install the **MetaMask** browser extension if you haven't already.
3.  Set your MetaMask network to **Rinkeby Test Network** (make sure you don't use real Ethereum—we don't want to spend actual money on this!).
4.  Get some test Ether from a Rinkeby faucet. Just search "Rinkeby faucet" on Google, paste your address, and get some free, fake playground gas.

---

## The Code: Writing the Smart Contract

In Remix, create a new file named `MyToken.sol`. We will write our contract using Solidity `v0.5.8`, which is the rock-solid stable release of early 2019.

Here is the complete, self-contained contract. Copy this into your editor, and then let’s walk through what each line does:

```solidity
pragma solidity ^0.5.8;

contract MyToken {
    string public name = "PandaCoin";
    string public symbol = "PANDA";
    uint8 public decimals = 18;
    uint256 public totalSupply;

    // The core ledger mapping addresses to balances
    mapping(address => uint256) public balanceOf;
    
    // Nested mapping to track allowances
    mapping(address => mapping(address => uint256)) public allowance;

    // Standard ERC-20 Events
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    // Constructor runs once when the contract is deployed
    constructor(uint256 _initialSupply) public {
        // 18 decimals is standard (matches ETH). 
        // We multiply our desired supply by 10^18 to account for decimal precision.
        totalSupply = _initialSupply * 10 ** uint256(decimals);
        
        // Give all initial tokens to the creator of the contract
        balanceOf[msg.sender] = totalSupply;
    }

    // Move tokens from sender's wallet to a target address
    function transfer(address _to, uint256 _value) public returns (bool success) {
        require(balanceOf[msg.sender] >= _value, "Insufficient balance.");
        
        balanceOf[msg.sender] -= _value;
        balanceOf[_to] += _value;
        
        emit Transfer(msg.sender, _to, _value);
        return true;
    }

    // Approve another address to spend your tokens
    function approve(address _spender, uint256 _value) public returns (bool success) {
        allowance[msg.sender][_spender] = _value;
        
        emit Approval(msg.sender, _spender, _value);
        return true;
    }

    // Approved spender transfers tokens on behalf of an owner
    function transferFrom(address _from, address _to, uint256 _value) public returns (bool success) {
        require(balanceOf[_from] >= _value, "Insufficient balance.");
        require(allowance[_from][msg.sender] >= _value, "Allowance exceeded.");

        balanceOf[_from] -= _value;
        balanceOf[_to] += _value;
        allowance[_from][msg.sender] -= _value;

        emit Transfer(_from, _to, _value);
        return true;
    }
}
```

### Deciphering the Logic

*   **`pragma solidity ^0.5.8;`**: This tells the compiler which version of Solidity to use. 
*   **`mapping(address => uint256)`**: This is Solidity's version of a hash table or dictionary. Key is the wallet address, value is their token balance.
*   **`msg.sender`**: This is a global variable representing the address that is calling the current function. When you deploy the contract, `msg.sender` is you.
*   **`require()`**: This is Solidity’s guardrail. If the condition inside `require` evaluates to `false`, the transaction immediately stops, reverts all state changes, and refunds the remaining gas to the user. It's like an `if-throw` block but on a blockchain ledger.
*   **`emit`**: This triggers an event. Events are written to the transaction logs on the blockchain, allowing frontends (like MetaMask) to listen to changes and update their UI in real-time.

---

## Launching Into Orbit: Deployment

Now that our code is ready, let's ship it.

1.  **Compile**: Go to the "Solidity Compiler" tab in Remix (the icon looks like a small contract logo). Set the compiler version to `0.5.8` and click **Compile MyToken.sol**.
2.  **Configure Environment**: Go to the "Deploy & Run Transactions" tab (the icon below the compiler). Under "Environment," select **Injected Web3**. This tells Remix to use MetaMask as your gateway to the Rinkeby network. You should see your MetaMask wallet address show up under "Account" with your test Ether balance.
3.  **Input Parameters**: Next to the orange "Deploy" button, you will see an input box for `_initialSupply`. Enter your desired token supply—let’s say `1000000` (1 million coins).
4.  **Ship It**: Click **Deploy**. MetaMask will slide out, asking you to confirm the transaction and pay a tiny amount of test gas. Click **Confirm**.

Now, watch the terminal log at the bottom of Remix. Within 15 to 30 seconds, you’ll see a green checkmark indicating the transaction has been mined. 

Congratulations! Your token is officially live on the Ethereum Rinkeby network.

---

## Interacting with Your Creation

In the Remix sidebar, look under **Deployed Contracts**. You’ll see your contract address and a list of blue and orange buttons representing your functions.

*   Click the **symbol** button: It will return `PANDA`.
*   Click the **totalSupply** button: It will return `1000000000000000000000000` (that's 1 million with 18 decimal zeros appended).
*   Copy your own MetaMask address, paste it into the **balanceOf** box, and click it: It should return your full total supply.

If you want to make it feel real, open MetaMask, click "Add Token," select "Custom Token," and paste your contract address (which you can copy from Remix). MetaMask will automatically read the `PANDA` symbol and `18` decimals from the ledger. 

Suddenly, your browser extension is proudly displaying that you are a millionaire in PandaCoins. 

Go ahead and use the `transfer` button in Remix to send some tokens to a friend's address. Have them add the contract to their MetaMask, and watch their screen update. You’ve just bypassed the entire global banking system to execute a transaction on a shared computer.

Welcome to smart contract development. You are now officially a builder in the Web3 space. Go build something useful.
