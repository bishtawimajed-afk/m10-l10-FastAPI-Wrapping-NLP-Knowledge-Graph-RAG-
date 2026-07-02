from pydantic import BaseModel, Field
from typing import List, Dict, Any

class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)

class Entity(BaseModel):
    text: str
    label: str
    start: int
    end: int

class ExtractResponse(BaseModel):
    entities: List[Entity]

class KGQueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)

class KGQueryResponse(BaseModel):
    cypher: str
    rows: List[Dict[str, Any]]
    count: int

class UnsupportedQueryDetail(BaseModel):
    reason: str
    supported_patterns: List[str]

class Citation(BaseModel):
    chunk_id: int
    score: float

class RAGQueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    k: int = Field(default=4, ge=1, le=10)

class RAGQueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    confidence: float

class HealthResponse(BaseModel):
    status: str = "ok"

class ReadyDetail(BaseModel):
    neo4j: str
    weaviate: str