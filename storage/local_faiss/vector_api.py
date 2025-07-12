import json
import os

import faiss
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel


class Query(BaseModel):
    vector: list[float]
    k: int = 5


app = FastAPI()
index = None
ids: list[str] = []
passages: dict[str, str] = {}

# Ruta donde persistiremos el índice y los metadatos
INDEX_DIR = "/data/index"
FAISS_FILE = os.path.join(INDEX_DIR, "faiss.index")
IDS_FILE = os.path.join(INDEX_DIR, "ids.json")
PASSAGES_FILE = os.path.join(INDEX_DIR, "passages.json")
EMBEDDINGS_FILE = "/data/processed/embeddings.jsonl"  # origen


@app.on_event("startup")
def load_index_and_passages():
    global index, ids, passages

    if os.path.isdir(INDEX_DIR) and os.path.exists(FAISS_FILE):
        index = faiss.read_index(FAISS_FILE)
        with open(IDS_FILE, "r", encoding="utf-8") as f:
            ids = json.load(f)
        with open(PASSAGES_FILE, "r", encoding="utf-8") as f:
            passages = json.load(f)

        print(f"Loaded persisted FAISS index with {index.ntotal} vectors.")
        print(f"Loaded {len(passages)} passages from metadata files.")
        return

    embeddings_list: list[list[float]] = []
    ids = []
    passages = {}

    with open(EMBEDDINGS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            embeddings_list.append(obj["embedding"])
            ids.append(obj["id"])
            passages[obj["id"]] = obj["text"]

    embeddings = np.array(embeddings_list, dtype="float32")
    dim = embeddings.shape[1]

    cpu_index = faiss.IndexFlatIP(dim)
    faiss.normalize_L2(embeddings)
    cpu_index.add(embeddings)
    index = cpu_index

    print(f"Built FAISS index with {index.ntotal} vectors.")
    print(f"Loaded {len(passages)} passages from JSONL.")

    os.makedirs(INDEX_DIR, exist_ok=True)
    faiss.write_index(index, FAISS_FILE)
    with open(IDS_FILE, "w", encoding="utf-8") as f:
        json.dump(ids, f)
    with open(PASSAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(passages, f)
    print(f"Persisted index and metadata to {INDEX_DIR}.")


@app.post("/search")
def search(q: Query):
    if index is None:
        raise RuntimeError("FAISS index not loaded")

    vec = np.array([q.vector], dtype="float32")
    faiss.normalize_L2(vec)
    similarity_scores, neighbor_idxs = index.search(vec, q.k)

    results = []
    for rank, idx in enumerate(neighbor_idxs[0]):
        doc_id = ids[idx]
        score = float(similarity_scores[0][rank])
        text = passages.get(doc_id, "")
        results.append({"id": doc_id, "score": score, "text": text})

    return {"results": results}


@app.get("/health")
def health():
    return {"status": "ok", "vectors": index.ntotal}
