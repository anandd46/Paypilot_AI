"""TF-IDF embedding provider — always available, no external dependencies.

Gracefully falls back to keyword-based scoring if scikit-learn is unavailable.
"""
from __future__ import annotations

import math
import re
from typing import Any

try:
    from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore[import-untyped]
    from sklearn.metrics.pairwise import cosine_similarity  # type: ignore[import-untyped]
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    np = None  # type: ignore[assignment]



class TFIDFEmbeddingProvider:
    """TF-IDF based embedding provider — works without any API keys.
    
    Falls back to keyword-based scoring if scikit-learn is unavailable (e.g. Python 3.14).
    """

    provider_name = "tfidf"

    def __init__(self) -> None:
        self._vectorizer: Any = None
        self._corpus: list[str] = []
        self._product_ids: list[str] = []

    def _text_from_product(self, product: dict[str, Any]) -> str:
        parts = [
            product.get("name", ""),
            product.get("description", ""),
            product.get("category", ""),
            product.get("brand", "") or "",
            " ".join(product.get("tags", [])),
            " ".join(product.get("features", [])),
        ]
        return " ".join(p for p in parts if p).lower()

    def fit(self, products: list[dict[str, Any]]) -> None:
        """Fit vectorizer on product corpus."""
        if not SKLEARN_AVAILABLE:
            return
        self._corpus = [self._text_from_product(p) for p in products]
        self._product_ids = [p["id"] for p in products]
        if self._corpus:
            self._vectorizer = TfidfVectorizer(  # type: ignore[misc]
                max_features=5000,
                ngram_range=(1, 2),
                stop_words="english",
            )
            self._vectorizer.fit(self._corpus)

    def embed_query(self, query: str) -> list[float]:
        """Convert a query string to a TF-IDF vector."""
        if not SKLEARN_AVAILABLE or self._vectorizer is None:
            return []
        vec = self._vectorizer.transform([query.lower()])
        return vec.toarray()[0].tolist()

    def embed_product(self, product: dict[str, Any]) -> list[float]:
        if not SKLEARN_AVAILABLE or self._vectorizer is None:
            return []
        text = self._text_from_product(product)
        vec = self._vectorizer.transform([text])
        return vec.toarray()[0].tolist()

    def similarity(self, query_vec: list[float], product_vec: list[float]) -> float:
        if not SKLEARN_AVAILABLE or not query_vec or not product_vec:
            return 0.0
        q = np.array(query_vec).reshape(1, -1)  # type: ignore[union-attr]
        p = np.array(product_vec).reshape(1, -1)  # type: ignore[union-attr]
        score: float = float(cosine_similarity(q, p)[0][0])  # type: ignore[misc]
        return max(0.0, min(1.0, score))

    def _keyword_score(self, query: str, product: dict[str, Any]) -> float:
        """Simple keyword matching fallback when sklearn is unavailable."""
        text = self._text_from_product(product)
        words = set(re.findall(r"\w+", query.lower()))
        if not words:
            return 0.5
        matches = sum(1 for w in words if w in text and len(w) > 2)
        return min(1.0, matches / max(len(words), 1))

    def rank_products(
        self, query: str, products: list[dict[str, Any]], top_k: int = 10
    ) -> list[tuple[dict[str, Any], float]]:
        """Rank products by semantic similarity to query."""
        if not products:
            return []

        if not SKLEARN_AVAILABLE:
            # Keyword fallback
            scored = [(p, self._keyword_score(query, p)) for p in products]
            scored.sort(key=lambda x: x[1], reverse=True)
            return scored[:top_k]

        # Ensure vectorizer is fit
        if self._vectorizer is None:
            self.fit(products)

        query_vec = self.embed_query(query)
        if not any(query_vec):
            return [(p, 0.5) for p in products[:top_k]]

        scored: list[tuple[dict[str, Any], float]] = []
        for product in products:
            prod_vec = self.embed_product(product)
            score = self.similarity(query_vec, prod_vec)
            scored.append((product, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]


# Module-level singleton
_tfidf_provider: TFIDFEmbeddingProvider | None = None


def get_tfidf_provider() -> TFIDFEmbeddingProvider:
    global _tfidf_provider
    if _tfidf_provider is None:
        _tfidf_provider = TFIDFEmbeddingProvider()
    return _tfidf_provider

