"""
LLMClient — swappable backend abstraction.

Supports four backends behind one common interface:
- llama.cpp local (default, no API cost — matches project's no-budget constraint)
- llama.cpp server (local Docker, no in-process model)
- Anthropic API (for reviewers who want to plug in their own key)
- OpenAI API (same, alternate provider)

Swapping backend never touches the RAG pipeline code (retrieval.py,
build_index.py) — only this file and the .env config change.
"""

import logging
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeout

from logging_config import log_timer

logger = logging.getLogger(__name__)


class OutputLimitError(ValueError):
    """The model stopped before completing its answer due to the output budget."""


_LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "120"))
_LLAMA_SERVER_TIMEOUT = int(os.getenv("LLAMA_SERVER_TIMEOUT", "300"))
_MAX_CONCURRENT = int(os.getenv("LLM_MAX_CONCURRENT", "1"))
_llm_semaphore = threading.Semaphore(_MAX_CONCURRENT)
_executor = ThreadPoolExecutor(max_workers=_MAX_CONCURRENT)


def _retry(max_attempts: int = 3, base_delay: float = 2.0):
    """Decorator: retry with exponential backoff on transient failure."""
    def decorator(fn):
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    status_code = getattr(e, "status_code", None)
                    if isinstance(e, OutputLimitError) or (
                        isinstance(status_code, int) and 400 <= status_code < 500 and status_code != 429
                    ) or (
                        isinstance(e, ValueError) and "exceed context window" in str(e)
                    ):
                        raise
                    if attempt < max_attempts:
                        delay = base_delay * (2 ** (attempt - 1))
                        logger.warning(
                            "LLM call failed (attempt %d/%d): %s. Retrying in %.1fs...",
                            attempt, max_attempts, e, delay,
                        )
                        time.sleep(delay)
            raise last_exc
        return wrapper
    return decorator


