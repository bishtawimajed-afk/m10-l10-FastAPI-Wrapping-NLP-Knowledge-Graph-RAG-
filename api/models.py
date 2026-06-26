"""Pydantic request/response models for the recipe service.

These are the typed-boundary contracts. They must mirror the TypeScript
interfaces in `web/lib/types.ts` exactly — drift produces silent render
failures in the Next.js frontend.
"""
from typing import List, Literal, Dict, Any

from pydantic import BaseModel, Field


# --- /extract --------------------------------------------------------

class ExtractRequest(BaseModel):
    """Request body for POST /extract.

    The request field has a length constraint that gates 422 on empty
    or oversized input.
    """
    # نص غير فارغ ومحدود بـ 5000 حرف كحد أقصى
    text: str = Field(..., min_length=1, max_length=5000)


class Entity(BaseModel):
    """A single named-entity span.

    Field names must match the corresponding TypeScript Entity
    interface in `web/lib/types.ts` exactly.
    """
    text: str = Field(...)
    label: str = Field(...)
    start: int = Field(...)
    end: int = Field(...)


class ExtractResponse(BaseModel):
    """Response body for POST /extract.

    Per the Evaluation Methodology, the returned list is ordered by
    start offset ascending.
    """
    entities: List[Entity] = Field(...)


# --- /kg/query -------------------------------------------------------

class KGRequest(BaseModel):
    """Request body for POST /kg/query.

    The question field has a length constraint.
    """
    # السؤال غير فارغ وأقل من 500 حرف
    question: str = Field(..., min_length=1, max_length=500)


class KGResponse(BaseModel):
    """Response body for POST /kg/query."""
    cypher: str = Field(...)
    rows: List[Dict[str, Any]] = Field(...)
    count: int = Field(...)


class UnsupportedQueryDetail(BaseModel):
    """Structured detail returned on 422 from /kg/query."""
    reason: Literal["unsupported_question"] = "unsupported_question"
    supported_patterns: List[str]


# --- /rag/answer -----------------------------------------------------

class RAGRequest(BaseModel):
    """Request body for POST /rag/answer.

    The question field has a length constraint; `k` is a bounded
    integer with a default.
    """
    question: str = Field(..., min_length=1, max_length=500)
    # القيمة الافتراضية 4 ويجب أن تقع بين 1 و 10
    k: int = Field(default=4, ge=1, le=10)


class Citation(BaseModel):
    """One citation: chunk id and retrieval score.

    Field names must match the TypeScript Citation interface.
    """
    chunk_id: int = Field(...)
    score: float = Field(...)


class RAGResponse(BaseModel):
    """Response body for POST /rag/answer.

    Grounding contract: when `answer` is not the empty-retrieval
    sentinel, `len(citations) > 0` is required.
    """
    answer: str = Field(...)
    citations: List[Citation] = Field(...)
    confidence: float = Field(...)


# --- Health / readiness ---------------------------------------------

class HealthResponse(BaseModel):
    """Liveness response."""
    status: str = Field(default="ok")


class ReadyDetail(BaseModel):
    """Readiness detail naming each backend's status."""
    neo4j: str = Field(...)
    weaviate: str = Field(...)