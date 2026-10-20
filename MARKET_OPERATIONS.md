# BULSHI market operations and evidence policy

## Current state (October 2026)
- All balances and payouts are simulated, with no cash value.
- 48 market titles are available. Only the safety contract has an empirically anchored opening price (5¢, based on 43 of 816 nflverse regular-season games in 2023–2025). The rate is unconditional and **not** a matchup forecast.
- Three penalty-related observations are **proxies**, not direct proof of the exact contract wording. The blocked-punt detector is **unvalidated** and its zero matches are **not** evidence that the event never occurred.
- Remaining market quotes are illustrative, not calibrated predictions.
- There is **no deployed dynamic market maker**. Quotes remain fixed until explicitly repriced; the trade RPC charges the database price at execution, under a row lock.

## Settlement (administrator action required)
Migration `evidence_based_demo_market_resolution_and_atomic_settlement` creates `public.market_resolutions` and `public.market_admins` and the authenticated RPC:
`resolve_demo_market(p_market_id bigint, p_winning_side text, p_evidence_url text, p_rationale text)`.

**No admin has been provisioned automatically.** An authorized project operator must separately grant a trusted existing auth user membership in `market_admins` through a secure admin workflow. Do not expose administrator enrollment to public clients.

Before resolving:
1. Specify the relevant **game, time window, and objective outcome**. Current broad titles lack game identifiers and expiry times, so many cannot be fairly resolved yet.
2. Require official NFL gamebooks/play-by-play for recorded football events; use primary video/broadcast evidence for camera-dependent incidents. Verify exact contract wording. If evidence is ambiguous, do not resolve.
3. Confirm the evidence URL and rationale; call the admin RPC once. It locks and closes the market, records an audit entry, pays winning single-leg demo contracts at 100¢ each, and settles affected parlays once won or irretrievably lost.
4. Check trade, slip, wallet, and resolution records in a **test project** before production use.

## Validation and test plan
- No user can call the resolution RPC without a matching admin membership.
- Cannot resolve a closed market or submit an invalid side / missing evidence.
- Two concurrent resolution attempts cannot pay twice.
- Winning YES/NO trades pay 100¢ per contract, losing trades 0.
- A multi-leg slip settles to 0 on any losing leg; it remains pending while all resolved legs win and other legs are unresolved; it pays the stored hypothetical payout only after every leg wins.
- Trades on a closed market are rejected by the trade RPC.
- Bonus credits and cash are debited correctly; settlement winnings are added to demo cash.
- Validate row-level security against users reading or modifying other users' wallets, trades, and slips.
- Test edge cases, high-volume concurrency, payout arithmetic, and rounding.

## Market maker requirements (not yet implemented)
Build and backtest an inventory-based bounded price model separately before exposing it to trades. The price needs a documented liquidity parameter, 1–99¢ bounds, deterministic sequential fills, bid/ask spread or fee assumptions, risk limits, and a clear distinction between **crowd-implied price** and **statistical evidence**. Market prices must not be presented as true event probabilities without calibration tests. Historical trade records must preserve execution price.

## Research priorities
1. Validate the safety and blocked-punt detectors against official NFL gamebooks and spot-checked play descriptions.
2. Define penalty contract semantics precisely: accepted penalties, multi-penalty plays, offsetting/declined flags, and yardage attribution.
3. For observable but non-play-by-play events (headset breaks, mascot/fan incidents, celebrations, signage), build a **complete sampled-game video/broadcast corpus with known coverage** before calculating frequencies. News clips establish that an event happened but not how often it *doesn't* happen.
4. Record every source, timestamp, game ID, event definition, observation window, numerator, denominator, exclusions, uncertainty interval, and human review status.
5. Reconcile duplicates and overlapping market wording; add specific game IDs and closing times before enabling live resolution.
