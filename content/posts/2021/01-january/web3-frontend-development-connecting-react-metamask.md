---
title: "Web3 Frontend Development: Connecting React to MetaMask"
subtitle: "A step-by-step developer tutorial on building your first dApp login flow."
date: "2021-01-16"
author: "Shantanu Vishwanadha"
authorUrl: "https://substack.com/@thecoderpanda"
tags: ["tutorials", "react", "metamask", "frontend"]
seoTitle: "Connect React to MetaMask: Web3 Developer Guide"
seoDescription: "Learn how to build a dApp login flow by connecting React to MetaMask. A complete developer tutorial with real-world code examples."
featuredImage: "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
imageAlt: "A dark screen displaying HTML and JavaScript source code"
category: "tutorials"
readingTime: "6 min read"
slug: "web3-frontend-development-connecting-react-metamask"
---

# Web3 Frontend Development: Connecting React to MetaMask

> **TL;DR:** Forget usernames, passwords, and database-managed authorization. In the Web3 world, your cryptographic wallet is your entire identity. Learn how to build a robust, production-ready login flow in React by connecting directly to MetaMask using standard browser APIs.

So, you’ve spent weeks learning Solidity, deployment scripts, and compiling smart contracts. You’re ready to conquer the decentralized world. But then you realize a minor detail: how on earth does a normal human actually interact with your contract? That's right—you need a frontend. And in Web3, the gateway to your application is not a signup form with database fields for password hashes; it's a "Connect Wallet" button.

Web3 frontend development can feel like learning a foreign language at first, even if you are a seasoned React veteran. Instead of making API requests to a backend database, your application queries a decentralized peer-to-peer network via an injected browser provider. Today, we’re going to walk through the exact steps to build a bulletproof MetaMask connection flow in React. Grab your coffee, open your terminal, and let's turn some code into Web3 magic.

## Understanding the Injected Provider: window.ethereum
When a user installs the MetaMask extension, it injects a global JavaScript object into their browser under `window.ethereum`. This object is an Ethereum Provider that complies with the EIP-1193 standard. It is the bridge between your React application and the Ethereum blockchain.

Through `window.ethereum`, your frontend can:
1. Detect if an Ethereum wallet extension is active.
2. Request the user's public cryptographic address (their identity).
3. Query the blockchain for balances, transaction receipts, and contract state.
4. Prompt the user to sign messages or authorize smart contract transactions.

```
+------------------+         +--------------------+         +--------------------+
|  React Frontend  | <=====> | window.ethereum    | <=====> | Ethereum Blockchain|
|  (User UI)       |         | (MetaMask Bridge)  |         | (Decentralized Net)|
+------------------+         +--------------------+         +--------------------+
```

Before doing any blockchain queries, your application must first verify that `window.ethereum` exists. If it doesn't, the user doesn't have MetaMask installed, and your UI needs to gracefully guide them to download it.

## The Connection Logic: Code Walkthrough
Let's build a clean, modular React component that handles connecting, checking state, and responding to network events. We will use React Hooks (`useState` and `useEffect`) to manage our wallet state cleanly.

Here is the complete implementation of a standard "Connect Wallet" component. We will walk through the critical parts right after:

```jsx
import React, { useState, useEffect } from 'react';

export default function WalletConnect() {
  const [errorMessage, setErrorMessage] = useState(null);
  const [defaultAccount, setDefaultAccount] = useState(null);
  const [userBalance, setUserBalance] = useState(null);
  const [connButtonText, setConnButtonText] = useState('Connect Wallet');

  // Request access to the user's accounts
  const connectWalletHandler = async () => {
    if (window.ethereum && window.ethereum.isMetaMask) {
      try {
        // Request accounts via EIP-1193 standard method
        const accounts = await window.ethereum.request({
          method: 'eth_requestAccounts',
        });
        accountChangedHandler(accounts[0]);
        setConnButtonText('Wallet Connected');
      } catch (error) {
        setErrorMessage(error.message);
      }
    } else {
      setErrorMessage('Please install MetaMask extension to continue.');
    }
  };

  // Update account state and request balance
  const accountChangedHandler = async (newAccount) => {
    setDefaultAccount(newAccount);
    try {
      const balance = await window.ethereum.request({
        method: 'eth_getBalance',
        params: [newAccount, 'latest'],
      });
      // Convert hexadecimal balance to human-readable Ether (in Wei format initially)
      const etherBalance = parseFloat(parseInt(balance, 16) / 10 ** 18).toFixed(4);
      setUserBalance(etherBalance);
    } catch (error) {
      setErrorMessage('Error fetching balance.');
    }
  };

  // Handle network/account changes dynamically
  const chainChangedHandler = () => {
    // Reload the page to avoid stale state issues across different networks
    window.location.reload();
  };

  // Setup event listeners for MetaMask state changes
  useEffect(() => {
    if (window.ethereum) {
      window.ethereum.on('accountsChanged', (accounts) => {
        if (accounts.length > 0) {
          accountChangedHandler(accounts[0]);
        } else {
          // User disconnected all accounts from the dApp
          setDefaultAccount(null);
          setUserBalance(null);
          setConnButtonText('Connect Wallet');
        }
      });

      window.ethereum.on('chainChanged', chainChangedHandler);
    }

    // Clean up event listeners on component unmount
    return () => {
      if (window.ethereum) {
        window.ethereum.removeListener('accountsChanged', accountChangedHandler);
        window.ethereum.removeListener('chainChanged', chainChangedHandler);
      }
    };
  }, []);

  return (
    <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px', maxWidth: '400px' }}>
      <h3>MetaMask Integration</h3>
      <button 
        onClick={connectWalletHandler}
        style={{
          backgroundColor: defaultAccount ? '#4CAF50' : '#FF9800',
          color: 'white',
          padding: '10px 15px',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          fontWeight: 'bold'
        }}
      >
        {connButtonText}
      </button>

      {defaultAccount && (
        <div style={{ marginTop: '20px' }}>
          <p><strong>Address:</strong> {defaultAccount.substring(0, 6)}...{defaultAccount.substring(38)}</p>
          <p><strong>Balance:</strong> {userBalance} ETH</p>
        </div>
      )}

      {errorMessage && (
        <p style={{ color: 'red', marginTop: '15px', fontSize: '14px' }}>
          <strong>Error:</strong> {errorMessage}
        </p>
      )}
    </div>
  );
}
```

