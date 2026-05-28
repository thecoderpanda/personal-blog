---
title: "The Graph Protocol: Indexing Blockchain Data Like a Pro"
subtitle: "A tutorial on writing subgraphs, query mappings, and boosting dApp frontend speeds."
date: "2021-08-28"
author: "Shantanu Vishwanadha"
authorUrl: "https://substack.com/@thecoderpanda"
tags: ["tutorials", "the-graph", "subgraph", "graphql"]
seoTitle: "GraphQL Subgraphs: Indexing Blockchain Data"
seoDescription: "Querying raw blockchain data is slow. Learn how to write custom subgraphs with The Graph Protocol to index event data and boost your React frontend speeds."
featuredImage: "https://images.unsplash.com/photo-1516116216624-53e697fedbea?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
imageAlt: "Structured programming functions displaying complex data index setups"
category: "tutorials"
readingTime: "6 min read"
slug: "graph-protocol-indexing-blockchain-data"
---

# The Graph Protocol: Indexing Blockchain Data Like a Pro

> **TL;DR:** Building a modern Web3 frontend requires instant access to data. But querying raw blockchain nodes directly is an absolute performance disaster. Enter The Graph Protocol, the decentralized indexer of Web3. In this tutorial, we will write a custom subgraph, configure schema files, define AssemblyScript event mappings, and query our data using GraphQL to supercharge your dApp's speeds.

Have you ever clicked a button in a decentralized application (dApp) and sat there, frozen in time, while a loading spinner stared back at you for 45 seconds? We've all been there. It is the silent killer of Web3 user experience. The reason for this latency is a fundamental architectural limitation: traditional blockchain RPC nodes (like Infura or Alchemy) are designed for verifying transactions, executing smart contract calls, and maintaining consensus state. They are *not* designed for complex relational databases queries, full-text search, or fast historical lookups.

If you ask an Ethereum node: "Give me all the active NFT listings created by a specific user, sorted from lowest to highest price," the node will choke. To answer that question, you would have to manually fetch every single block, parse every transaction event since the genesis block, reconstruct the market state in memory, and then filter the results on your frontend. It is a slow, expensive, and completely unscalable approach. 

The Graph Protocol solves this problem elegantly, acting as the decentralized SQL indexing layer of Web3. In this guide, we'll build a custom subgraph to index our NFT marketplace events, enabling our React frontend to retrieve complex data structures in milliseconds using standard GraphQL queries.

## The Core Blueprint: Manifest, Schema, and Mappings

To index smart contract data using The Graph, we must define a **Subgraph**. A subgraph is a structured configuration consisting of three core files:

1. **`subgraph.yaml` (The Manifest)**: This is the entry point. It tells The Graph which smart contracts to listen to, which block to start indexing from, which cryptographic events (like `LogListed` or `LogPurchased`) to intercept, and which handler functions to execute when those events are detected.
2. **`schema.graphql` (The Data Schema)**: This file defines the actual data structures (entities) we want to store and expose. It uses standard GraphQL schema definition language (SDL). You define your entities, relations, and data types (Strings, BigInts, Bytes, Booleans) here.
3. **`src/mapping.ts` (The Mappings)**: This is where the magic happens. Mappings are written in AssemblyScript (a strict subset of TypeScript that compiles to WebAssembly). These mapping functions intercept Ethereum event logs, parse their parameters, instantiate our defined GraphQL entities, and save them directly to The Graph’s decentralized database nodes.

## Hands-on Implementation Tutorial

Let's write a custom subgraph to index our previously built NFT marketplace contract. 

First, we define our **`schema.graphql`**. We want to store a clean representation of token listings so our React dApp can query them instantly. Note the `@entity` decorator, which signals to The Graph compiler that this structure must be compiled into a database table.

```graphql
# schema.graphql

type TokenListing @entity {
  id: ID!
  seller: Bytes!       # Address of the seller
  nftContract: Bytes!  # Address of the ERC-721 contract
  tokenId: BigInt!     # ID of the NFT
  price: BigInt!       # Price in Wei
  active: Boolean!     # Active state
}
```

Next, we write the **`subgraph.yaml`** manifest. This configuration bridges the contract's event logs on-chain with our AssemblyScript mappings.

