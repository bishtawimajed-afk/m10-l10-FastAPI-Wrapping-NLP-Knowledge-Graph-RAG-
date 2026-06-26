from neo4j import Session
from fastapi import HTTPException, status
from api.w9b_mapper import map_query, UnsupportedQueryError

def execute_kg_query(question: str, session: Session):
    try:
        cypher_query = map_query(question)
        result = session.run(cypher_query)
        rows = [record.data() for record in result]
        return {
            "cypher": cypher_query,
            "rows": rows,
            "count": len(rows)
        }
    except UnsupportedQueryError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "reason": "unsupported_question",
                "supported_patterns": getattr(e, "supported_patterns", [])
            }
        )