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


def test_answer_shows_matched_quote_and_restricts_filing_links() -> None:
    app = AppTest.from_file(str(APP), default_timeout=35)
    app.session_state["last_result"] = {
        "compare": False,
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
