import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from neo4j import GraphDatabase
import weaviate
import spacy
from transformers import pipeline

from api.models import (
    ExtractRequest, ExtractResponse,
    KGRequest, KGResponse,
    RAGRequest, RAGResponse,
    HealthResponse
)
from api.deps import get_nlp, get_session, get_weaviate, get_embedder, get_generator
from api.nlp import extract_entities
from api.kg import execute_kg_query
from api.rag import run_rag_pipeline

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.nlp = spacy.load("en_core_web_sm")
    
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
    app.state.neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    
    weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
    app.state.weaviate_client = weaviate.Client(url=weaviate_url)
    
    from sentence_transformers import SentenceTransformer
    app.state.embedder = SentenceTransformer("all-MiniLM-L6-v2")
    app.state.generator = pipeline("text2text-generation", model="google/flan-t5-base")
    
    yield
    app.state.neo4j_driver.close()

app = FastAPI(title="Recipe NLP & RAG Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("WEB_ORIGIN", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/extract", response_model=ExtractResponse)
async def api_extract_entities(payload: ExtractRequest, nlp=Depends(get_nlp)):
    ents = extract_entities(payload.text, nlp)
    return {"entities": ents}

@app.post("/kg/query", response_model=KGResponse)
async def api_query_knowledge_graph(payload: KGRequest, session=Depends(get_session)):
    return execute_kg_query(payload.question, session)

@app.post("/rag/answer", response_model=RAGResponse)
async def api_rag_answer(
    payload: RAGRequest,
    weaviate_client=Depends(get_weaviate),
    embedder=Depends(get_embedder),
    generator=Depends(get_generator)
):
    return run_rag_pipeline(payload.question, payload.k, weaviate_client, embedder, generator)

@app.get("/healthz", response_model=HealthResponse)
async def health_check():
    return {"status": "ok"}

@app.get("/readyz")
async def readiness_check(request: Request):
    try:
        driver = request.app.state.neo4j_driver
        with driver.session() as session:
            session.run("RETURN 1 AS ok").single()
        
        weaviate_client = request.app.state.weaviate_client
        if not weaviate_client.is_ready():
            raise Exception()
            
        return {"neo4j": "up", "weaviate": "up"}
    except Exception:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service Unavailable")