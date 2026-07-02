export interface Entity {
  text: string;
  label: string;
  start: int;
  end: int;
}

export interface ExtractResponse {
  entities: Entity[];
}

export interface KGQueryResponse {
  cypher: string;
  rows: Record<string, any>[];
  count: number;
}

export interface Citation {
  chunk_id: number;
  score: number;
}

export interface RAGQueryResponse {
  answer: string;
  citations: Citation[];
  confidence: number;
}