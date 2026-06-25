# Learning Rewards Anti-Abuse Considerations

Study Copilot may eventually reward learning activity through points, badges, or Stellar-linked incentives. Rewarded behavior can be gamed, so anti-abuse planning should happen before any reward has monetary or transferable value.

## Abuse Scenarios

### Fake Activity

- Scripted clients repeatedly call card view, quiz, or progress endpoints.
- Browser automation scrolls through cards without real study time.
- Users submit the same topic repeatedly to create easy sessions.
- Users paste trivial notes or generated filler text to trigger completion flows.
- Quiz answers are brute-forced until the correct option is found.

### Repeated Sessions

- A learner repeatedly resets sessions to claim first-session or first-topic rewards.
- The same uploaded material is renamed or slightly modified to appear new.
- Local storage is cleared to reset frontend-only progress.
- Users replay captured API requests after a reward rule is discovered.

### Multi-Account And Wallet Farming

- A single actor creates many accounts or wallets to farm welcome rewards.
- Wallets are rotated to bypass per-wallet caps.
- Learners share one completed session across many accounts.
- Referral or team rewards are abused through self-referrals.

### Sensitive Material Abuse

- Users upload private, copyrighted, or regulated content to maximize reward output.
- Attackers include prompt-injection text that tries to alter scoring or reward logic.
- Public rewards reveal private study topics or learning patterns.

## Mitigation Strategies

### Rate Limits And Caps

- Cap reward-eligible actions per user, session, wallet, IP range, and device fingerprint where appropriate.
- Limit first-session and first-upload rewards to one claim per verified learner.
- Apply cooldowns between streak-qualified sessions.
- Set daily and weekly reward ceilings.
- Hold unusual activity for manual or delayed review instead of issuing immediately.

### Server-Side Verification

- Keep reward state on the backend; do not trust local storage or client timestamps.
- Require server-generated session IDs and one-time reward nonces.
- Track reward rule versions so old clients cannot replay retired rules.
- Record minimal event summaries, such as viewed card count, quiz attempts, and elapsed time.
- Validate that reward events belong to the same learner and session.

### Meaningful Engagement Checks

- Require a minimum number of cards viewed and a minimum elapsed time window.
- Combine quiz attempts with card interaction instead of rewarding clicks alone.
- Avoid rewarding repeated identical topics or duplicated uploaded material.
- Use broad duplicate detection, such as content hashes, without storing raw private material.
- Make high-value rewards depend on multiple signals, not one easily scripted event.

### Wallet And Identity Controls

- Keep rewards optional for learners who do not want wallet identity.
- Require signed wallet-link challenges before any wallet-linked reward.
- Separate testnet experiments from mainnet reward issuance.
- Delay transferable rewards until account, wallet, and abuse controls are stable.
- Provide a recovery or unlinking flow for lost or compromised wallets.

## Privacy Guardrails

- Do not place uploaded notes, PDF text, prompts, exact study topics, or quiz answers on-chain.
- Avoid public leaderboards until learners understand what is visible.
- Store only minimal reward evidence, such as a badge ID, timestamp, and privacy-preserving hash.
- Do not log raw uploaded study material as part of abuse analysis.
- Give users clear notice before activity becomes reward-eligible.

## Recommended MVP Policy

The first reward MVP should use off-chain, non-transferable points or badges:

1. Rewards have no cash value.
2. Rewards are capped per learner and per day.
3. Streak calculations use backend server time.
4. Uploaded content is not stored solely for reward verification.
5. Suspicious sessions can be denied without blocking normal studying.
6. Mainnet or transferable Stellar assets remain disabled.

This keeps the motivation layer useful for product learning while reducing the risk of turning Study Copilot into a farming target.

## Open Questions

- What minimum engagement threshold is fair without encouraging surveillance?
- Should rewards depend on quiz accuracy, time spent, streak consistency, or topic diversity?
- How should repeated study of the same material be treated?
- What evidence is enough to issue a badge without storing private notes?
- What activity should trigger manual review or delayed payout?
- Who can reverse or revoke a wrongly issued reward?
- What user-facing explanation should appear when a reward is denied?
- When, if ever, should rewards become transferable or mainnet-based?

## Pre-Launch Checklist

- Define every reward rule and abuse assumption before implementation.
- Add tests for duplicate claims, replayed requests, and exceeded caps.
- Add backend-side rate limits for reward endpoints.
- Add privacy review for every stored reward event field.
- Keep testnet and mainnet reward paths visibly separate.
- Revisit this document before any token, wallet, or paid reward launch.
