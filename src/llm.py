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
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, backend: str | None = None):
        if self._initialized:
            return
        self._initialized = True

        self.backend = backend or os.getenv("LLM_BACKEND", "llama_cpp")

        if self.backend == "llama_cpp":
            self._init_llama_cpp()
        elif self.backend == "anthropic":
            self._init_anthropic()
        elif self.backend == "openai":
            self._init_openai()
        else:
            raise ValueError(f"Unknown backend: {self.backend}")

    def _init_llama_cpp(self):
        from llama_cpp import Llama

        model_path = os.getenv("LLAMA_CPP_MODEL_PATH")
        if not model_path:
            raise ValueError(
                "LLAMA_CPP_MODEL_PATH not set in .env — point it at your "
                "downloaded .gguf file, e.g. models/llama-3-8b-instruct.Q4_K_M.gguf"
            )
        model_path = os.path.expandvars(model_path)
        self._llm = Llama(model_path=model_path, n_ctx=8192, n_gpu_layers=-1, verbose=False)

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

    def generate(self, prompt: str, system: str = None, max_tokens: int = 500) -> str:
        if self.backend == "llama_cpp":
            return self._generate_llama_cpp(prompt, system, max_tokens)
        elif self.backend == "anthropic":
            return self._generate_anthropic(prompt, system, max_tokens)
        elif self.backend == "openai":
            return self._generate_openai(prompt, system, max_tokens)

    def _generate_llama_cpp(self, prompt: str, system: str, max_tokens: int) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        output = self._llm.create_chat_completion(messages=messages, max_tokens=max_tokens)
        return output["choices"][0]["message"]["content"].strip()

    def _generate_anthropic(self, prompt: str, system: str, max_tokens: int) -> str:
        kwargs = {"model": self._model, "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}]}
        if system:
            kwargs["system"] = system
        response = self._client.messages.create(**kwargs)
        return response.content[0].text.strip()

    def _generate_openai(self, prompt: str, system: str, max_tokens: int) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = self._client.chat.completions.create(
            model=self._model, max_tokens=max_tokens, messages=messages
        )
        return response.choices[0].message.content.strip()


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger(__name__)
    model_path = os.getenv("LLAMA_CPP_MODEL_PATH")
    if not model_path or not os.path.exists(os.path.expandvars(model_path)):
        logger.error("No model found at LLAMA_CPP_MODEL_PATH. Set LLM_BACKEND or LLAMA_CPP_MODEL_PATH in .env first.")
        sys.exit(1)
    client = LLMClient()
    logger.info("Backend: %s", client.backend)
    result = client.generate("Say hello in exactly five words.")
    logger.info(result)
