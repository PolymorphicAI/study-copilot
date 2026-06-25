# Stellar Study Streak Rewards Research

Study Copilot may eventually use Stellar assets to encourage consistent study habits. Rewards can be motivating, but they also add abuse, compliance, and product-risk concerns. This document outlines reward scenarios, Stellar asset options, abuse risks, and an MVP recommendation.

## Research Sources

- Stellar assets: https://developers.stellar.org/docs/learn/fundamentals/stellar-data-structures/assets
- Stellar accounts: https://developers.stellar.org/docs/learn/fundamentals/stellar-data-structures/accounts
- Stellar Asset Contract: https://developers.stellar.org/docs/tokens/stellar-asset-contract
- Soroban smart contracts overview: https://developers.stellar.org/docs/build/smart-contracts/overview

## Reward Scenarios

Potential reward triggers:

- Complete a first study session.
- Maintain a three-day or seven-day study streak.
- Complete a quiz set with a minimum accuracy threshold.
- Review a previously generated card after a delay.
- Finish a topic review flow without skipping every card.
- Use notes or PDF upload to create study material and then complete a review.

Reward design should favor consistency and meaningful engagement over raw clicks. Streak rewards should not require users to disclose sensitive topics, upload private documents, or connect a wallet before they understand the tradeoff.

## Stellar Asset Options

### Off-Chain Points First

Study Copilot can start with internal points that are not on-chain and cannot be transferred.

Best fit:

- Earliest MVP.
- UX experiments.
- Tuning streak rules before adding token value.

Tradeoffs:

- Not portable outside the app.
- Requires backend storage before points persist across sessions.
- Not independently verifiable.

### Classic Stellar Issued Asset

An issuer account can create a custom Stellar asset for rewards. Learners would need a Stellar account and trustline before receiving that asset.

Best fit:

- Simple transferable reward experiments.
- Wallet-native balances.
- Future community or sponsor reward programs.

Tradeoffs:

- Trustlines add UX complexity.
- Transferable assets can create market expectations.
- Issuer account custody and supply controls need operational planning.
- Mainnet issuance raises compliance, tax, and support questions.

### Stellar Asset Contract Or Soroban Token

The Stellar Asset Contract and Soroban token patterns can represent assets in smart-contract flows, including richer rules around minting, distribution, and integration with other contracts.

Best fit:

- Future programmable rewards.
- Badge-gated or contract-verified reward flows.
- Testnet contract prototypes.

Tradeoffs:

- More implementation complexity than off-chain points.
- Requires contract audits before real value is involved.
- Still needs anti-abuse controls outside the contract.

### Non-Transferable Credits

Rewards can be modeled as non-transferable credits or achievement-linked balances rather than open tokens.

Best fit:

- Learning motivation without creating a tradable asset.
- Lower economic risk.
- Badge or achievement unlocks.

Tradeoffs:

- Requires custom rules or off-chain enforcement.
- Less portable than normal Stellar assets.
- Users may still perceive credits as monetary value.

## Suggested Reward Flow

1. Learner studies without a wallet requirement.
2. App tracks local progress signals, such as cards viewed, quiz attempts, and streak days.
3. Backend verifies the reward rule and checks rate limits.
4. App shows a clear explanation of the earned reward.
5. If using off-chain points, backend updates the learner profile.
6. If using Stellar rewards, learner connects a verified wallet.
7. Backend queues or submits the reward transaction only after abuse checks pass.
8. App shows reward status: pending, issued, failed, or held for review.

## Abuse Risks

- Scripted clients can replay study sessions or quiz requests.
- Users can create many accounts or wallets to farm first-session rewards.
- Users can upload trivial or repeated content to trigger study flows.
- Learners may brute-force quizzes if reward rules only check correctness.
- Timezone and clock manipulation can fake streak boundaries.
- Transferable assets can encourage farming, resale, or bot participation.
- Reward incentives can reduce learning quality if points are easier than understanding.

## Mitigation Ideas

- Keep initial rewards off-chain and low/no monetary value.
- Use server-side streak state instead of trusting client timestamps.
- Rate-limit reward-eligible actions per learner, device, IP range, and wallet.
- Require meaningful intervals between streak days.
- Add minimum engagement checks, such as card dwell time plus quiz attempts.
- Cap daily rewards and add cooldowns.
- Delay on-chain issuance until a reward passes review thresholds.
- Use testnet only while reward economics are being validated.
- Pair rewards with anti-abuse research before enabling mainnet assets.

## MVP Recommendation

Rewards should be future work, not the first Stellar MVP.

Recommended path:

1. Ship wallet identity and achievement badges first.
2. Add off-chain, non-transferable streak points for experimentation.
3. Measure whether points improve study consistency without encouraging low-quality behavior.
4. Add testnet Stellar reward prototypes only after anti-abuse controls exist.
5. Defer mainnet or transferable rewards until legal, compliance, treasury, and support questions are answered.

This keeps Study Copilot focused on learning while still leaving a path to Stellar-native incentives later.

## Open Questions

- What reward value, if any, is appropriate for study streaks?
- Should rewards depend on quiz accuracy, completion, or verified time spent?
- How should users recover rewards if they lose a wallet?
- Should rewards be redeemable, transferable, or purely symbolic?
- Who funds and controls reward issuance?
- What user notice is needed before study behavior becomes reward-eligible?
