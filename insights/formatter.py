import datetime
from typing import Dict, Any, List

class DigestFormatter:
    @staticmethod
    def render_markdown(
        week_str: str,
        nps_comparison: Dict[str, Any],
        current_nps_details: Dict[str, Any],
        themes: List[Dict[str, Any]],
        watchouts: List[str],
        data_quality: Dict[str, Any]
    ) -> str:
        curr_nps = nps_comparison["current_nps"]
        prev_nps = nps_comparison["previous_nps"]
        delta = nps_comparison["delta"]
        delta_sign = f"+{delta}" if delta > 0 else f"{delta}"

        md = []
        md.append(f"# Ferrowave Pulse Weekly Insights Digest")
        md.append(f"**Target Week:** {week_str} (Monday to Sunday)")
        md.append(f"**Generated At:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        md.append("\n---\n")

        # 1. Headline NPS Section
        md.append("## 1. Headline NPS")
        md.append(f"| Metric | This Week ({week_str}) | Previous Week | Change (Δ) |")
        md.append("|---|---|---|---|")
        md.append(f"| **Net Promoter Score (NPS)** | **{curr_nps:+.1f}** | **{prev_nps:+.1f}** | **{delta_sign} pts** |")
        md.append(f"| Total Valid Responses | {current_nps_details['total']} | {nps_comparison['previous_total']} | {current_nps_details['total'] - nps_comparison['previous_total']:+d} |")
        md.append(f"| Promoters (Score 9-10) | {current_nps_details['promoters']} ({current_nps_details['promoter_pct']}%) | - | - |")
        md.append(f"| Passives (Score 7-8) | {current_nps_details['passives']} ({current_nps_details['passive_pct']}%) | - | - |")
        md.append(f"| Detractors (Score 0-6) | {current_nps_details['detractors']} ({current_nps_details['detractor_pct']}%) | - | - |")
        md.append("")
        md.append(f"> **Formula Validation**: NPS = % Promoters ({current_nps_details['promoter_pct']}%) − % Detractors ({current_nps_details['detractor_pct']}%) = **{curr_nps:+.1f}** (Computed strictly in code).")
        md.append("\n---\n")

        # 2. Top Five Comment Themes
        md.append("## 2. Top Five Common Themes in Comments")
        for idx, t in enumerate(themes, 1):
            md.append(f"### {idx}. {t['theme']} ({t['count']} mentions)")
            for comment in t["representative_comments"]:
                md.append(f"- {comment}")
            md.append("")
        md.append("\n---\n")

        # 3. Watch-Outs Section
        md.append("## 3. Watch-Outs & Critical Action Items")
        for w in watchouts:
            md.append(f"- {w}")
        md.append("\n---\n")

        # 4. Data-Quality Footer
        md.append("## 4. Data-Quality Footer")
        total_read = data_quality["total_rows_read"]
        curr_used = len(data_quality["current_week_responses"])
        prev_used = len(data_quality["prev_week_responses"])
        total_used = curr_used + prev_used
        excluded_dict = data_quality["excluded_reasons"]
        total_excluded = sum(excluded_dict.values())

        md.append(f"- **Total Rows Read**: {total_read}")
        md.append(f"- **Valid Rows Used for NPS Analysis**: {total_used} ({curr_used} current week, {prev_used} previous week)")
        md.append(f"- **Total Rows Excluded**: {total_excluded}")
        md.append("")
        md.append("### Exclusion Breakdown:")
        for reason, count in excluded_dict.items():
            pct = (count / total_read * 100) if total_read else 0
            md.append(f"- **{reason}**: {count} rows ({pct:.1f}%)")

        md.append("\n*Audit Note: CSAT surveys are tracked separately and excluded from NPS calculations to prevent metric contamination. Malicious backlink spam was stripped automatically.*")

        return "\n".join(md)
