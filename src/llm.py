"""
LLMClient — swappable backend abstraction.

Supports three backends behind one common interface:
- llama.cpp local (default, no API cost — matches project's no-budget constraint)
- Anthropic API (for reviewers who want to plug in their own key)
- OpenAI API (same, alternate provider)

Swapping backend never touches the RAG pipeline code (retrieval.py,
build_index.py) — only this file and the .env config change.
"""

import logging
import os
import threading
import time

logger = logging.getLogger(__name__)


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
        if self._initialized:
            return

        preferred = backend or os.getenv("LLM_BACKEND", "llama_cpp")
        backends = [preferred]
        if preferred != "llama_cpp":
            backends.append("llama_cpp")

        last_error = None
        for candidate in backends:
            self.backend = candidate
            try:
                if candidate == "llama_cpp":
                    self._init_llama_cpp()
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
        n_gpu_layers = int(os.getenv("LLAMA_CPP_N_GPU_LAYERS", "-1"))
        try:
            self._llm = Llama(model_path=model_path, n_ctx=8192, n_gpu_layers=n_gpu_layers, seed=42, verbose=False)
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

    @_retry(max_attempts=3, base_delay=2.0)
    def generate(self, prompt: str, system: str = None, max_tokens: int = 500, temperature: float | None = None) -> str:
        if self.backend == "llama_cpp":
            return self._generate_llama_cpp(prompt, system, max_tokens, temperature)
        if self.backend == "anthropic":
            return self._generate_anthropic(prompt, system, max_tokens)
        if self.backend == "openai":
            return self._generate_openai(prompt, system, max_tokens, temperature)
        raise ValueError(f"Unknown backend: {self.backend}")

    def _generate_llama_cpp(self, prompt: str, system: str, max_tokens: int, temperature: float | None = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        kwargs = {"messages": messages, "max_tokens": max_tokens}
        if temperature is not None:
            kwargs["temperature"] = temperature
        output = self._llm.create_chat_completion(**kwargs)
        return output["choices"][0]["message"]["content"].strip()

    def _generate_anthropic(self, prompt: str, system: str, max_tokens: int) -> str:
        kwargs = {"model": self._model, "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}]}
        if system:
            kwargs["system"] = system
        response = self._client.messages.create(**kwargs)
        return response.content[0].text.strip()

    def _generate_openai(self, prompt: str, system: str, max_tokens: int, temperature: float | None = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        kwargs = {"model": self._model, "max_tokens": max_tokens, "messages": messages}
        if temperature is not None:
            kwargs["temperature"] = temperature
        response = self._client.chat.completions.create(**kwargs)
        return response.choices[0].message.content.strip()
