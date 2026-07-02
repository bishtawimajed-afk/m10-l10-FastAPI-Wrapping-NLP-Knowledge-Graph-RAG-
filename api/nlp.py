import spacy
from typing import List
from api.models import Entity

def extract_entities(nlp_model, text: str) -> List[Entity]:
    doc = nlp_model(text)
    entities = []
    
    for ent in doc.ents:
        entities.append(
            Entity(
                text=ent.text,
                label=ent.label_,
                start=ent.start_char,
                end=ent.end_char
            )
        )
    
    entities.sort(key=lambda x: x.start)
    return entities