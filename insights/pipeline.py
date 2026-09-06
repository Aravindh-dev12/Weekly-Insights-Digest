import csv
import re
import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from dateutil import parser

class CleanedResponse:
    def __init__(
        self,
        response_id: str,
        submitted_at: datetime.datetime,
        survey: str,
        score: int,
        comment: str,
        segment: str,
        language: str,
        channel: str,
        is_spam: bool = False
    ):
        self.response_id = response_id
        self.submitted_at = submitted_at
        self.survey = survey
        self.score = score
        self.comment = comment
        self.segment = segment
        self.language = language
        self.channel = channel
        self.is_spam = is_spam

class SurveyDataPipeline:
    WORD_TO_NUM = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
    }

    SPAM_PATTERNS = [
        r"best-seo-tools\.example",
        r"backlink",
        r"cheap backlinks",
        r"free backlinks"
    ]

    @classmethod
    def clean_score(cls, raw: str) -> Optional[int]:
        if not raw:
            return None
        cleaned = raw.strip().lower()
        if cleaned in cls.WORD_TO_NUM:
            return cls.WORD_TO_NUM[cleaned]
        # Match pattern like "10/10" or "8 out of 10"
        m = re.match(r"^(\d+)(?:\s*(?:/|out of)\s*10)?$", cleaned)
        if m:
            val = int(m.group(1))
            if 0 <= val <= 10:
                return val
            return None
        # Float like 7.5
        try:
            f = float(cleaned)
            val = int(round(f))
            if 0 <= val <= 10:
                return val
        except ValueError:
            pass
        return None

    @classmethod
    def is_spam(cls, comment: str) -> bool:
        if not comment:
            return False
        for pat in cls.SPAM_PATTERNS:
            if re.search(pat, comment, re.IGNORECASE):
                return True
        return False

    @classmethod
    def parse_csv(
        cls,
        csv_path: Path,
        target_week_start: datetime.date
    ) -> Dict[str, Any]:
        """
        Parses survey CSV, filtering for target week and previous week.
        Categorizes used and excluded rows with explicit accounting.
        """
        target_monday = target_week_start
        target_sunday = target_monday + datetime.timedelta(days=6)
        prev_monday = target_monday - datetime.timedelta(days=7)
        prev_sunday = target_monday - datetime.timedelta(days=1)

        total_rows_read = 0
        current_week_nps: List[CleanedResponse] = []
        prev_week_nps: List[CleanedResponse] = []
        
        excluded_reasons: Dict[str, int] = {
            "non_nps_survey (CSAT)": 0,
            "spam_detected": 0,
            "invalid_or_missing_score": 0,
            "outside_target_and_prev_week": 0
        }

        with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                total_rows_read += 1
                survey = row.get("survey", "").strip()
                raw_score = row.get("score", "").strip()
                comment = row.get("comment", "").strip()
                submitted_raw = row.get("submitted_at", "").strip()

                # Parse date safely
                try:
                    dt = parser.parse(submitted_raw)
                    if dt.tzinfo is not None:
                        dt = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
                except Exception:
                    excluded_reasons["outside_target_and_prev_week"] += 1
                    continue

                row_date = dt.date()

                # 1. Non-NPS survey check
                if "CSAT" in survey.upper():
                    excluded_reasons["non_nps_survey (CSAT)"] += 1
                    continue

                # 2. Spam check
                if cls.is_spam(comment):
                    excluded_reasons["spam_detected"] += 1
                    continue

                # 3. Score validation
                score = cls.clean_score(raw_score)
                if score is None:
                    excluded_reasons["invalid_or_missing_score"] += 1
                    continue

                cleaned_obj = CleanedResponse(
                    response_id=row.get("response_id", f"r_{total_rows_read}"),
                    submitted_at=dt,
                    survey=survey,
                    score=score,
                    comment=comment,
                    segment=row.get("segment", "unknown").strip(),
                    language=row.get("language", "en").strip(),
                    channel=row.get("channel", "unknown").strip()
                )

                if target_monday <= row_date <= target_sunday:
                    current_week_nps.append(cleaned_obj)
                elif prev_monday <= row_date <= prev_sunday:
                    prev_week_nps.append(cleaned_obj)
                else:
                    excluded_reasons["outside_target_and_prev_week"] += 1

        return {
            "total_rows_read": total_rows_read,
            "current_week_responses": current_week_nps,
            "prev_week_responses": prev_week_nps,
            "excluded_reasons": excluded_reasons
        }
