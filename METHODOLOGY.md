# Methodology: Exception Classification Design

This explains the reasoning behind the reconciliation engine's exception taxonomy, not just what it does, but why each category exists.

## Core Principle
A break is only escalated as a genuine problem once it's been checked against every *expected* reason two independent records might temporarily disagree. Most breaks aren't errors; they're timing artifacts of normal institutional processes.

## Classification Hierarchy (in order of evaluation)
1. **Missing entirely from one side**: the most severe category; flagged immediately as `UNRECORDED_AT_CUSTODIAN` or `UNBOOKED_INTERNAL_TRADE`.
2. **Cash-only variance on a cash position**: checked for a genuine balance break.
3. **Unlisted/Alternatives assets**: market value variances here are checked against independent valuation cycle timing before being classified as a lag rather than an error, since these assets reprice quarterly, not daily.
4. **Fixed Income coupon timing**: similarly checked against known payment schedules before assuming an error.
5. **Small, corporate-action-plausible quantity shifts**: checked against known DRP-style events before assuming a hard quantity break.
6. **Remaining quantity mismatches**: classified as genuine `QUANTITY_BREAK`.
7. **Remaining market value mismatches**: checked against an FX tolerance band (non-AUD holdings, variance under 0.8%) before being classified as expected FX timing rather than a real pricing error.

## Why This Order Matters
Each check exists specifically to prevent a false-alarm escalation for a known, benign timing pattern, mirroring how a real reconciliation control avoids flooding an operations team with noise, reserving genuine investigation effort for breaks that don't have an obvious explanation.

---
*Maintained by Cohen Pikari ([github.com/cohen-pikari](https://github.com/cohen-pikari))*
