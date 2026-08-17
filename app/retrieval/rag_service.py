"""
Knowledge Retrieval Service (Section 4.1 #6 / 5.3 'Retrieval').

For simplicity and to keep the toolkit runnable with only GROQ_API_KEY (Groq
does not currently serve a text-embeddings endpoint), this uses a simple
hashed bag-of-words vector + cosine similarity instead of a hosted embedding
model. In Postgres, swap `KnowledgeDocument.embedding` for a pgvector column
and this module for real embeddings (e.g. sentence-transformers) without
touching the API layer.
"""

from __future__ import annotations

import hashlib
import re

import numpy as np
from sqlalchemy.orm import Session

from app import models

VECTOR_DIM = 256


def embed_text(text: str) -> list[float]:
    vec = np.zeros(VECTOR_DIM, dtype=np.float64)
    for token in re.findall(r"[a-z0-9]+", text.lower()):
        idx = int(hashlib.md5(token.encode()).hexdigest(), 16) % VECTOR_DIM
        vec[idx] += 1.0
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


def cosine_similarity(a: list[float], b: list[float]) -> float:
    a_arr, b_arr = np.array(a), np.array(b)
    denom = np.linalg.norm(a_arr) * np.linalg.norm(b_arr)
    if denom == 0:
        return 0.0
    return float(np.dot(a_arr, b_arr) / denom)


def index_document(db: Session, project_id: str, title: str, content: str, source: str = "manual") -> models.KnowledgeDocument:
    doc = models.KnowledgeDocument(
        project_id=project_id,
        title=title,
        content=content,
        embedding=embed_text(content),
        source=source,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def query_documents(db: Session, project_id: str, query: str, top_k: int = 5) -> list[tuple[models.KnowledgeDocument, float]]:
    query_vec = embed_text(query)
    docs = db.query(models.KnowledgeDocument).filter(models.KnowledgeDocument.project_id == project_id).all()
    scored = [(doc, cosine_similarity(query_vec, doc.embedding)) for doc in docs]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:top_k]
