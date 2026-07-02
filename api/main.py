import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status, Header, Security
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from jose import jwt, JWTError

from .deps import get_embedder, get_generator, get_nlp, get_session, get_weaviate
from .models import (
    Entity,
    ExtractRequest,
    ExtractResponse,
    HealthResponse,
    KGRequest,
    KGResponse,
    RAGRequest,
    RAGResponse,
    UnsupportedQueryDetail,
)

from api.auth import (
    create_access_token,
    verify_jwt,
    verify_api_key,
    verify_api_key_or_jwt,
    api_key_header,
    oauth2_scheme,
    get_jwt_secret,
    get_jwt_algorithm
)

USER_STORE = {
    "admin": "admin",
    "demo": "demo",
    "stretch": "stretch"
}

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="M10 Recipe Service", lifespan=lifespan)


@app.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    expected_password = USER_STORE.get(payload.username)
    if payload.username in USER_STORE and payload.password == expected_password:
        token = create_access_token(subject=payload.username)
        return {"access_token": token, "token_type": "bearer"}
        
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password"
    )


@app.get("/admin/echo")
def admin_echo(
    api_key: str = Security(api_key_header),
    token: str = Depends(oauth2_scheme)
):
    valid_key = os.environ.get("API_KEY_VALID", os.environ.get("API_KEY", "my-super-secure-dev-api-key"))
    
    if api_key and api_key == valid_key and (not token or token == "None"):
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Valid credential but wrong scope."
         )
         
    if not token or token == "None":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or Expired Token"
        )
        
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[get_jwt_algorithm()])
        return {"message": "echo", "user": payload.get("sub")}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or Expired Token"
        )


@app.post("/extract", response_model=ExtractResponse, dependencies=[Depends(verify_api_key_or_jwt)])
def extract(req: ExtractRequest, nlp=Depends(get_nlp)):
    raise NotImplementedError


@app.post("/kg/query", response_model=KGResponse, dependencies=[Depends(verify_api_key_or_jwt)])
def kg_query(req: KGRequest, session=Depends(get_session)):
    raise NotImplementedError


@app.post("/rag/answer", response_model=RAGResponse, dependencies=[Depends(verify_api_key_or_jwt)])
def rag_answer(req: RAGRequest, weaviate_client=Depends(get_weaviate), generator=Depends(get_generator), embedder=Depends(get_embedder)):
    raise NotImplementedError


@app.get("/healthz")
def healthz():
    raise NotImplementedError


@app.get("/readyz")
def readyz(session=Depends(get_session), weaviate_client=Depends(get_weaviate)):
    raise NotImplementedError