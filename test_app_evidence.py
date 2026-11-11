from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).with_name("app.py")


def test_analytics_does_not_present_historical_scores_as_current() -> None:
    app = AppTest.from_file(str(APP), default_timeout=35).run()
    app.sidebar.radio[0].set_value("System Analytics").run()

    assert not app.exception
    text = "\n".join(item.value for item in app.markdown)
    assert "74.2%" not in text
    assert "69.7%" not in text
    assert "Answer quality has not been independently verified" in "\n".join(item.value for item in app.info)


def test_research_question_is_free_form_without_presets() -> None:
    app = AppTest.from_file(str(APP), default_timeout=35).run()

    assert not app.exception
    assert len(app.text_area) == 1
    assert app.text_area[0].label == "Research question"
    assert not any(button.label in {"Revenue", "Costs", "Margins"} for button in app.button)


def test_research_question_accepts_cross_company_prompt_without_truncation() -> None:
    from src.rag import sanitize_input

    question = ("Compare how Chipotle's labor costs changed for the three months ended June 30, 2024 "
                "and how Johnson & Johnson's Europe sales grew for the quarter ended March 29, 2026, "
                "respectively. Report each company's metric separately; do not treat them as the same metric or period.")
    app = AppTest.from_file(str(APP), default_timeout=35).run()

    assert len(question) > 256
    assert app.text_area[0].proto.max_chars >= len(question)
    assert sanitize_input(question) == question
    app.text_area[0].set_value(question).run()
    assert not app.exception
    assert app.text_area[0].value == question


def test_answer_shows_matched_quote_and_restricts_filing_links() -> None:
    app = AppTest.from_file(str(APP), default_timeout=35)
    app.session_state["last_result"] = {
        "compare": False,
        "question": "What changed in revenue?",
        "answer": "Revenue rose with pricing.",
        "structured": True,
        "claims": [{"statement": "Revenue rose.", "source_chunk_index": 0, "source_quote": "Pricing contributed to revenue."}],
        "sources": [{
            "text": "Pricing contributed to revenue. " + "Full passage " * 60,
            "metadata": {
                "ticker": "CMG", "form": "10-Q", "filing_date": "2026-10-29",
                "filing_url": "https://www.sec.gov/Archives/edgar/data/1058090/123/report.htm",
            },
        }],
    }
    app.run()

    assert not app.exception
    markup = "\n".join(item.value for item in app.markdown)
    assert "Quote matched in retrieved text" in markup
    assert "Question analyzed: What changed in revenue?" in "\n".join(item.value for item in app.get("caption"))
    assert "Open SEC filing" in markup
    assert "Full passage " * 60 in markup
    assert any("Pricing contributed to revenue." in item.value for item in app.text)

    app.session_state["last_result"]["sources"][0]["metadata"]["filing_url"] = 'https://evil.example/Archives/edgar/data/1/x'
    app.run()
    markup = "\n".join(item.value for item in app.markdown)
    assert "Open SEC filing" not in markup
    assert "link unavailable" in markup

    app.session_state["last_result"]["sources"][0]["metadata"]["filing_url"] = "https://[bad-host/Archives/edgar/data/1"
    app.run()
    assert not app.exception


def test_unverified_answer_is_not_labeled_sourced() -> None:
    app = AppTest.from_file(str(APP), default_timeout=35)
    app.session_state["last_result"] = {
        "compare": False,
        "answer": "I cannot verify this claim.",
        "structured": True,
        "claims": [],
        "sources": [],
    }
    app.run()

    assert not app.exception
    markup = "\n".join(item.value for item in app.markdown)
    assert "No checked quote" in markup
    assert ">sourced<" not in markup
    assert "No verified finding" in "\n".join(item.value for item in app.subheader)


def test_failed_quote_validation_hides_generated_financial_claim() -> None:
    app = AppTest.from_file(str(APP), default_timeout=35)
    app.session_state["last_result"] = {
        "compare": False,
        "answer": "Revenue grew 25% due to price increases.",
        "structured": True,
        "claims": [{"source_chunk_index": 0, "source_quote": "not in passage"}],
        "verification_errors": ["Quote not found"],
        "sources": [],
    }
    app.run()

    assert not app.exception
    text = "\n".join(item.value for item in app.markdown)
    assert "Revenue grew 25%" not in text
    assert "I cannot verify the generated claims" in text
    assert "Quote matched in retrieved text" not in text
    assert "Validation: Quote not found" in "\n".join(item.value for item in app.text)


def test_output_limit_displays_actionable_notice() -> None:
    app = AppTest.from_file(str(APP), default_timeout=35)
    app.session_state["last_result"] = {
        "compare": False,
        "answer": "The model reached its 2048-token output limit before completing a verified answer.",
        "structured_fallback": True,
        "structured_failure_reason": "output_limit",
        "claims": [],
        "sources": [],
    }
    app.run()

    assert not app.exception
    text = "\n".join(item.value for item in app.markdown)
    assert "2048-token output limit" in text
    assert "Quote matched in retrieved text" not in text
    assert "answer-token limit" in "\n".join(item.value for item in app.warning)
