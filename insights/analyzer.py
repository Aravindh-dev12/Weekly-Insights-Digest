import re
from typing import List, Dict, Any, Tuple
from insights.pipeline import CleanedResponse

class ThemeAnalyzer:
    THEME_DEFINITIONS = [
        {
            "name": "Dashboard & Rendering Latency",
            "keywords": ["dashboard", "render", "loading", "seconds to load", "slowness", "slow", "optimise"],
            "description": "Complaints regarding dashboard loading times and rendering lag at high data volumes."
        },
        {
            "name": "Integrations & Automation (Slack / Zapier)",
            "keywords": ["slack", "zapier", "integraci", "webhook", "integration", "alert"],
            "description": "Positive feedback and inquiries regarding Slack, Zapier, and webhook connectivity."
        },
        {
            "name": "Support Responsiveness & SLA",
            "keywords": ["support", "reply", "ticket", "responded", "waiting for support", "days to get a reply"],
            "description": "Customer feedback regarding support response delays and ticket resolution."
        },
        {
            "name": "CSV & Data Export Discrepancies",
            "keywords": ["export", "csv", "missing", "reconcile", "timezone", "download"],
            "description": "Issues with exported survey data, timezone reconciliation, or missing daily records."
        },
        {
            "name": "Pricing & Renewal Adjustments",
            "keywords": ["price", "renewal", "cost", "charged", "pricing", "value"],
            "description": "Feedback regarding 2026 pricing updates and renewal costs."
        },
        {
            "name": "Mobile Application Requests",
            "keywords": ["mobile app", "mobile", "app for alerts", "ios", "android"],
            "description": "Requests for dedicated native mobile apps for monitoring pulses."
        }
    ]

    WATCHOUT_PATTERNS = [
        (r"charged twice", "CRITICAL BILLING: Customer reports double billing charges."),
        (r"missing the most recent day", "DATA QUALITY: Daily survey CSV export is dropping latest day data."),
        (r"20\+\s*seconds", "PERFORMANCE: Severe dashboard degradation reported (> 20s latency)."),
        (r"three days to get a reply", "SUPPORT SLA: Multi-day support delay reported by paying account."),
        (r"\+?\d[\d\s\-]{8,}\d", "URGENT OUTREACH: Customer provided direct phone number requesting call.")
    ]

    @classmethod
    def extract_themes(cls, responses: List[CleanedResponse], top_n: int = 5) -> List[Dict[str, Any]]:
        categorized: Dict[str, List[CleanedResponse]] = {t["name"]: [] for t in cls.THEME_DEFINITIONS}
        uncategorized: List[CleanedResponse] = []

        for r in responses:
            comment = r.comment.strip()
            if not comment or comment in ["-", "No comment", "None", "n/a"]:
                continue

            c_lower = comment.lower()
            matched = False
            for t in cls.THEME_DEFINITIONS:
                if any(kw in c_lower for kw in t["keywords"]):
                    categorized[t["name"]].append(r)
                    matched = True
                    break
            if not matched:
                uncategorized.append(r)

        # Sort themes by volume
        sorted_themes = sorted(
            [{"name": k, "responses": v, "count": len(v)} for k, v in categorized.items() if len(v) > 0],
            key=lambda x: x["count"],
            reverse=True
        )[:top_n]

        results = []
        for item in sorted_themes:
            resps = item["responses"]
            # Pick 1 or 2 distinct representative comments
            unique_comments = []
            seen = set()
            for r in resps:
                c = r.comment.strip()
                if c not in seen:
                    seen.add(c)
                    unique_comments.append(f'"{c}" (Score: {r.score}, {r.segment} segment)')
                if len(unique_comments) >= 2:
                    break

            results.append({
                "theme": item["name"],
                "count": item["count"],
                "representative_comments": unique_comments
            })

        return results

    @classmethod
    def extract_watchouts(cls, responses: List[CleanedResponse]) -> List[str]:
        watchouts = []
        seen_alerts = set()

        for r in responses:
            comment = r.comment.strip()
            for pat, alert_desc in cls.WATCHOUT_PATTERNS:
                if re.search(pat, comment, re.IGNORECASE):
                    key = alert_desc.split(":")[0]
                    if key not in seen_alerts:
                        seen_alerts.add(key)
                        watchouts.append(f"**{alert_desc}**\n  - Quote: *\"{comment}\"* (Respondent {r.response_id}, {r.segment})")

        if not watchouts:
            watchouts.append("No critical anomaly alerts flagged in customer feedback this week.")

        return watchouts
