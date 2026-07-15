.PHONY: install test run eval-recall eval-llm eval-faithfulness clean

install:
	pip install -r requirements.txt

test:
	pytest tests.py -v

run:
	streamlit run app.py

eval-recall:
	python src/eval_recall.py

eval-llm:
	python src/eval_llm.py

eval-faithfulness:
	python src/eval_faithfulness.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
