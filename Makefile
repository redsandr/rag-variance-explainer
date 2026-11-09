.PHONY: install test lint typecheck run eval-recall eval-llm eval-faithfulness clean

install:
	python -m pip install -e ".[dev]"

test:
	pytest tests.py -v

lint:
	ruff check src/ app.py conftest.py tests.py

typecheck:
	mypy src/ conftest.py

check: test lint typecheck

run:
	streamlit run app.py

mcp:
	python src/server.py

mcp-sse:
	python src/server.py --sse --port 8765

api:
	uvicorn src.api:app --reload --port 8000

eval-recall:
	python src/eval_recall.py

eval-ablation:
	python src/eval_ablation.py

benchmark:
	python src/benchmark_methods.py

dataset-stats:
	python src/dataset_stats.py

eval-llm:
	python src/eval_llm.py

eval-faithfulness:
	python src/eval_faithfulness.py

clean:
	python -c "import shutil, pathlib; shutil.rmtree('.pytest_cache', ignore_errors=True); [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__')]"
