import os
import spacy
import weaviate
import neo4j
from neo4j import GraphDatabase

from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sentence_transformers import SentenceTransformer
from transformers import pipeline

from api.models import (
    ExtractRequest, ExtractResponse, 
    KGQueryRequest, KGQueryResponse, 
    RAGQueryRequest, RAGQueryResponse,
    HealthResponse
)
from api.nlp import extract_entities
from api.kg import execute_kg_query
from api.rag import run_rag_pipeline
from api.deps import get_session, get_weaviate, get_generator, get_embedder
from api.w9b_mapper import UnsupportedQueryError

def load_generator():
    return pipeline("text2text-generation", model="google/flan-t5-base")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.nlp = spacy.load("en_core_web_sm")
    
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
    app.state.neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    
    weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
    app.state.weaviate_client = weaviate.Client(url=weaviate_url)
    
    app.state.embedder = SentenceTransformer("all-MiniLM-L6-v2")
    app.state.generator = load_generator()
    
    yield
    
    app.state.neo4j_driver.close()
    del app.state.nlp

app = FastAPI(lifespan=lifespan)

web_origin = os.getenv("WEB_ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[web_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz", response_model=HealthResponse)
async def get_healthz():
    return HealthResponse(status="ok")

@app.get("/readyz")
async def get_readyz(request: Request):
    neo4j_status = "down"
    weaviate_status = "down"
    
    try:
        driver = request.app.state.neo4j_driver
        with driver.session() as session:
            result = session.run("RETURN 1 AS ok")
            if result.single():
                neo4j_status = "up"
    except Exception:
        neo4j_status = "down"
        
    try:
        client = request.app.state.weaviate_client
        if client.is_ready():
            weaviate_status = "up"
    except Exception:
        weaviate_status = "down"
        
    if neo4j_status == "down" or weaviate_status == "down":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"neo4j": neo4j_status, "weaviate": weaviate_status}
        )
        
    return {"neo4j": neo4j_status, "weaviate": weaviate_status}

@app.post("/extract", response_model=ExtractResponse)
async def post_extract(payload: ExtractRequest, request: Request):
    nlp_model = request.app.state.nlp
    try:
        ents = extract_entities(nlp_model, payload.text)
        return ExtractResponse(entities=ents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/kg/query", response_model=KGQueryResponse)
async def post_kg_query(payload: KGQueryRequest, session=Depends(get_session)):
    try:
        res = execute_kg_query(session, payload.question)
        return KGQueryResponse(**res)
    except UnsupportedQueryError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "reason": "unsupported_question",
                "supported_patterns": getattr(e, "supported_patterns", [])
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rag/answer", response_model=RAGQueryResponse)
async def post_rag_answer(
    payload: RAGQueryRequest,
    weaviate_client=Depends(get_weaviate),
    generator=Depends(get_generator),
    embedder=Depends(get_embedder)
):
    try:
        res = run_rag_pipeline(payload.question, payload.k, weaviate_client, generator, embedder)
        return RAGQueryResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))