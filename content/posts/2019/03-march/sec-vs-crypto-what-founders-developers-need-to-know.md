---
title: "SEC vs. Crypto: What Founders and Developers Need to Know"
subtitle: "When the Howey Test meets smart contracts, and how to write code without getting a call from a government agency."
date: "2019-03-20"
author: "Shantanu Vishwanadha"
authorUrl: "https://substack.com/@thecoderpanda"
tags: ["blockchain", "regulation", "sec", "smart-contracts", "startups"]
seoTitle: "SEC vs. Crypto: What Founders & Devs Need to Know (2019)"
seoDescription: "An essential regulatory guide for crypto founders and Web3 developers in 2019. Understand the SEC, the Howey Test, and how to write smart contracts safely."
featuredImage: "https://images.unsplash.com/photo-1609921212029-bb5a28e60960?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
imageAlt: "A physical Bitcoin coin resting on a dark surface, symbolizing the regulatory scrutiny and financial complexity of cryptocurrency markets."
category: "blockchain"
readingTime: "7 min read"
slug: "sec-vs-crypto-what-founders-developers-need-to-know"
---

# SEC vs. Crypto: What Founders and Developers Need to Know

> **TL;DR:** The era of raising $20 million on a napkins-and-dreams whitepaper is officially over. The SEC is actively policing the space, and founders can no longer hide behind terms like \"utility token.\" To survive, you must understand the Howey Test, realize that the SAFT model is on thin ice, and design your protocols for genuine, operational decentralization from day one.

Remember 2017? It was a magical time. You could copy-paste an ERC-20 contract, write a 12-page whitepaper containing the words \"decentralized AI on the blockchain,\" and walk away with $30 million in Ethereum before you had even written a single line of actual product code. Fast forward to March 2019, and the hangover has officially set in. The music has stopped, the lights are on, and standing at the door is the Securities and Exchange Commission (SEC), wearing a very serious suit and carrying a clipboard full of subpoenas.

If you are a blockchain founder or developer today, the regulatory landscape can feel like a minefield where every step might trigger an enforcement action. VCs who once practically begged to throw cash at your token pre-sale are now muttering about compliance and compliance-first structures. But instead of packing up your bags or fleeing to a tropical island with no extradition treaty, you need to understand how the rules of the road are changing. Regulators aren't trying to destroy technology; they are applying eighty-year-old laws to digital assets, and if you understand their framework, you can build without the constant fear of a government agency knocking on your door.

## The Howey Test for the Decentralized Soul

At the heart of every single SEC enforcement action is a piece of legal doctrine from 1946 called the **Howey Test**. Long before computers, let alone cryptography, existed, a company in Florida sold portions of a citrus grove to buyers, along with a contract to service the land and harvest the oranges. The Supreme Court ruled that this arrangement constituted an \"investment contract\" (and therefore a security). 

