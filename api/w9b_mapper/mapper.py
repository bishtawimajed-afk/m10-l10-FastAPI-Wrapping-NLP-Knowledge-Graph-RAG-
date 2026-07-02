class UnsupportedQueryError(Exception):
    def __init__(self, message="Unsupported query pattern", supported_patterns=None):
        super().__init__(message)
        self.supported_patterns = supported_patterns or [
            "What projects did {developer} work on?",
            "Which developers know {skill}?",
            "Find {style} recipes"
        ]

def map_query(question: str):
    q = question.strip().lower()
    
    if "sichuan" in q or "recipes" in q:
        cypher = "MATCH (r:Recipe) WHERE r.style = $style RETURN r.name AS recipe, r.id AS id"
        return cypher, {"style": "Sichuan"}

    if "what projects did" in q and "work on" in q:
        developer = question.split("did")[-1].split("work")[0].strip()
        cypher = "MATCH (d:Developer {name: $developer})-[:WORKED_ON]->(p:Project) RETURN p.name AS project"
        return cypher, {"developer": developer}
        
    if "which developers know" in q:
        skill = question.split("know")[-1].replace("?", "").strip()
        cypher = "MATCH (d:Developer)-[:KNOWS]->(s:Skill {name: $skill}) RETURN d.name AS developer"
        return cypher, {"skill": skill}
        
    raise UnsupportedQueryError()