from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        # Split on sentence boundaries while keeping sentences clean
        raw_sentences = re.split(r"(?<=[.!?])\s+|(?<=\.)\n+", text.strip())
        sentences = [s.strip() for s in raw_sentences if s.strip()]
        if not sentences:
            return []

        chunks: list[str] = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            group = sentences[i : i + self.max_sentences_per_chunk]
            chunk = " ".join(group).strip()
            if chunk:
                chunks.append(chunk)
        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if not current_text:
            return []
        if len(current_text) <= self.chunk_size:
            return [current_text]
        if not remaining_separators:
            # Fallback when no separators remain: split strictly by chunk_size
            return [
                current_text[i : i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]

        sep = remaining_separators[0]
        next_seps = remaining_separators[1:]

        if sep == "":
            splits = list(current_text)
        else:
            splits = current_text.split(sep)

        # If separator not present, proceed to next separator
        if len(splits) <= 1:
            return self._split(current_text, next_seps)

        chunks: list[str] = []
        current_chunk: list[str] = []
        current_len = 0
        sep_len = len(sep)

        for part in splits:
            if not part and sep != "":
                continue
            part_len = len(part)

            if part_len > self.chunk_size:
                if current_chunk:
                    chunks.append(sep.join(current_chunk))
                    current_chunk = []
                    current_len = 0
                chunks.extend(self._split(part, next_seps))
            else:
                needed = part_len if not current_chunk else current_len + sep_len + part_len
                if needed <= self.chunk_size:
                    current_chunk.append(part)
                    current_len = needed
                else:
                    if current_chunk:
                        chunks.append(sep.join(current_chunk))
                    current_chunk = [part]
                    current_len = part_len

        if current_chunk:
            chunks.append(sep.join(current_chunk))

        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    norm_a = math.sqrt(sum(x * x for x in vec_a))
    norm_b = math.sqrt(sum(y * y for y in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    dot_val = _dot(vec_a, vec_b)
    sim = dot_val / (norm_a * norm_b)
    return max(-1.0, min(1.0, sim))


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        fixed_chunker = FixedSizeChunker(chunk_size=chunk_size, overlap=20)
        sentence_chunker = SentenceChunker(max_sentences_per_chunk=3)
        recursive_chunker = RecursiveChunker(chunk_size=chunk_size)

        fixed_chunks = fixed_chunker.chunk(text)
        sentence_chunks = sentence_chunker.chunk(text)
        recursive_chunks = recursive_chunker.chunk(text)

        def _calc_stats(chunks: list[str]) -> dict:
            count = len(chunks)
            avg_len = sum(len(c) for c in chunks) / count if count > 0 else 0.0
            return {
                "count": count,
                "avg_length": avg_len,
                "chunks": chunks,
            }

        return {
            "fixed_size": _calc_stats(fixed_chunks),
            "by_sentences": _calc_stats(sentence_chunks),
            "recursive": _calc_stats(recursive_chunks),
        }


class HeadingChunker:
    """
    Chunk Markdown documents based on section headings (e.g. '## ...').
    Sections exceeding max_chunk_size are recursively split, prepending the
    parent heading to each child chunk to preserve contextual grounding.
    """

    def __init__(
        self,
        max_chunk_size: int = 400,
        fallback_chunker: RecursiveChunker | None = None,
    ) -> None:
        self.max_chunk_size = max_chunk_size
        self.fallback_chunker = fallback_chunker or RecursiveChunker(chunk_size=max_chunk_size)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        lines = text.split("\n")
        sections: list[tuple[str, list[str]]] = []
        current_heading = ""
        current_lines: list[str] = []

        for line in lines:
            if re.match(r"^#{1,4}\s+", line):
                if current_lines or current_heading:
                    sections.append((current_heading, current_lines))
                current_heading = line.strip()
                current_lines = []
            else:
                current_lines.append(line)

        if current_lines or current_heading:
            sections.append((current_heading, current_lines))

        chunks: list[str] = []
        for heading, body_lines in sections:
            body_text = "\n".join(body_lines).strip()
            full_section = f"{heading}\n\n{body_text}".strip() if heading else body_text
            if not full_section:
                continue

            if len(full_section) <= self.max_chunk_size:
                chunks.append(full_section)
            else:
                sub_chunks = self.fallback_chunker.chunk(body_text) if body_text else [heading]
                for idx, sub in enumerate(sub_chunks):
                    if heading:
                        prefix = heading if idx == 0 else f"{heading} (tiếp theo)"
                        combined = f"{prefix}\n\n{sub}".strip()
                    else:
                        combined = sub.strip()
                    if combined:
                        chunks.append(combined)

        return chunks