## Deconstructing the Magic: Important Details
Let's highlight the specific details that will save you days of head-scratching when deployment errors hit.

### 1. The accountChangedHandler
When the user connects, MetaMask returns an array containing their hexadecimal public address. We save the first element `accounts[0]` to our state.
But here's the catch: the wallet balance returned by `eth_getBalance` is formatted in **hexadecimal Wei** (the smallest denomination of Ether, where 1 ETH = 10^18 Wei). To convert this value to a normal human decimal representation, we parse the hex value into an integer using `parseInt(balance, 16)` and then divide by `10 ** 18`.

### 2. Dynamically Responding to User Actions
MetaMask is highly dynamic. Users can switch accounts directly within the extension, or they can switch from the Ethereum Mainnet to a test network like Rinkeby or Kovan.
To prevent your dApp frontend from showing stale or incorrect data, we use the `window.ethereum.on` listener API:
- `accountsChanged`: Triggered whenever the user selects a different wallet address. If the array is empty, it means they disconnected their wallet from your site entirely.
- `chainChanged`: Triggered when the active blockchain network changes. The standard practice recommended by MetaMask is to run `window.location.reload()` on chain changes, ensuring all cached states are cleared and reset safely.

## Best Practices for Web3 Frontends
When building a professional Web3 frontend in January 2021, keep these battle-tested development guidelines in mind:

- **Graceful Onboarding**: Do not force your application to request connection immediately on page load. It is incredibly annoying for users. Always provide an explicitly designed "Connect Wallet" button so the user is in control of when they grant access to their address.
- **Address Masking**: Hexadecimal public keys are long, ugly strings. Always mask the middle of the address when displaying it in your header UI—e.g., `0x71C...497a`.
- **Comprehensive Error Handling**: Users can cancel the signature request popup in MetaMask, which will trigger a rejection error code `4001`. Ensure your application catches and logs this without crashing the interface.

Building dApps is an exciting frontier. By mastering the basic EIP-1193 provider connection logic in React, you now have the fundamental foundation to interact with complex decentralized protocols, query blockchain state, and build next-generation internet-native software.

## Key Takeaways
- **The Injected Bridge**: The `window.ethereum` object acts as the standard EIP-1193 bridge between React frontends and blockchain networks.
- **Address-Based Identity**: In Web3, users authorize using their public keys, eliminating the need for traditional email/password databases.
- **Hexadecimal Handling**: Blockchain nodes return financial numbers (like balance values) in hexadecimal Wei, requiring format parsing in JS.
- **Dynamic Change Listeners**: Listening to `accountsChanged` and `chainChanged` ensures the UI remains consistent when users swap accounts or networks.

## Frequently Asked Questions

**Q: Can we use libraries like ethers.js or web3.js instead of raw window.ethereum requests?**
A: Yes. Libraries like ethers.js and web3.js wrap around the raw injected provider `window.ethereum` to offer high-level utility functions, cleaner syntax, and pre-packaged contract interaction APIs. However, understanding the raw provider is critical for debugging connection issues.

**Q: Why does MetaMask recommend reloading the page on chainChanged?**
A: Different networks have different state roots, smart contract addresses, and gas parameters. Reloading the page ensures that no state remains from the previous network, preventing critical transaction errors.

**Q: Can a dApp steal a user's funds just by connecting their wallet?**
A: No. Simply connecting your wallet only shares your public key address with the application. To move funds or interact with contracts, the application must explicitly request you to sign and confirm a transaction via a MetaMask popup.

---

*If this gave you even one useful insight, subscribe — I drop these every week.*

*— [Shantanu Vishwanadha](https://substack.com/@thecoderpanda)*
