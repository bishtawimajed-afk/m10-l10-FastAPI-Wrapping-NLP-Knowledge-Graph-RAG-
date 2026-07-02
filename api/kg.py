from neo4j import Session
from typing import Dict, Any
from api.w9b_mapper import map_query

def execute_kg_query(session: Session, question: str) -> Dict[str, Any]:
    cypher_query, params = map_query(question)
    result = session.run(cypher_query, **params)
    rows = [record.data() for record in result]
    
    return {
        "cypher": cypher_query,
        "rows": rows,
        "count": len(rows)
    }