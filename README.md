# Ferrowave Weekly Insights Digest (Task 3)

A command-line tool that reads raw, messy survey exports and generates a structured weekly NPS digest containing headline NPS metrics, comment themes, critical watch-outs, and a data-quality audit footer.

---

## 1. Quick Start

### Run CLI
```bash
python digest.py --input task3_data/responses_sample.csv --week 2026-08-17 --out outputs/digest_2026-08-17.md
```

### Options:
- `--input <path>`: Path to survey responses CSV (e.g. `task3_data/responses_sample.csv`).
- `--week <YYYY-MM-DD>`: Target week date (Monday to Sunday, e.g. `2026-08-17`).
- `--out <path>`: Output markdown or HTML file (default: `digest.md`).

---

## 2. Methodology & Guarantees

1. **Arithmetic Strictly in Code**:
   $$\text{Promoter \%} = \left(\frac{\text{Count}(\text{Score} \in \{9, 10\})}{N}\right) \times 100$$
   $$\text{Detractor \%} = \left(\frac{\text{Count}(\text{Score} \in \{0, \dots, 6\})}{N}\right) \times 100$$
   $$\text{Net Promoter Score} = \text{Promoter \%} - \text{Detractor \%}$$
   Arithmetic is computed deterministically in code with zero LLM approximation.

2. **Data Cleaning & Sanity Filters**:
   - **Timestamp Normalization**: Handles both ISO 8601 with timezone (`2026-08-14T05:58:01Z`) and naive US formats (`08/11/2026 12:25`), converting to uniform UTC dates.
   - **Score Sanitization**: Parses textual numbers (`ten`, `eight`), fraction formats (`10/10`, `8 out of 10`), trailing spaces (`9 `), and floats (`7.5`). Rejects out-of-range (`-1`) or missing (`N/A`) values.
   - **Spam Rejection**: Automatically detects and excludes advertising backlink spam (`best-seo-tools.example`).
   - **Survey Segmentation**: Isolates `Post-support CSAT` from NPS calculations to prevent metric cross-contamination.

3. **Data-Quality Accounting**:
   The digest footer accounts for 100% of rows read:
   $$\text{Total Read} = \text{Used} + \sum \text{Excluded Reasons}$$

---

## 3. Running Tests

```bash
pytest tests/
```
Validates:
- NPS calculation formula
- Zero crashes on messy CSV rows
- Full mathematical data-quality accounting
- Spam link detection
- Robust score parsing
