# ITERATIONS.md

Task: Task 3 (Weekly Insights Digest)

## Entries

### 2026-09-06 Iteration 1: Offset-Naive vs Offset-Aware Datetime Comparison
- **Built or changed**: Initial date comparison between `parser.parse(row["submitted_at"])` and target week boundaries.
- **Observed (evidence)**: Python threw `TypeError: can not compare offset-naive and offset-aware datetimes` on row 8 (`08/11/2026 12:25`), which lacked a UTC `Z` specifier unlike the surrounding ISO rows.
- **Concluded**: CSV survey exports in the wild mix multiple client date formats and timezone assumptions.
- **Next**: Added timezone normalization in `SurveyDataPipeline.parse_csv()`: converts aware datetimes to UTC and strips tzinfo to ensure homogeneous date-level comparisons across all 357 rows.

### 2026-09-06 Iteration 2: Python Script / Package Name Shadowing
- **Built or changed**: Created `digest.py` importing from internal module `digest.pipeline`.
- **Observed (evidence)**: `ModuleNotFoundError: No module named 'digest.pipeline'; 'digest' is not a package`.
- **Concluded**: Having both a script named `digest.py` and a folder named `digest/` caused Python module resolution to shadow the folder with the file.
- **Next**: Renamed the internal package folder to `insights/` and added explicit package `__init__.py` markers. CLI execution completed without import collision.

### 2026-09-06 Iteration 3: Terminal Code Page Encoding Failure on Delta Symbol
- **Built or changed**: Terminal summary printed `\u0394` (Δ).
- **Observed (evidence)**: `UnicodeEncodeError: 'charmap' codec can't encode character '\u0394'` on Windows console cp1252.
- **Concluded**: CLI console logging must avoid raw Greek symbols that trip legacy Windows code pages.
- **Next**: Replaced terminal print string with `Delta`, preserving Unicode delta formatting within the output markdown file.

---

## Part B (Task 3 only)

*(Reserved for Part B requirements change after v1 review).*
