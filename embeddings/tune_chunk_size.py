import json

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from embeddings.azure_embeddings import embed_text_batch
from ingestion.tokenizer import get_tokenizer

tokenizer = get_tokenizer()

# thresholds to test
CHUNK_SIZES = [300, 500, 700]
OVERLAPS = [50, 100, 200]


def count_token_lengths(file_path):
    """Return list of token lengths for each record in JSONL at file_path."""
    lengths = []
    for line in open(file_path, encoding="utf-8"):
        rec = json.loads(line)
        ids = tokenizer(rec["text"]).input_ids
        lengths.append(len(ids))
    return lengths


def chunk_text_ids(ids, size, overlap):
    """Return list of chunks (each a list of token IDs)."""
    chunks = []
    step = size - overlap
    for i in range(0, len(ids), step):
        chunk = ids[i : i + size]
        if chunk:
            chunks.append(chunk)
    return chunks


def avg_adjacent_similarity(chunks):
    """Compute avg cosine similarity between embeddings of adjacent chunks."""
    if len(chunks) < 2:
        return None
    # decode back to text for embedding call
    texts = [tokenizer.decode(c) for c in chunks]
    embs = embed_text_batch(texts)
    sims = [cosine_similarity([a], [b])[0][0] for a, b in zip(embs, embs[1:])]
    return float(np.mean(sims))


def main():
    raw_file = "data/processed/text-corpus_test.jsonl"
    lengths = count_token_lengths(raw_file)
    total = len(lengths)

    # 1) report % of texts exceeding each chunk size
    print("Document length distribution:")
    for size in CHUNK_SIZES:
        pct = sum(1 for lenght in lengths if lenght > size) / total * 100
        print(f"  >{size} tokens: {pct:.2f}%")

    # 2) for each (size, overlap), sample one long document to test avg_sim
    #    here we pick the *longest* document for each size
    print("\nAdjacency similarity on the longest doc per size:")
    # find one doc per threshold that exceeds chunk size
    docs = []
    for size in CHUNK_SIZES:
        # pick first doc that exceeds size
        for line in open(raw_file, encoding="utf-8"):
            rec = json.loads(line)
            ids = tokenizer(rec["text"]).input_ids
            if len(ids) > size:
                docs.append((size, ids, rec["text"][:100] + "..."))
                break

    for size, ids, snippet in docs:
        for overlap in OVERLAPS:
            chunks = chunk_text_ids(ids, size, overlap)
            sim = avg_adjacent_similarity(chunks)
            if sim is None:
                print(f"size={size}, overlap={overlap} -> only {len(chunks)} chunk(s), skipping")
            else:
                print(f"size={size}, overlap={overlap} -> avg_sim={sim:.3f}")


if __name__ == "__main__":
    main()
