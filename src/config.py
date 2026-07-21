import logging
import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def init_config(env_file: str | None = None) -> None:
    load_dotenv(env_file)


init_config()


def _validate_float_range(key: str, value: float, lo: float, hi: float) -> float:
    if not lo <= value <= hi:
        raise ValueError(
            f"{key}={value} is outside valid range [{lo}, {hi}]. "
            f"Check your .env file."
        )
    return value


def _validate_positive_int(key: str, value: int) -> int:
    if value < 1:
        raise ValueError(
            f"{key}={value} must be >= 1. Check your .env file."
        )
    return value


@dataclass
class RAGConfig:
    retrieval_top_k: int = int(os.getenv("RAG_TOP_K", "5"))
    retrieval_min_relevance: float = float(os.getenv("RAG_MIN_RELEVANCE", "0.3"))
    retrieval_n_candidates: int = int(os.getenv("RAG_N_CANDIDATES", "50"))

    expansion_enabled: bool = os.getenv("RAG_EXPANSION_ENABLED", "true").lower() == "true"
    expansion_n_terms: int = int(os.getenv("RAG_EXPANSION_N_TERMS", "3"))

    keyword_boost_enabled: bool = os.getenv("RAG_KEYWORD_BOOST_ENABLED", "true").lower() == "true"
    keyword_boost_weight: float = float(os.getenv("RAG_KEYWORD_BOOST_WEIGHT", "0.15"))

    forward_looking_penalty_enabled: bool = os.getenv("RAG_FORWARD_LOOKING_PENALTY_ENABLED", "true").lower() == "true"
    forward_looking_penalty_weight: float = float(os.getenv("RAG_FORWARD_LOOKING_PENALTY_WEIGHT", "-0.15"))
    forward_looking_patterns: list = field(default_factory=lambda:
                                      (os.getenv("RAG_FORWARD_LOOKING_PATTERNS", "").split(",")
                                       if os.getenv("RAG_FORWARD_LOOKING_PATTERNS")
                                       else ["through licensed restaurants", "increases in ingredient",
                                             "global conflicts", "severe weather", "climate change",
                                             "forward-looking statements", "could be adversely",
                                             "may not be achieved", "risk factors", "no assurance"]))

    hybrid_search_enabled: bool = os.getenv("RAG_HYBRID_SEARCH_ENABLED", "true").lower() == "true"

    cross_encoder_enabled: bool = os.getenv("RAG_CROSS_ENCODER_ENABLED", "true").lower() == "true"
    cross_encoder_model: str = os.getenv("RAG_CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    cross_encoder_device: str = os.getenv("RAG_CROSS_ENCODER_DEVICE", "cpu")
    cross_encoder_batch_size: int = int(os.getenv("RAG_CROSS_ENCODER_BATCH_SIZE", "32"))
    cross_encoder_weight: float = float(os.getenv("RAG_CROSS_ENCODER_WEIGHT", "0.7"))

    db_path: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    build_filings_per_company: int = int(os.getenv("RAG_FILINGS_PER_COMPANY", "8"))

    sec_user_agent: str = os.getenv("SEC_USER_AGENT", "RAG-Variance-Explainer (sebas@portfolio.dev)")
    structured_output_enabled: bool = os.getenv("RAG_STRUCTURED_OUTPUT_ENABLED", "true").lower() == "true"
    llm_max_tokens: int = int(os.getenv("RAG_LLM_MAX_TOKENS", "2048"))
    llm_temperature: float = float(os.getenv("RAG_LLM_TEMPERATURE", "0.1"))

    def __post_init__(self) -> None:
        _validate_positive_int("RAG_TOP_K", self.retrieval_top_k)
        _validate_float_range("RAG_MIN_RELEVANCE", self.retrieval_min_relevance, 0.0, 1.0)
        _validate_positive_int("RAG_N_CANDIDATES", self.retrieval_n_candidates)
        _validate_positive_int("RAG_EXPANSION_N_TERMS", self.expansion_n_terms)
        _validate_float_range("RAG_KEYWORD_BOOST_WEIGHT", self.keyword_boost_weight, -1.0, 1.0)
        _validate_float_range("RAG_FORWARD_LOOKING_PENALTY_WEIGHT", self.forward_looking_penalty_weight, -1.0, 1.0)
        _validate_float_range("RAG_CROSS_ENCODER_WEIGHT", self.cross_encoder_weight, 0.0, 1.0)
        _validate_positive_int("RAG_CROSS_ENCODER_BATCH_SIZE", self.cross_encoder_batch_size)
        _validate_positive_int("RAG_FILINGS_PER_COMPANY", self.build_filings_per_company)
        _validate_positive_int("RAG_LLM_MAX_TOKENS", self.llm_max_tokens)
        _validate_float_range("RAG_LLM_TEMPERATURE", self.llm_temperature, 0.0, 2.0)


config = RAGConfig()
