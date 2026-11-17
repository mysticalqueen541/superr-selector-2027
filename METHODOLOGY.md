# SUPERR SELECTOR — Scoring Methodology
**Rajasthan Royals | IPL 2027 auction strategy | 17 November 2026**

This document describes the methodology implemented in `analytics.py` and `bowling_analytics.py`.

## Final score
**Final / 200 = 2 × (0.40 × Situation / 100 + 0.60 × Pressure / 100)**

**Pressure / 100 = 0.60 × Pressure-situation / 100 + 0.40 × Overall pressure reliability / 100.**

## Sources, filters and minimum samples
The six original competition CSVs supply ranking data. The reference Excel workbook is not a ranking data source. All covers IPL and selected T20 competitions; T20s covers T20I and two Asia Cup T20 competitions; IPL covers IPL competitions. Eligibility requires at least nine matches and the selected minimum pressure balls (default 100). Pressure-situation minimum defaults to 20 balls. Pakistan/Bangladesh and retirement-from-both-T20I-and-IPL exclusions are optional shortlist filters, applied after eligible-cohort scoring.

## Six baseline situations
**Batting:** powerplay (overs 1–6), middle (7–15), death (16–20), split into setting/chasing. Weights: setting 2, 1, 3; chasing 4, 2, 6. Strike-rate bands award up to 10 points per situation; weighted maximum 180, normalized to 100.

**Bowling:** the same three phases, split into bowling first/defending. Weights 2 for each bowling-first phase and 4 for each defending phase. Lower economy earns higher percentile points; minimum 12 balls for a baseline situation. Weighted maximum 180, normalized to 100.

## Pressure conditions
**Batting:** any of difficult chase (second innings from over 7, required run rate ≥ 9 and greater than current run rate), early collapse (at least three wickets already lost in first 10 overs), death overs (16–20), or knockout match. Overlapping flags count a delivery once overall.

**Bowling:** defending in the second innings when the chasing team's pre-ball CRR > RRR. This is distinct from the batting definition.

Pressure-situation points use the same six situations, but award zero below the selected per-situation pressure-ball threshold. Batting pressure-situation maximum is 180 weighted points; bowling defending-pressure maximum is 120; both are normalized to 100.

## Overall pressure reliability
**Batters:** 50% eligible-cohort percentile for pressure strike rate and 50% percentile for pressure strike-rate improvement over overall strike rate.

**Bowlers:** 50% percentile for lower pressure economy and 50% positive improvement credit relative to chase economy. Non-positive or unavailable economy improvement earns zero improvement credit.

Both use a pressure-ball confidence factor `pressure_balls / (pressure_balls + 60)`, shrinking small samples toward a neutral 50-point rating.

## Data safeguards and interpretation
Pre-ball state uses batter runs and numeric extras. Super Overs do not enter regular 20-over phase scores. Valid rain-shortened revised targets are retained; audited discrepancies, no-results, and weather chases without verified revised target/overs are excluded from reconstructed chase pressure. Scores rank statistical performance relative to the eligible cohort and do not replace scouting, role fit, availability or price evaluation.

**Professional PDF version:** `Superr_Selector_Methodology.pdf` (provided alongside this source document).
