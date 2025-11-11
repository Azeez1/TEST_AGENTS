import os
from typing import List, Dict, Any
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

INDEX = os.getenv("PINECONE_INDEX", "proposal_kb")
_EMBED = os.getenv("EMBEDDINGS_MODEL", "gte-large")

class RAGClient:
    def __init__(self):
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise RuntimeError("Missing PINECONE_API_KEY")
        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(INDEX)
        self.embed = SentenceTransformer(_EMBED)  # swap out if using hosted embeddings

    def embed_text(self, text: str) -> List[float]:
        return self.embed.encode([text], normalize_embeddings=True)[0].tolist()

    def upsert(self, records: List[Dict[str, Any]]):
        # each record: {"id": str, "text": str, "metadata": {...}}
        vectors = []
        for r in records:
            vec = self.embed_text(r["text"])
            vectors.append({"id": r["id"], "values": vec, "metadata": r.get("metadata", {})})
        self.index.upsert(vectors=vectors)

    def search(self, query: str, filters: Dict[str, Any] = None, k: int = 5) -> List[Dict[str, Any]]:
        qv = self.embed_text(query)
        resp = self.index.query(vector=qv, top_k=k, filter=filters or {}, include_metadata=True)
        out = []
        for m in resp.matches:
            md = m.metadata or {}
            out.append({
                "verbatim": md.get("verbatim") or md.get("text") or "",
                "title": md.get("title", ""),
                "source_url": md.get("source_url", ""),
                "jurisdiction": md.get("jurisdiction", ""),
                "standard": md.get("standard", ""),
                "score": m.score
            })
        return out
