"""
Test-wide safeguards: prevent accidental real LLM / network calls.

Any test that tries to initialise a real LLM backend (llama.cpp, Anthropic,
OpenAI) will fail loudly with a clear message instead of hanging or leaking
API keys in CI.
"""

from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def _block_real_llm():
    """Patch all LLM init methods so tests never load real models or call APIs.

    The unknown-backend test (test_llm_unknown_backend_fallback_raises_runtime_error)
    still passes because it expects *all* backends to fail — these patches
    make every backend fail instantly, which is exactly the condition it tests.
    """
    with (
        patch("src.llm.LLMClient._init_llama_cpp", side_effect=RuntimeError("blocked by test fixture - real LLM not allowed")),
        patch("src.llm.LLMClient._init_anthropic", side_effect=RuntimeError("blocked by test fixture - real LLM not allowed")),
        patch("src.llm.LLMClient._init_openai", side_effect=RuntimeError("blocked by test fixture - real LLM not allowed")),
    ):
        yield
