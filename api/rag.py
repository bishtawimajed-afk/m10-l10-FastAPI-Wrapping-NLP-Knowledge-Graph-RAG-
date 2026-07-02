import re
from typing import Dict, Any, List

def run_rag_pipeline(question: str, k: int, weaviate_client, generator, embedder) -> Dict[str, Any]:
    sentinel_response = {
        "answer": "I cannot answer this from the available sources",
        "citations": [],
        "confidence": 0.0
    }

    vector = embedder.encode(question).tolist()

    res = (
        weaviate_client.query.get("Chunk", ["text", "chunk_id"])
        .with_near_vector({"vector": vector})
        .with_additional(["distance"])
        .with_limit(k)
        .do()
    )

    chunks = res.get("data", {}).get("Get", {}).get("Chunk", [])
    if not chunks:
        return sentinel_response

    context_str = ""
    for idx, chunk in enumerate(chunks, 1):
        context_str += f"[{idx}] {chunk['text']}\n"

    prompt = (
        f"Answer the question based only on the context provided below. "
        f"Cite each claim using the source number in square brackets like [1], [2], etc.\n\n"
        f"Context:\n{context_str}\n"
        f"Question: {question}\n"
        f"Answer:"
    )

    gen_outputs = generator(prompt, max_new_tokens=256, do_sample=False)
    generated_text = gen_outputs[0]["generated_text"]

    matches = re.findall(r"\[(\d+)\]", generated_text)
    valid_indices = []
    for m in matches:
        val = int(m)
        if 1 <= val <= len(chunks):
            valid_indices.append(val)

    if not valid_indices:
        return sentinel_response

    unique_indices = list(dict.fromkeys(valid_indices))
    citations = []
    scores = []

    for idx in unique_indices:
        chunk = chunks[idx - 1]
        distance = chunk.get("_additional", {}).get("distance", 0.0)
        score = max(0.0, min(1.0, 1.0 - distance))
        
        citations.append({
            "chunk_id": int(chunk["chunk_id"]),
            "score": float(score)
        })
        scores.append(score)

    confidence = sum(scores) / len(scores) if scores else 0.0

    return {
        "answer": generated_text,
        "citations": citations,
        "confidence": float(confidence)
    }