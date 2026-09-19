from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb  # noqa: F401

            client = chromadb.Client()
            self._collection = client.get_or_create_collection(name=collection_name)
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        """Build a normalized stored record for one document."""
        return {
            "id": doc.id,
            "content": doc.content,
            "embedding": self._embedding_fn(doc.content),
            "metadata": dict(doc.metadata) if doc.metadata else {},
        }

    def _search_records(
        self, query: str, records: list[dict[str, Any]], top_k: int
    ) -> list[dict[str, Any]]:
        """Run in-memory similarity search over provided records using dot product."""
        if not records or top_k <= 0:
            return []

        query_emb = self._embedding_fn(query)
        scored: list[dict[str, Any]] = []
        for rec in records:
            score = _dot(query_emb, rec["embedding"])
            scored.append({
                "id": rec["id"],
                "content": rec["content"],
                "score": score,
                "metadata": rec["metadata"],
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        for doc in docs:
            record = self._make_record(doc)
            self._store.append(record)

        if self._use_chroma and self._collection is not None and docs:
            try:
                ids = [doc.id for doc in docs]
                documents = [doc.content for doc in docs]
                embeddings = [self._embedding_fn(doc.content) for doc in docs]
                metadatas = [dict(doc.metadata) if doc.metadata else {} for doc in docs]
                self._collection.add(
                    ids=ids,
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas if any(metadatas) else None,
                )
            except Exception:
                pass

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        return len(self._store)

    def search_with_filter(
        self, query: str, top_k: int = 3, metadata_filter: dict | None = None
    ) -> list[dict[str, Any]]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if not metadata_filter:
            return self.search(query, top_k=top_k)

        candidates: list[dict[str, Any]] = []
        for rec in self._store:
            rec_meta = rec.get("metadata", {})
            matches = True
            for key, val in metadata_filter.items():
                if rec_meta.get(key) != val:
                    matches = False
                    break
            if matches:
                candidates.append(rec)

        return self._search_records(query, candidates, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        initial_len = len(self._store)
        self._store = [
            rec
            for rec in self._store
            if rec["id"] != doc_id and rec.get("metadata", {}).get("doc_id") != doc_id
        ]
        removed = len(self._store) < initial_len

        if self._use_chroma and self._collection is not None and removed:
            try:
                self._collection.delete(ids=[doc_id])
            except Exception:
                pass

        return removed
