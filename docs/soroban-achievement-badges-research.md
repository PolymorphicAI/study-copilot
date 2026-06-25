# Soroban Achievement Badges Research

Study Copilot may eventually issue verifiable study achievements for learners. Soroban can support that goal, but the first design should keep private study content off-chain and separate achievement evidence from reward mechanics.

## Research Sources

- Soroban smart contracts overview: https://developers.stellar.org/docs/build/smart-contracts/overview
- Soroban data storage: https://developers.stellar.org/docs/build/smart-contracts/data-storage
- Soroban token interface: https://developers.stellar.org/docs/build/smart-contracts/tokens
- Stellar account model: https://developers.stellar.org/docs/learn/fundamentals/stellar-data-structures/accounts

## Possible Achievement Types

Good early badge candidates are objective, low-stakes, and easy to explain:

- First study session completed.
- First quiz answered correctly.
- Seven-day study streak reached.
- Topic review completed with a minimum number of cards viewed.
- Notes-to-cards flow used successfully.
- PDF-to-cards flow used successfully.
- Accessibility or keyboard-navigation practice completed.

Avoid early badges for sensitive or high-stakes claims:

- Grades, exam readiness, medical or legal learning outcomes.
- Exact study topics that may reveal private academic or workplace material.
- Claims that depend on hidden AI quality scoring.
- Rewards that can be farmed without stronger abuse controls.

## Soroban Representation Options

### Contract-Recorded Achievement Events

A Soroban contract can emit or store a compact achievement record for a verified learner wallet.

Suggested fields:

```json
{
  "learner": "G...",
  "badge_id": "first_quiz_correct",
  "issued_at": 1782432000,
  "evidence_hash": "sha256:...",
  "metadata_uri": "ipfs://..."
}
```

Best fit:

- Verifiable proof that a badge was issued.
- Portable achievement references.
- Minimal on-chain state.

Tradeoffs:

- Requires wallet identity and transaction-signing flow.
- On-chain state and events are public.
- Evidence hashes can still become privacy-sensitive if source data is guessable.

### Non-Transferable Badge Token

Soroban token contracts could model achievement badges as tokens, but a badge should usually be non-transferable or tightly permissioned so a learner cannot sell or move proof-of-learning claims.

Best fit:

- Future interoperable badge display.
- Wallet-native ownership semantics.
- Public profile experiments.

Tradeoffs:

- Transferability must be intentionally restricted.
- Token semantics may imply financial value even when the badge is only a credential.
- More contract and UX complexity than an event or registry record.

### Off-Chain Badge Registry With On-Chain Anchor

Study Copilot can store badge details off-chain and anchor only a hash or registry pointer on Soroban.

Best fit:

- Privacy-preserving MVP.
- Rich badge metadata without large on-chain payloads.
- Easier deletion or correction of off-chain user-facing metadata.

Tradeoffs:

- Requires reliable off-chain hosting.
- Verifiers need both the on-chain anchor and the off-chain metadata.
- Deletion and mutability rules need clear documentation.

## On-Chain Versus Off-Chain Metadata

Keep on-chain data minimal:

- learner public key or profile contract ID
- badge ID
- issued timestamp
- issuer contract or admin address
- hash of evidence summary
- metadata URI or versioned schema ID

Keep off-chain data:

- badge display name and description
- icon or image
- localized copy
- detailed criteria text
- user-facing progress summaries
- revocation or correction notes

Never put these on-chain:

- Uploaded PDFs, pasted notes, extracted text, or prompts.
- Exact private study topics unless the learner explicitly opts in.
- Email, school, employer, grades, accommodations, or other personal data.
- Raw quiz answers or detailed behavioral logs.

## MVP Badge Recommendation

Start with an off-chain badge registry and optional Soroban anchor on testnet:

1. Define a small fixed badge catalog in the app.
2. Let users study without a wallet.
3. If a learner connects a verified Stellar wallet, allow optional badge anchoring.
4. Store badge display metadata off-chain.
5. Put only a badge ID, learner public key, timestamp, and evidence hash on-chain.
6. Keep rewards separate until anti-abuse controls are stronger.

This approach gives Study Copilot a credible path to verifiable achievements without exposing study material or overcommitting to token economics.

## Issuance Flow

1. Learner completes an achievement-worthy action.
2. Backend evaluates local criteria, such as quiz correctness or streak count.
3. App shows a preview of the badge and explains whether anchoring is optional.
4. Learner connects a wallet or continues with an off-chain badge only.
5. Backend prepares a compact evidence summary and hash.
6. Soroban contract records the badge claim or emits an achievement event.
7. App stores the off-chain badge metadata and links it to the wallet identity record.

## Risks And Open Questions

- How should badges be revoked or corrected after issuance?
- Should badges be transferable, soulbound, or only displayed through Study Copilot?
- Who is allowed to issue badges: the app backend, a DAO, or a multisig-controlled issuer?
- How will the app prevent badge farming through scripted sessions?
- How much detail can be included in evidence without revealing private study material?
- What happens if the learner rotates or loses the linked wallet?
- Should testnet badges be clearly separated from any future mainnet credentials?

## Next Steps

- Pair this design with wallet identity research before building contracts.
- Create a badge catalog with stable IDs and criteria.
- Prototype a testnet-only contract that records a badge ID, learner address, timestamp, and evidence hash.
- Add privacy review for metadata and evidence hashing.
- Add anti-abuse requirements before any reward-bearing badge is issued.
