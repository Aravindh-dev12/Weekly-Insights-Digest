import sys
import argparse
import datetime
from pathlib import Path
from dateutil import parser
from insights.pipeline import SurveyDataPipeline
from insights.metrics import NPSMetrics
from insights.analyzer import ThemeAnalyzer
from insights.formatter import DigestFormatter

def run_digest(input_csv: str, week_str: str, out_file: str):
    csv_path = Path(input_csv)
    if not csv_path.exists():
        print(f"Error: Input file {csv_path} does not exist.", file=sys.stderr)
        sys.exit(1)

    try:
        target_week_date = parser.parse(week_str).date()
        # Align to Monday of that week
        target_monday = target_week_date - datetime.timedelta(days=target_week_date.weekday())
    except Exception as e:
        print(f"Error parsing week date {week_str}: {e}", file=sys.stderr)
        sys.exit(1)

    # 1. Parse & Filter CSV
    parsed = SurveyDataPipeline.parse_csv(csv_path, target_monday)

    current_resps = parsed["current_week_responses"]
    prev_resps = parsed["prev_week_responses"]

    # 2. Compute Metrics
    current_metrics = NPSMetrics.calculate_nps(current_resps)
    prev_metrics = NPSMetrics.calculate_nps(prev_resps)
    comparison = NPSMetrics.compare_weeks(current_metrics, prev_metrics)

    # 3. Analyze Themes & Watch-outs
    themes = ThemeAnalyzer.extract_themes(current_resps, top_n=5)
    watchouts = ThemeAnalyzer.extract_watchouts(current_resps)

    # 4. Render Markdown Report
    report = DigestFormatter.render_markdown(
        week_str=str(target_monday),
        nps_comparison=comparison,
        current_nps_details=current_metrics,
        themes=themes,
        watchouts=watchouts,
        data_quality=parsed
    )

    out_path = Path(out_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Weekly Insights Digest successfully generated!")
    print(f"  Target Week: {target_monday}")
    print(f"  Current Week NPS: {comparison['current_nps']:+.1f} (from {comparison['current_total']} responses)")
    print(f"  Previous Week NPS: {comparison['previous_nps']:+.1f} (Delta {comparison['delta']:+0.1f} pts)")
    print(f"  Top Themes Extracted: {len(themes)}")
    print(f"  Output saved to: {out_path}")

def main():
    parser_cli = argparse.ArgumentParser(description="Ferrowave Weekly Insights Digest CLI")
    subparsers = parser_cli.add_subparsers(dest="subcommand")

    digest_parser = subparsers.add_parser("digest", help="Generate weekly NPS insights digest")
    digest_parser.add_argument("--input", type=str, required=True, help="Path to survey responses CSV")
    digest_parser.add_argument("--week", type=str, required=True, help="Target week (YYYY-MM-DD)")
    digest_parser.add_argument("--out", type=str, default="digest.md", help="Output file path")

    # Also support direct flags on root: python digest.py --input ... --week ... --out ...
    parser_cli.add_argument("--input", type=str, help="Path to survey responses CSV")
    parser_cli.add_argument("--week", type=str, help="Target week (YYYY-MM-DD)")
    parser_cli.add_argument("--out", type=str, default="digest.md", help="Output file path")

    args = parser_cli.parse_args()

    input_file = args.input
    week = args.week
    out = args.out

    if not input_file or not week:
        parser_cli.print_help()
        sys.exit(1)

    run_digest(input_file, week, out)

if __name__ == "__main__":
    main()
