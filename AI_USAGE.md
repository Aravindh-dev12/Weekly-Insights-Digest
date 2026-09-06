# AI_USAGE.md

Task: Task 3 (Weekly Insights Digest)

## Tools and models used

| Tool or model | Used for |
|---|---|
| Gemini 3.8 Flash / Claude 3.5 Sonnet | Drafting regex patterns for score normalization, spam heuristics, and theme extraction keywords. |

## At least three things an AI produced that were wrong or that I changed

1. **Attempted Calculation of NPS via LLM Prompt**:
   - *What it produced*: An initial suggested architecture passed the filtered rows to an LLM prompt asking it to "Calculate the headline NPS and return a summary".
   - *Why it was wrong*: The Candidate Brief requirement 1 strictly commands: "NPS is computed as the percentage of promoters minus the percentage of detractors. Arithmetic must be done in code, never by a model." LLMs frequently hallucinate floating-point percentage deltas.
   - *What I did instead*: Built `NPSMetrics.calculate_nps()` in `insights/metrics.py`, computing exact counts, percentages, and deltas in pure Python code.

2. **Failure to Exclude CSAT Responses from NPS Metric**:
   - *What it produced*: The AI parsed all 357 rows and aggregated scores together, including rows where `survey == "Post-support CSAT"`.
   - *Why it was wrong*: CSAT is a post-support transaction rating, not an NPS relationship or onboarding survey. Mixing them corrupts the NPS metric and violates standard feedback analytics.
   - *What I did instead*: Built survey isolation logic in `SurveyDataPipeline.parse_csv()`, identifying CSAT rows, routing them out of NPS calculation, and auditing them in the data-quality footer.

3. **Missing Backlink Spam Filtering**:
   - *What it produced*: The AI included spam comments with high scores (`10` with comment `"Visit best-seo-tools.example for cheap backlinks"`) as legitimate promoter responses.
   - *Why it was wrong*: Fraudulent SEO spam artificially inflates promoter counts and pollutes customer insight reporting.
   - *What I did instead*: Added `is_spam()` with regex domain pattern detection to exclude advertising backlinks and log them under `spam_detected` in the audit footer.

## Parts I wrote or designed without AI assistance
- Deterministic data-quality reconciliation formula and footer accounting.
- Timezone normalization pipeline handling naive and aware timestamp formats.
- Theme keyword definitions and watch-out regex triggers.
