import logging
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config import get_settings
from app.services.llm_service import llm_service
from app.services.vector_store import LocalVectorStore

logger = logging.getLogger(__name__)
settings = get_settings()


class RAGService:
    """RAG for interview experiences using ChromaDB or local vector store fallback."""

    def __init__(self) -> None:
        self._client = None
        self._collection = None
        self._embedding_fn = None
        self._use_chroma: Optional[bool] = None
        self._local_store: Optional[LocalVectorStore] = None

    def _init_backend(self) -> None:
        if self._use_chroma is not None:
            return

        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            self._client = chromadb.PersistentClient(
                path=settings.chroma_persist_dir,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            embedding_fn = self._get_embedding_function()
            if embedding_fn:
                self._collection = self._client.get_or_create_collection(
                    name=settings.chroma_collection_name,
                    embedding_function=embedding_fn,
                    metadata={"hnsw:space": "cosine"},
                )
            else:
                self._collection = self._client.get_or_create_collection(
                    name=settings.chroma_collection_name,
                    metadata={"hnsw:space": "cosine"},
                )
            self._use_chroma = True
            logger.info("RAG using ChromaDB at %s", settings.chroma_persist_dir)
        except Exception as exc:
            logger.warning("ChromaDB unavailable (%s), using local vector store", exc)
            self._use_chroma = False
            store_path = Path(settings.chroma_persist_dir) / "local_vectors.json"
            self._local_store = LocalVectorStore(str(store_path))

    def _get_embedding_function(self):
        if self._embedding_fn is None:
            try:
                from chromadb.utils import embedding_functions

                self._embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                )
            except Exception as e:
                logger.warning("SentenceTransformer unavailable for ChromaDB: %s", e)
                self._embedding_fn = None
        return self._embedding_fn

    async def ingest_experience(
        self,
        company: str,
        role: str,
        experience: str,
        outcome: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> str:
        self._init_backend()
        doc_id = str(uuid.uuid4())
        metadata = {
            "company": company,
            "role": role,
            "outcome": outcome or "unknown",
            "difficulty": difficulty or "medium",
        }
        document = (
            f"Company: {company}\nRole: {role}\nOutcome: {outcome or 'N/A'}"
            f"\nDifficulty: {difficulty or 'N/A'}\n\n{experience}"
        )

        if self._use_chroma and self._collection:
            self._collection.add(
                ids=[doc_id],
                documents=[document],
                metadatas=[metadata],
            )
        elif self._local_store:
            self._local_store.add(document, metadata, doc_id=doc_id)

        return doc_id

    async def query(
        self,
        question: str,
        company: Optional[str] = None,
        role: Optional[str] = None,
        top_k: int = 5,
    ) -> tuple[List[Dict[str, Any]], str]:
        self._init_backend()

        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []
        distances: List[Optional[float]] = []

        if self._use_chroma and self._collection:
            where_filter = {"company": company} if company else None
            try:
                results = self._collection.query(
                    query_texts=[question],
                    n_results=top_k,
                    where=where_filter,
                )
                documents = results.get("documents", [[]])[0]
                metadatas = results.get("metadatas", [[]])[0]
                distances = results.get("distances", [[]])[0]
            except Exception as e:
                logger.error("ChromaDB query error: %s", e)
        elif self._local_store:
            documents, metadatas, scores = self._local_store.query(
                question, top_k=top_k, company=company
            )
            distances = [1 - s for s in scores]

        sources: List[Dict[str, Any]] = []
        context_parts: List[str] = []

        for i, doc in enumerate(documents):
            meta = metadatas[i] if i < len(metadatas) else {}
            dist = distances[i] if i < len(distances) else None
            sources.append({
                "company": meta.get("company", ""),
                "role": meta.get("role", ""),
                "outcome": meta.get("outcome", ""),
                "relevance_score": 1 - dist if dist is not None else None,
            })
            context_parts.append(doc)

        context = (
            "\n\n---\n\n".join(context_parts)
            if context_parts
            else "No relevant interview experiences found."
        )

        system_prompt = (
            "You are an expert placement preparation assistant. "
            "Answer questions about interview experiences based ONLY on the provided context. "
            "If the context doesn't contain relevant information, say so honestly."
        )

        user_prompt = f"""Context from interview experiences:
{context}

User question: {question}
{f'Company filter: {company}' if company else ''}
{f'Role filter: {role}' if role else ''}

Provide a helpful, detailed answer based on the interview experiences above."""

        answer = await llm_service.generate(
            user_prompt, system=system_prompt, temperature=0.5
        )
        return sources, answer


rag_service = RAGService()