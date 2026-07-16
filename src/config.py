import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


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

    llm_max_tokens: int = int(os.getenv("RAG_LLM_MAX_TOKENS", "2048"))
    llm_temperature: float = float(os.getenv("RAG_LLM_TEMPERATURE", "0.1"))


config = RAGConfig()
