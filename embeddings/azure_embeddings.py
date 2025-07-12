#!/usr/bin/env python3
import argparse
import json
import os
import time

from azure.ai.inference import EmbeddingsClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv(override=True)

endpoint = os.environ["EMBEDDINGS_ENDPOINT"]
key = os.environ["EMBEDDINGS_KEY"]
client = EmbeddingsClient(endpoint=endpoint, credential=AzureKeyCredential(key))


def embed_text_batch(texts: list[str], model: str) -> list[list[float]]:
    while True:
        try:
            resp = client.embed(model=model, input=texts)
            return [e.embedding for e in resp.data]
        except HttpResponseError as e:
            if e.status_code == 429:
                time.sleep(60)
                continue
            raise


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-i", "--input", required=True, help="JSONL of chunks with id & text")
    p.add_argument("-o", "--output", required=True, help="JSONL for embeddings (will include id)")
    p.add_argument("-b", "--batch-size", type=int, default=64)
    p.add_argument("-m", "--model", default="text-embedding-3-small")
    args = p.parse_args()

    # Count total
    with open(args.input, encoding="utf-8") as f:
        total = sum(1 for _ in f)

    buffer = []
    meta_buffer = []
    out_fp = open(args.output, "w", encoding="utf-8")
    processed = 0

    with open(args.input, encoding="utf-8") as fin, tqdm(total=total) as bar:
        for line in fin:
            rec = json.loads(line)
            buffer.append(rec["text"])
            meta_buffer.append(
                {
                    "id": rec["id"],
                    "source_id": rec.get("source_id"),
                    "chunk_index": rec.get("chunk_index"),
                    "text": rec["text"],
                }
            )
            if len(buffer) >= args.batch_size:
                embs = embed_text_batch(buffer, args.model)
                for meta, vec in zip(meta_buffer, embs):
                    out_fp.write(
                        json.dumps(
                            {
                                "id": meta["id"],
                                "source_id": meta["source_id"],
                                "chunk_index": meta["chunk_index"],
                                "text": meta["text"],
                                "embedding": vec,
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
                    processed += 1
                    bar.update(1)
                buffer.clear()
                meta_buffer.clear()

        # Flush remainder
        if buffer:
            embs = embed_text_batch(buffer, args.model)
            for meta, vec in zip(meta_buffer, embs):
                out_fp.write(
                    json.dumps(
                        {
                            "id": meta["id"],
                            "source_id": meta["source_id"],
                            "chunk_index": meta["chunk_index"],
                            "text": meta["text"],
                            "embedding": vec,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                processed += 1
                bar.update(1)

    out_fp.close()
    print(f"Wrote {processed} embeddings with IDs to {args.output}")


if __name__ == "__main__":
    main()