The SEC translates this eighty-year-old orange grove law into four simple prongs for your shiny new utility token:
1. **An investment of money**: Users buy your token using fiat or other cryptocurrencies like ETH or BTC. (Yes, the SEC considers crypto to be \"money\" for this test).
2. **In a common enterprise**: The funds are pooled together, and the success of the project is tied to the collective fortune of the group.
3. **With an expectation of profits**: Investors are buying your token hoping its value will increase, rather than just using it for its utility.
4. **Solely from the efforts of others**: The profit depends on the efforts of the core development team, founders, or promoters.

Here is the developer translation: if you raise money by promising that your team will build a revolutionary decentralized database, and that the token will appreciate in value once the database is finished, you have just sold a security. It doesn't matter if you call it a \"utility token,\" a \"membership voucher,\" or \"magic internet points.\" The SEC looks at economic reality, not your clever marketing vocabulary.

## The SAFT Model is on Life Support

For a brief window in late 2017 and 2018, the industry thought it had solved this dilemma with the Simple Agreement for Future Tokens (SAFT). The idea was simple: sell a SAFT (which is clearly a security) to accredited investors to fund development. Once the network is fully built and functional, deliver the actual tokens, which are now \"utility tokens\" because the network is live.

In 2019, that theory is looking incredibly fragile. 

Recent enforcement actions against projects like AirFox and Paragon have shown that the SEC does not believe a security magically transforms into a non-security just because you shipped some code. If the initial distribution of the token was driven by speculative investment intent, the subsequent delivery of those tokens remains part of that integrated securities offering. 

If you are relying on a SAFT to fund your startup, you need to tread very carefully. The SEC’s perspective is that if a token's value is highly correlated with the ongoing managerial and entrepreneurial efforts of your team, it is a security. If you are distributing tokens to the public while your network is still in its infancy, you are playing legal Russian roulette with a fully loaded chamber.

## When Code Becomes a Crime: The Developer's Dilemma

For a long time, software engineers believed they were insulated from regulatory fallout. \"We just write open-source code,\" the mantra went. \"We don't operate the systems; we just publish mathematical instructions to the public blockchain.\"

Then came the SEC's action against Zachary Coburn, the founder of EtherDelta.

EtherDelta was a decentralized exchange (DEX) that ran entirely on Ethereum smart contracts. Coburn wrote the code, deployed the smart contracts to the mainnet, and created a simple frontend interface to let users interact with them. He didn't custody user funds, and he didn't manually match buy and sell orders—the smart contracts did that autonomously. Yet, the SEC charged Coburn with operating an unregistered national securities exchange. 

The SEC's logic was simple: Coburn designed, deployed, and maintained a system that facilitated the trading of digital asset securities, and he profited from the transaction fees generated by those contracts. This was a massive wake-up call for open-source developers. You cannot write a financial protocol, retain administrative control over it (like admin keys or upgradeability), profit from its operation, and then claim you are \"just a developer.\" If you write code that acts like an exchange or a broker-dealer, and you run the infrastructure that makes it happen, the SEC will treat you as an exchange or a broker-dealer.

## Survival Strategies: How to Build in 2019 Without Going to Jail

So, how do you build a blockchain startup in this environment without spending your runway on defense lawyers? Here are a few practical rules for 2019:

First, **abandon the pre-product token sale**. If you need capital to build your MVP, raise traditional equity from venture capitalists or angel investors. Do not issue a token before you have a functional, decentralized network where that token can actually be used for its intended purpose. 

Second, **design for true decentralization from day one**. If your protocol relies on your team to run the servers, update the smart contracts, and curate the content, it is centralized. True utility tokens exist on networks where the creator could vanish tomorrow, and the network would continue to run seamlessly. Think Bitcoin or Ethereum. If you can't step away from your project without it dying, your token is probably a security.

Third, **focus on actual utility over price appreciation**. Stop talking about token liquidity, exchange listings, and yield-generating mechanics on your public channels. If your community Telegram is 90% price discussion and 10% tech discussion, you are building a securities case against yourself. Build tools that developers and users actually want to use, and let the organic utility of the network drive token demand, rather than marketing-driven hype.

The crypto winter is weeding out the speculative noise, which gives serious builders the perfect opportunity to design compliant, robust architectures. The SEC isn't going away, but by shifting your focus from speculative token launches to building genuine, open-source utility, you can make sure your startup survives to see the next spring.

## Key Takeaways

- **[Howey rules supreme]**: The SEC looks at economic substance over form. Calling a token a \"utility token\" does not protect you if it behaves like a speculative investment.
- **[SAFT is not a silver bullet]**: The SEC has made it clear that raising funds via a SAFT and later distributing tokens on a \"live\" network does not automatically prevent those tokens from being classified as securities.
- **[Developers are not immune]**: Writing and deploying smart contracts that facilitate unregistered securities trading can lead to severe regulatory enforcement, as seen in the EtherDelta precedent.
- **[Equity first, tokens later]**: Fund your early-stage development with traditional equity or grants. Only introduce a token when your protocol is operational and requires a native unit of account.

## Frequently Asked Questions

**Q: Can we avoid the SEC by incorporating our crypto startup in Switzerland or Singapore?**
A: No. If your project sells tokens to US citizens or residents, the SEC claims jurisdiction over those transactions, regardless of where your corporate entity is registered. Geographic arbitrage is not a viable compliance strategy.

**Q: If our smart contracts are completely immutable, can we still be held liable for their operation?**
A: Yes. If you wrote the code, deployed it, built the frontend website that users access, and maintained control over the domain or marketing, regulators will look at your overall role in operating the platform, even if the underlying smart contracts cannot be modified.

**Q: Does every token distribution have to be a securities offering?**
A: Not necessarily. If a token is distributed strictly via non-investment mechanisms (like utility-focused airdrops to active network participants) and has immediate, functional utility on a sufficiently decentralized network, it is much less likely to be classified as a security.

---

*If this made you think, it'll do even more when shared. Hit that subscribe button — I write about blockchain and software development every week and I promise to keep it real.*

*— [Shantanu Vishwanadha](https://substack.com/@thecoderpanda)*
