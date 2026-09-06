import datetime
from pathlib import Path
from insights.pipeline import SurveyDataPipeline, CleanedResponse
from insights.metrics import NPSMetrics
from insights.analyzer import ThemeAnalyzer

def test_nps_math_strict_in_code():
    responses = [
        CleanedResponse("1", datetime.datetime.now(), "NPS", 10, "Great", "Enterprise", "en", "email"),
        CleanedResponse("2", datetime.datetime.now(), "NPS", 9, "Love it", "Growth", "en", "email"),
        CleanedResponse("3", datetime.datetime.now(), "NPS", 8, "Good", "Starter", "en", "link"),
        CleanedResponse("4", datetime.datetime.now(), "NPS", 7, "Okay", "Starter", "en", "link"),
        CleanedResponse("5", datetime.datetime.now(), "NPS", 4, "Too slow", "Scale", "en", "sdk"),
    ]
    metrics = NPSMetrics.calculate_nps(responses)
    # Total = 5, Promoters = 2 (40%), Passives = 2 (40%), Detractors = 1 (20%)
    # NPS = 40.0 - 20.0 = +20.0
    assert metrics["total"] == 5
    assert metrics["promoters"] == 2
    assert metrics["passives"] == 2
    assert metrics["detractors"] == 1
    assert metrics["promoter_pct"] == 40.0
    assert metrics["detractor_pct"] == 20.0
    assert metrics["nps"] == 20.0

def test_pipeline_no_crash_on_any_row():
    csv_file = Path(__file__).resolve().parent.parent / "task3_data" / "responses_sample.csv"
    assert csv_file.exists()
    parsed = SurveyDataPipeline.parse_csv(csv_file, datetime.date(2026, 8, 17))
    assert parsed["total_rows_read"] > 350
    assert len(parsed["current_week_responses"]) > 0

def test_data_quality_reconciliation():
    csv_file = Path(__file__).resolve().parent.parent / "task3_data" / "responses_sample.csv"
    parsed = SurveyDataPipeline.parse_csv(csv_file, datetime.date(2026, 8, 17))
    total_read = parsed["total_rows_read"]
    used = len(parsed["current_week_responses"]) + len(parsed["prev_week_responses"])
    excluded = sum(parsed["excluded_reasons"].values())
    assert total_read == used + excluded

def test_spam_detection():
    assert SurveyDataPipeline.is_spam("Visit best-seo-tools.example for cheap backlinks") is True
    assert SurveyDataPipeline.is_spam("Get 500 free backlinks at best-seo-tools.example") is True
    assert SurveyDataPipeline.is_spam("Integrations just work. Zapier plus Slack covers everything.") is False

def test_score_parsing():
    assert SurveyDataPipeline.clean_score("10") == 10
    assert SurveyDataPipeline.clean_score("10/10") == 10
    assert SurveyDataPipeline.clean_score("ten") == 10
    assert SurveyDataPipeline.clean_score("8 out of 10") == 8
    assert SurveyDataPipeline.clean_score("eight") == 8
    assert SurveyDataPipeline.clean_score("9 ") == 9
    assert SurveyDataPipeline.clean_score("7.5") == 8
    assert SurveyDataPipeline.clean_score("-1") is None
    assert SurveyDataPipeline.clean_score("N/A") is None
    assert SurveyDataPipeline.clean_score("") is None
