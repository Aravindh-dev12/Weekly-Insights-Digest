# DECISIONS.md

Task: Task 3 (Weekly Insights Digest, Part A)
Author: Engineering Candidate
Last updated: 2026-09-06

## How to use this file

One entry per significant decision. Keep entries short and specific.

## Stack

| Decision | Options considered | Chosen | Why | What would make me reverse it | Cost (time, money, complexity) |
|---|---|---|---|---|---|
| Language and runtime | Python 3.12 vs TypeScript | Python 3.12 | Rich data manipulation (`datetime`, `dateutil`, regex), standard library `csv`, and fast CLI ergonomics. | Strict corporate requirement for Node.js. | Zero cost. |
| Framework | Pandas vs Standard Library + Dateutil | Pure Python Standard Library + `python-dateutil` | Dataset is ~360 rows. Pandas adds a ~60MB dependency and binary wheel overhead for operations easily done in 100 lines of standard library. | If dataset scaled to 10M+ rows requiring vectorization. | Zero third-party baggage; sub-second runtime. |
| Theme Clustering | Unconstrained LLM API call vs Lexical Keyword/Pattern Clustering | Deterministic Rule/Keyword Clustering + Regex Alerts | Brief specifies: "Total model spend under USD 1 for the sample file; tool must not crash on any row." Deterministic clustering costs $0.00, runs in < 0.1s offline, and yields consistent categorization across repeated runs. | If customer comments were radically unstructured across 50+ diverse topics. | $0.00 spend. |

## Design decisions

| Decision | Options considered | Chosen | Why | What would make me reverse it | Cost |
|---|---|---|---|---|---|
| Arithmetic Enforcement | LLM math vs Code calculation | Deterministic Python calculation | Brief strictly dictates: "Arithmetic must be done in code, never by a model." Guaranteed 100% precision. | None; mathematical determinism is mandatory. | Instant execution (< 1ms). |
| Survey Type Isolation | Mix CSAT and NPS vs Exclude CSAT | Exclude `Post-support CSAT` from NPS calculation | CSAT and NPS measure fundamentally different concepts. Mixing CSAT scores into NPS corrupts metric integrity. | If product explicitly wanted a blended customer sentiment index. | Transparently audited in footer. |
| Inconsistent Timezones | Fail on naive vs Normalize all to UTC | Parse with dateutil and normalize to UTC naive date | Some records have ISO 8601 UTC stamps (`2026-08-14T05:58:01Z`) while others have US local formats (`08/11/2026 12:25`). Normalizing prevents comparison crashes. | Explicit per-customer timezone preferences. | Handled in pipeline ingestion. |

## Spend

| Item | Measured or estimated | Amount (USD) | Evidence |
|---|---|---|---|
| Development spend | Measured | $0.00 | Local execution and testing. |
| Per digest run | Measured | $0.00 | Pure-Python deterministic processing. |

## Known gaps

1. Advanced Multilingual NLP: Spanish comments (`Die Slack-Integration`, `La integración`) are categorized via shared root keywords (`integraci`), but an integrated translation step would enable cross-language embedding clustering.
2. Custom Week Boundary Configuration: Currently expects Monday-to-Sunday ISO weeks.
