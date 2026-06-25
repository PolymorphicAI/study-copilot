# Stellar Wallet Identity Research

Study Copilot may eventually let learners connect a Stellar wallet so learning progress, achievements, and rewards can become portable. This document outlines wallet options, a learner identity flow, UX considerations for non-crypto learners, and implementation risks.

## Research Sources

- Stellar Wallet SDK: https://developers.stellar.org/docs/build/apps/wallet/overview
- Stellar Wallets Kit: https://github.com/Creit-Tech/Stellar-Wallets-Kit
- Freighter API: https://docs.freighter.app/docs/guide/introduction
- Stellar account model: https://developers.stellar.org/docs/learn/fundamentals/stellar-data-structures/accounts

## Wallet Connection Options

### Freighter Browser Extension

Freighter is a familiar browser-extension path for Stellar users. It can provide wallet availability checks, public-key access, network selection, and transaction signing in web apps.

Best fit:

- Desktop web MVP.
- Learners who already have a Stellar wallet.
- Developer testing on testnet.

Tradeoffs:

- Extension installation is an extra step for new learners.
- Mobile support and embedded-browser flows need separate review.
- The app must handle missing extension, locked wallet, wrong network, and declined signature states.

### Stellar Wallets Kit

Stellar Wallets Kit provides a higher-level multi-wallet integration layer for Stellar wallets. It can help avoid coupling Study Copilot to one wallet provider too early.

Best fit:

- A wallet-agnostic integration path.
- Future support for multiple Stellar wallets.
- Cleaner UI around "connect wallet" choices.

Tradeoffs:

- Adds a frontend dependency and adapter layer.
- Requires wallet-specific testing across supported providers.
- The app still needs a clear identity model after a wallet returns a public key.

### Manual Public Key Entry

Study Copilot could allow users to paste a Stellar public key before full wallet connection exists.

Best fit:

- Early research prototypes.
- Read-only identity display.
- Learners who want to preview wallet-linked achievements without signing.

Tradeoffs:

- No proof that the learner controls the address.
- Easy to mistype or paste another user's public key.
- Should not unlock rewards, credentials, or account recovery by itself.

## Recommended Learner Identity Flow

1. User studies normally without a wallet.
2. User opens an optional "Connect wallet" action from profile or achievements.
3. App explains that wallet connection is optional and is used for portable learner identity, not required for studying.
4. User selects a wallet provider, such as Freighter or a kit-supported wallet.
5. App requests the public key and checks the selected network.
6. App asks the wallet to sign a short, human-readable challenge that includes:
   - app name
   - purpose, such as "Link this wallet to Study Copilot"
   - timestamp
   - nonce
   - network
7. Backend verifies the signature and creates a wallet-link record.
8. App stores only the public key, verification timestamp, network, and learner profile reference.
9. Achievements and rewards reference the verified wallet identity, not raw uploaded study materials.

## Non-Crypto Learner UX

Wallet identity should not be required for the core study loop. Learners should be able to generate cards, upload notes, practice quizzes, and track local progress before understanding Stellar.

Recommended copy:

> Connect a Stellar wallet only if you want portable achievements or future rewards. You can keep studying without one.

UX guidance:

- Make wallet connection optional and reversible.
- Use "learning profile" language before "crypto wallet" language.
- Explain public keys as public identifiers, not passwords.
- Never ask for seed phrases or private keys.
- Provide a testnet-only development mode.
- Show clear recovery guidance if a learner loses wallet access.

## Data Model Notes

A minimal wallet identity record could include:

```json
{
  "learner_id": "local-or-account-id",
  "stellar_public_key": "G...",
  "network": "testnet",
  "verified_at": "2026-06-26T00:00:00Z",
  "verification_method": "signed_challenge",
  "status": "active"
}
```

Do not store:

- Secret keys, seed phrases, recovery phrases, or raw wallet session secrets.
- Full uploaded materials, notes, prompts, or PDF text as wallet-linked identity evidence.
- On-chain references that expose private study topics or sensitive learning history.

## Implementation Risks

- Learners may confuse public keys, secret keys, and wallet recovery phrases.
- A wallet address is pseudonymous, not automatically a real-world identity.
- Wallet-linking can expose cross-app activity if the same address is reused.
- Signed challenges must use nonces to prevent replay.
- Mainnet rewards create abuse, tax, and compliance questions.
- Wallet provider APIs can differ by browser, device, and network.
- A compromised local account could link an attacker's wallet unless re-authentication is required.

## MVP Recommendation

Start with optional testnet wallet linking for achievements only:

- Use Freighter or Stellar Wallets Kit for public-key access and signed challenge proof.
- Keep normal study flows wallet-free.
- Store only a verified public key and minimal profile metadata.
- Do not write uploaded study materials or detailed learning activity on-chain.
- Do not ship token rewards in the first wallet identity MVP.

This gives Study Copilot a path toward portable learner identity while keeping the first integration understandable, reversible, and lower-risk.

## Next Steps

- Prototype a frontend wallet connection button in a non-production branch.
- Define the signed challenge message format.
- Add backend signature verification research for Stellar public keys.
- Decide whether the first wallet integration should use Freighter directly or Stellar Wallets Kit.
- Pair this with achievement badge and reward anti-abuse research before enabling mainnet features.
