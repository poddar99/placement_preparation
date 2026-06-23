"""Lightweight vector store fallback when ChromaDB is unavailable."""

from __future__ import annotations

import json
import logging
import math
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class LocalVectorStore:
    """JSON-backed vector store with cosine similarity search."""

    def __init__(self, persist_path: str) -> None:
        self.path = Path(persist_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._records: List[Dict[str, Any]] = []
        self._embedder = None
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                self._records = json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                logger.warning("Corrupt vector store at %s, resetting", self.path)
                self._records = []

    def _save(self) -> None:
        self.path.write_text(json.dumps(self._records, indent=2), encoding="utf-8")

    def _get_embedder(self):
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._embedder = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception as exc:
                logger.warning("SentenceTransformer unavailable: %s", exc)
                self._embedder = False
        return self._embedder if self._embedder is not False else None

    def _embed(self, text: str) -> List[float]:
        embedder = self._get_embedder()
        if embedder:
            return embedder.encode(text).tolist()
        # Bag-of-words fallback embedding
        tokens = text.lower().split()
        vocab = sorted(set(tokens))
        return [tokens.count(token) for token in vocab] or [1.0]

    def add(
        self,
        document: str,
        metadata: Dict[str, Any],
        doc_id: Optional[str] = None,
    ) -> str:
        record_id = doc_id or str(uuid.uuid4())
        self._records.append({
            "id": record_id,
            "document": document,
            "metadata": metadata,
            "embedding": self._embed(document),
        })
        self._save()
        return record_id

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        company: Optional[str] = None,
    ) -> Tuple[List[str], List[Dict[str, Any]], List[float]]:
        if not self._records:
            return [], [], []

        query_embedding = self._embed(query_text)
        scored: List[Tuple[float, Dict[str, Any]]] = []

        for record in self._records:
            meta = record.get("metadata", {})
            if company and meta.get("company", "").lower() != company.lower():
                continue
            score = _cosine_similarity(query_embedding, record.get("embedding", []))
            scored.append((score, record))

        scored.sort(key=lambda item: item[0], reverse=True)
        top = scored[:top_k]

        documents = [item[1]["document"] for item in top]
        metadatas = [item[1].get("metadata", {}) for item in top]
        scores = [item[0] for item in top]
        return documents, metadatas, scores