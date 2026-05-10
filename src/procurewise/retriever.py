from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path

from .config import KNOWLEDGE_BASE_DIR
from .schemas import Evidence


TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9$]+")


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_PATTERN.findall(text)]


class PolicyRetriever:
    def __init__(self, knowledge_base_dir: Path = KNOWLEDGE_BASE_DIR) -> None:
        self.knowledge_base_dir = knowledge_base_dir
        self.documents = self._load_documents()
        self.document_frequencies = self._document_frequencies()

    def search(self, query: str, top_k: int = 4) -> list[Evidence]:
        query_terms = tokenize(query)
        if not query_terms:
            return []

        scored: list[Evidence] = []
        for doc in self.documents:
            score = self._score(query_terms, doc["tokens"])
            if score > 0:
                scored.append(
                    Evidence(
                        source=doc["source"],
                        heading=doc["heading"],
                        text=doc["text"],
                        score=round(score, 3),
                    )
                )
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]

    def _load_documents(self) -> list[dict[str, object]]:
        docs: list[dict[str, object]] = []
        for path in sorted(self.knowledge_base_dir.glob("*.md")):
            current_heading = path.stem.replace("_", " ").title()
            buffer: list[str] = []
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.startswith("#"):
                    if buffer:
                        self._append_doc(docs, path.name, current_heading, buffer)
                        buffer = []
                    current_heading = line.lstrip("#").strip()
                elif line.strip():
                    buffer.append(line.strip())
            if buffer:
                self._append_doc(docs, path.name, current_heading, buffer)
        return docs

    def _append_doc(
        self, docs: list[dict[str, object]], source: str, heading: str, lines: list[str]
    ) -> None:
        text = " ".join(lines)
        docs.append(
            {
                "source": source,
                "heading": heading,
                "text": text,
                "tokens": Counter(tokenize(text)),
            }
        )

    def _document_frequencies(self) -> Counter:
        frequencies: Counter = Counter()
        for doc in self.documents:
            frequencies.update(set(doc["tokens"].keys()))
        return frequencies

    def _score(self, query_terms: list[str], doc_terms: Counter) -> float:
        score = 0.0
        total_docs = max(len(self.documents), 1)
        for term in query_terms:
            if term not in doc_terms:
                continue
            tf = 1 + math.log(doc_terms[term])
            idf = math.log((1 + total_docs) / (1 + self.document_frequencies[term])) + 1
            score += tf * idf
        return score

