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
	python -c "import shutil, pathlib; shutil.rmtree('.pytest_cache', ignore_errors=True); [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__')]"
