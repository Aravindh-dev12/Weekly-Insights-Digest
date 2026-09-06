# DEPENDENCIES.md

Task: Task 3 (Weekly Insights Digest)

Every third-party package added beyond Python standard library:

| Package | Version | What it does for me here | What I would have to write if it were removed | Risk (size, maintenance, licence, lock-in) |
|---|---|---|---|---|
| `python-dateutil` | 2.9.0 | Flexible timestamp parsing for mixed ISO and US datetime strings. | A custom regex pattern parser testing multiple `datetime.strptime` formats. | Very low risk; Apache 2.0 / Dual BSD. |
| `click` | 8.5.0 | Command-line option parsing. | Standard library `argparse` (which is also supported as native fallback). | Low risk; BSD license. |
| `pytest` | 9.1.1 | Unit test execution. | Standard library `unittest`. | Development dependency only. |
