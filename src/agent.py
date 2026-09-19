from __future__ import annotations

from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        """
        Answer a question by retrieving relevant context and querying the LLM.
        """
        results = self.store.search(question, top_k=top_k)
        context_blocks = [r["content"] for r in results if "content" in r]
        context_text = "\n\n".join(context_blocks)

        prompt = (
            f"Use the following pieces of context to answer the question at the end.\n\n"
            f"Context:\n{context_text}\n\n"
            f"Question: {question}\n\n"
            f"Answer:"
        )
        return self.llm_fn(prompt)
