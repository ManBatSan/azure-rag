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

client = EmbeddingsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key),
)


def embed_text_batch(texts: list[str], model: str) -> list[list[float]]:
    """Call the Azure OpenAI embeddings endpoint, retrying on 429."""
    while True:
        try:
            resp = client.embed(model=model, input=texts)
            return [e.embedding for e in resp.data]
        except HttpResponseError as e:
            if e.status_code == 429:
                retry_after = 60
                print(f"\nRate limit hit (429). Waiting {retry_after}s before retry...")
                time.sleep(retry_after)
                continue
            raise


def main():
    parser = argparse.ArgumentParser(
        description="Generate embeddings for chunked texts via Azure OpenAI"
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to input JSONL file of chunks (with a 'text' field)",
    )
    parser.add_argument(
        "--output", "-o", required=True, help="Path to output JSONL file for embeddings"
    )
    parser.add_argument(
        "--batch-size", "-b", type=int, default=64, help="Number of texts to send per API call"
    )
    parser.add_argument(
        "--model",
        "-m",
        default="text-embedding-3-small",
        help="Azure OpenAI embedding model to use",
    )
    args = parser.parse_args()

    # First, count total chunks so tqdm knows the length
    with open(args.input, encoding="utf-8") as f:
        total_chunks = sum(1 for _ in f)

    buffer = []
    processed = 0
    out_fp = open(args.output, "w", encoding="utf-8")

    # Re-open to iterate
    with open(args.input, encoding="utf-8") as f, tqdm(total=total_chunks, unit="chunk") as pbar:
        for line in f:
            rec = json.loads(line)
            buffer.append(rec["text"])

            if len(buffer) >= args.batch_size:
                embs = embed_text_batch(buffer, args.model)
                for txt, vec in zip(buffer, embs):
                    out_fp.write(
                        json.dumps({"text": txt, "embedding": vec}, ensure_ascii=False) + "\n"
                    )
                    processed += 1
                    pbar.update(1)
                buffer = []

        # flush remainder
        if buffer:
            embs = embed_text_batch(buffer, args.model)
            for txt, vec in zip(buffer, embs):
                out_fp.write(json.dumps({"text": txt, "embedding": vec}, ensure_ascii=False) + "\n")
                processed += 1
                pbar.update(1)

    out_fp.close()
    print(f"\nWrote {processed} embeddings to {args.output}")


if __name__ == "__main__":
    main()
