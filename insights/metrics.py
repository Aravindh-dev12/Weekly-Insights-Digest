from typing import List, Dict, Any, Optional
from insights.pipeline import CleanedResponse

class NPSMetrics:
    @staticmethod
    def calculate_nps(responses: List[CleanedResponse]) -> Dict[str, Any]:
        """
        Calculates NPS strictly in code:
        Promoters: 9-10
        Passives: 7-8
        Detractors: 0-6
        NPS = (% Promoters) - (% Detractors)
        """
        total = len(responses)
        if total == 0:
            return {
                "total": 0,
                "promoters": 0,
                "passives": 0,
                "detractors": 0,
                "promoter_pct": 0.0,
                "passive_pct": 0.0,
                "detractor_pct": 0.0,
                "nps": 0.0
            }

        promoters = sum(1 for r in responses if r.score in [9, 10])
        passives = sum(1 for r in responses if r.score in [7, 8])
        detractors = sum(1 for r in responses if 0 <= r.score <= 6)

        promoter_pct = (promoters / total) * 100.0
        passive_pct = (passives / total) * 100.0
        detractor_pct = (detractors / total) * 100.0
        nps = round(promoter_pct - detractor_pct, 1)

        return {
            "total": total,
            "promoters": promoters,
            "passives": passives,
            "detractors": detractors,
            "promoter_pct": round(promoter_pct, 1),
            "passive_pct": round(passive_pct, 1),
            "detractor_pct": round(detractor_pct, 1),
            "nps": nps
        }

    @staticmethod
    def compare_weeks(current_nps_data: Dict[str, Any], prev_nps_data: Dict[str, Any]) -> Dict[str, Any]:
        curr = current_nps_data["nps"]
        prev = prev_nps_data["nps"]
        delta = round(curr - prev, 1)
        direction = "up" if delta > 0 else ("down" if delta < 0 else "unchanged")
        return {
            "current_nps": curr,
            "previous_nps": prev,
            "delta": delta,
            "direction": direction,
            "current_total": current_nps_data["total"],
            "previous_total": prev_nps_data["total"]
        }
