.PHONY: install test lint typecheck run eval-recall eval-llm eval-faithfulness clean

install:
	pip install -r requirements.txt
	pip install ruff mypy

test:
	pytest tests.py -v

lint:
	ruff check src/ app.py

typecheck:
	mypy src/config.py src/chunking.py src/post_process.py src/rag.py src/llm.py src/embedding.py --no-strict-optional --ignore-missing-imports

check: test lint typecheck

run:
	streamlit run app.py

mcp:
	python src/server.py

mcp-sse:
	python src/server.py --sse --port 8765

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