```yaml
# subgraph.yaml
specVersion: 0.0.2
schema:
  file: ./schema.graphql
dataSources:
  - kind: ethereum/contract
    name: NFTMarketplace
    network: mainnet
    source:
      address: "0xYourMarketplaceContractAddress"
      abi: NFTMarketplace
      startBlock: 12965000
    mapping:
      kind: ethereum/events
      apiVersion: 0.0.5
      language: wasm/assemblyscript
      entities:
        - TokenListing
      abis:
        - name: NFTMarketplace
          file: ./abis/NFTMarketplace.json
      eventHandlers:
        - event: LogListed(uint256,address,address,uint256,uint256)
          handler: handleLogListed
      file: ./src/mapping.ts
```

Finally, we write our mapping function in **`src/mapping.ts`**. We'll write the AssemblyScript logic to process the raw `LogListed` event and write it to our database entity.

```typescript
// src/mapping.ts
import { LogListed as LogListedEvent } from "../generated/NFTMarketplace/NFTMarketplace"
import { TokenListing } from "../generated/schema"

export function handleLogListed(event: LogListedEvent): void {
  // Use the unique listing ID from event parameters as the entity ID
  let listing = new TokenListing(event.params.listingId.toString())

  // Map the event parameters to our database fields
  listing.seller = event.params.seller
  listing.nftContract = event.params.nftContract
  listing.tokenId = event.params.tokenId
  listing.price = event.params.price
  listing.active = true

  // Save the entity to the Graph Node store
  listing.save()
}
```

Once written, you run the `graph codegen` command to compile your schemas and AssemblyScript files, followed by `graph deploy` to push the subgraph to The Graph’s hosting service or decentralized network.

## Querying the Subgraph from React

Now that your data is indexed, querying it from your React frontend is incredibly simple and blazing fast. You don't need any complex Web3 providers or manual loop parsers. You simply execute a standard HTTP POST request containing a GraphQL query.

Here is how you query the 10 lowest-priced active listings from your subgraph in a single, high-performance request:

```javascript
import { useEffect, useState } from "react";

const SUBGRAPH_URL = "https://api.thegraph.com/subgraphs/name/yourusername/your-marketplace";

const QUERY_ACTIVE_LISTINGS = `
  query {
    tokenListings(
      first: 10,
      where: { active: true },
      orderBy: price,
      orderDirection: asc
    ) {
      id
      seller
      nftContract
      tokenId
      price
    }
  }
`;

export function useActiveListings() {
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(SUBGRAPH_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: QUERY_ACTIVE_LISTINGS }),
    })
      .then((res) => res.json())
      .then((result) => {
        setListings(result.data.tokenListings);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch listings:", err);
        setLoading(false);
      });
  }, []);

  return { listings, loading };
}
```

This React custom hook replaces hundreds of lines of fragile node-querying boilerplate. It queries the data instantly, updating your user interface in milliseconds, giving your decentralized application the look, feel, and performance of a modern Web2 platform.

## Key Takeaways
- **Compute Offloading**: Decouple state storage from state queries. Let smart contracts handle updates, and let subgraphs handle reads.
- **AssemblyScript Translation**: AssemblyScript mappings serve as compilation bridges, translating raw binary Ethereum logs into structured entity tables.
- **GraphQL Power**: Querying data with GraphQL allows frontends to request the exact fields they need, reducing payload sizes and latency.
- **Speed is UX**: Moving from RPC queries to custom subgraphs drops dApp data loading times from 30+ seconds to sub-100 milliseconds.

## Frequently Asked Questions

**Q: Can I just write my indexing logic using a traditional Node.js/PostgreSQL server?**
A: Yes, but it introduces major centralization and maintenance overhead. If your server crashes or loses internet connection, you miss block events and display stale data. Running on The Graph provides a decentralized, highly redundant indexing network that is continuously synchronized by nodes globally.

**Q: What happens if a smart contract event is modified or updated?**
A: If you change your smart contract's event structure, you must update your `subgraph.yaml` manifest and mapping handler logic, then increment the subgraph version and re-deploy. The Graph will re-index your entire smart contract history from the start block to sync the new schema.

**Q: Is querying data from subgraphs on The Graph free?**
A: On the hosted service, query endpoints are free to use. As the network transitions fully to the decentralized mainnet, developers pay a minimal query fee in GRT (The Graph's utility token) using state channels, which is highly efficient and costs fractions of a cent per request.

---

*If this gave you even one useful insight, subscribe — I drop these every week.*

*— [Shantanu Vishwanadha](https://substack.com/@thecoderpanda)*