class LLMClient:
    _instance = None
    _lock = threading.Lock()

    _initialized: bool

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    @classmethod
    def reset(cls):
        with cls._lock:
            cls._instance = None

    def __init__(self, backend: str | None = None):
        """Initialize the LLM client with a swappable backend.

        Tries the preferred backend first; falls back to llama_cpp if that
        fails. Raises RuntimeError if every backend in the chain fails.
        Singleton — subsequent calls return the same instance without
        re-initializing.
        """
        if self._initialized:
            return

        preferred = backend or os.getenv("LLM_BACKEND", "llama_cpp")
        backends = [preferred]
        if preferred not in ("llama_cpp", "llama_server"):
            backends.append("llama_cpp")

        last_error = None
        for candidate in backends:
            self.backend = candidate
            try:
                if candidate == "llama_cpp":
                    self._init_llama_cpp()
                elif candidate == "llama_server":
                    self._init_llama_server()
                elif candidate == "anthropic":
                    self._init_anthropic()
                elif candidate == "openai":
                    self._init_openai()
                else:
                    raise ValueError(f"Unknown backend: {candidate}")
                self._initialized = True
                if candidate != preferred:
                    logger.warning(
                        "Preferred backend '%s' unavailable, fell back to '%s'.",
                        preferred, candidate,
                    )
                return
            except Exception as e:
                last_error = e
                logger.warning("Backend '%s' failed: %s", candidate, e)
                continue

        cls = type(self)
        cls._instance = None
        self._initialized = False
        raise RuntimeError(
            f"All LLM backends failed. Last error: {last_error}"
        ) from last_error

    def _init_llama_cpp(self):
        from llama_cpp import Llama

        model_path = os.getenv("LLAMA_CPP_MODEL_PATH")
        if not model_path:
            raise ValueError(
                "LLAMA_CPP_MODEL_PATH not set in .env — point it at your "
                "downloaded .gguf file, e.g. models/llama-3-8b-instruct.Q4_K_M.gguf"
            )
        model_path = os.path.expandvars(model_path)
        n_gpu_layers = int(os.getenv("LLAMA_CPP_N_GPU_LAYERS", "0"))
        n_batch = int(os.getenv("LLAMA_CPP_N_BATCH", "32"))
        n_ctx = int(os.getenv("LLAMA_CPP_N_CTX", "8192"))
        if n_batch < 1 or n_ctx < 1:
            raise ValueError("LLAMA_CPP_N_BATCH and LLAMA_CPP_N_CTX must be positive integers")
        try:
            self._llm = Llama(model_path=model_path, n_ctx=n_ctx, n_batch=n_batch, n_gpu_layers=n_gpu_layers, seed=42, verbose=False)
        except Exception as e:
            if "CUDA" in str(e) or "cuda" in str(e) or "memory" in str(e).lower():
                raise RuntimeError(
                    f"GPU memory error loading model. Try setting LLAMA_CPP_N_GPU_LAYERS=0 in .env "
                    f"to use CPU only, or reduce n_ctx. Original error: {e}"
                ) from e
            raise

    def _init_anthropic(self):
        import anthropic

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in .env")
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")

    def _init_openai(self):
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in .env")
        self._client = OpenAI(api_key=api_key)
        self._model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def _init_llama_server(self):
        from openai import OpenAI

        self._client = OpenAI(
            api_key="local",
            base_url="http://127.0.0.1:8080/v1",
            timeout=_LLAMA_SERVER_TIMEOUT,
            max_retries=0,
        )
        models = self._client.models.list().data
        self._model = os.getenv("LLAMA_SERVER_MODEL") or (models[0].id if models else None)
        if not self._model:
            raise RuntimeError("Local llama-server has no loaded model")

    @_retry(max_attempts=3, base_delay=2.0)
    def generate(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int = 500,
        temperature: float | None = None,
        response_format: dict | None = None,
    ) -> str:
        """Generate a completion for *prompt*, routed to the active backend.

        Automatically retries on transient failures (network timeout, API
        503) with exponential backoff. The caller never needs to know which
        backend is actually serving the request.

        Applies a global semaphore to cap concurrent generations (default 1)
        and enforces a per-call timeout (default 120 s) to prevent hangs.
        """

        t_start = time.perf_counter()
        timeout = _LLAMA_SERVER_TIMEOUT if self.backend == "llama_server" else _LLM_TIMEOUT
        acquired = _llm_semaphore.acquire(timeout=timeout)
        if not acquired:
            raise TimeoutError(
                f"All {_MAX_CONCURRENT} generation slot(s) busy — try again later."
            )
        try:
            if self.backend == "llama_cpp":
                future = _executor.submit(self._generate_llama_cpp, prompt, system, max_tokens, temperature, response_format)
            elif self.backend == "anthropic":
                future = _executor.submit(self._generate_anthropic, prompt, system, max_tokens)
            elif self.backend == "llama_server":
                future = _executor.submit(self._generate_openai, prompt, system, max_tokens, temperature, response_format)
            elif self.backend == "openai":
                future = _executor.submit(self._generate_openai, prompt, system, max_tokens, temperature)
            else:
                raise ValueError(f"Unknown backend: {self.backend}")

            elapsed = time.perf_counter() - t_start
            remaining = max(timeout - elapsed, 1)
            with log_timer(logger, f"llm.{self.backend}"):
                try:
                    return future.result(timeout=remaining)
                except FuturesTimeout:
                    raise TimeoutError(f"LLM ({self.backend}) did not respond within {timeout}s timeout.") from None
        finally:
            _llm_semaphore.release()

    def _generate_llama_cpp(
        self,
        prompt: str,
        system: str | None,
        max_tokens: int,
        temperature: float | None = None,
        response_format: dict | None = None,
    ) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        kwargs = {"messages": messages, "max_tokens": max_tokens}
        if temperature is not None:
            kwargs["temperature"] = temperature
        if response_format is not None:
            kwargs["response_format"] = response_format
        output = self._llm.create_chat_completion(**kwargs)
        if output["choices"][0].get("finish_reason") == "length":
            raise OutputLimitError(f"Generated answer reached the {max_tokens}-token output limit")
        return output["choices"][0]["message"]["content"].strip()

    def _generate_anthropic(self, prompt: str, system: str | None, max_tokens: int) -> str:
        kwargs = {"model": self._model, "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}]}
        if system:
            kwargs["system"] = system
        response = self._client.messages.create(**kwargs)
        return response.content[0].text.strip()

    def _generate_openai(self, prompt: str, system: str | None, max_tokens: int, temperature: float | None = None, response_format: dict | None = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        kwargs = {"model": self._model, "max_tokens": max_tokens, "messages": messages}
        if temperature is not None:
            kwargs["temperature"] = temperature
        if response_format is not None:
            kwargs["response_format"] = response_format
        response = self._client.chat.completions.create(**kwargs)
        if response.choices[0].finish_reason == "length":
            raise OutputLimitError(f"Generated answer reached the {max_tokens}-token output limit")
        return response.choices[0].message.content.strip()
