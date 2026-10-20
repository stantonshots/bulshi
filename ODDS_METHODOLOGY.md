# BULSHI odds evidence — methodology and limitations

This repository includes a reproducible NFL regular-season event-frequency pipeline in `scripts/build_odds_evidence.py`. It downloads nflverse play-by-play parquet files for 2023, 2024, and 2025 and writes `odds-evidence.json` when the workflow succeeds.

## What this measures
For each coded market: number of distinct games with at least one matching event / number of regular-season games examined. A Wilson 95% interval accompanies the observed rate. The resulting number is an **unconditional historical frequency**, not a team-specific or matchup-specific prediction and not an exchange quote. NFL game data attribution: nflverse, CC BY 4.0.

## Evidence classification
- **Measured historical rate:** a game-level event with a clear, reproducible detection rule and sufficiently complete structured data.
- **Proxy:** structured data is relevant but the market's exact language cannot be established by that data (for example, timing of a taunting flag, penalty counting conventions).
- **Unverified:** the event has no validated denominator and cannot honestly be assigned a statistically established probability.

Videos, social posts and news articles can prove an event occurred, but cannot establish its frequency unless a complete or systematically sampled set of games is reviewed, including games with no event. For events such as headset destruction, mascot incidents, choreographed celebrations, and unusual fan behavior, no validated game-level annotation dataset has been assembled. Those markets remain **unverified**.

## Operational constraints
The GitHub Actions workflow requires repository Actions to be enabled, outbound download access to nflverse, and permission to write repository contents. The pipeline has not been confirmed to complete successfully. It intentionally does not overwrite Supabase contract prices. The current contract prices remain illustrative, not statistically calibrated. Historical evidence is displayed separately once the JSON is generated.

Before production use: audit column availability, test each rule against game film and official play reports, check sampling and selection bias, document market time windows and resolution rules, and calibrate model forecasts out-of-sample. Do not represent these odds as guaranteed correct.
