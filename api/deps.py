from fastapi import Request

def get_nlp(request: Request):
    return request.app.state.nlp

def get_session(request: Request):
    driver = request.app.state.neo4j_driver
    with driver.session() as session:
        yield session

def get_weaviate(request: Request):
    return request.app.state.weaviate_client

def get_embedder(request: Request):
    return request.app.state.embedder

def get_generator(request: Request):
    return request.app.state.generator