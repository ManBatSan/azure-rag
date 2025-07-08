import argparse
import json

from ingestion.tokenizer import get_tokenizer


def chunk_text_ids(ids, size, overlap):
    """Split token ID list into overlapping chunks."""
    chunks = []
    step = size - overlap
    for i in range(0, len(ids), step):
        chunk = ids[i : i + size]
        if chunk:
            chunks.append(chunk)
    return chunks


def main():
    parser = argparse.ArgumentParser(description="Chunk input JSONL into token-based windows")
    parser.add_argument("--size", type=int, default=500, help="Maximum number of tokens per chunk")
    parser.add_argument(
        "--overlap", type=int, default=100, help="Number of tokens to overlap between chunks"
    )
    parser.add_argument(
        "--input", type=str, required=True, help="Path to input JSONL with fields 'id' and 'text'"
    )
    parser.add_argument(
        "--output", type=str, required=True, help="Path to output JSONL for chunked records"
    )
    args = parser.parse_args()

    tokenizer = get_tokenizer()

    out_fp = open(args.output, "w", encoding="utf-8")
    total_chunks = 0

    for line in open(args.input, encoding="utf-8"):
        rec = json.loads(line)
        orig_id = rec.get("id") or rec.get("source_id") or rec.get("uuid")
        text = rec["text"]
        ids = tokenizer(text, add_special_tokens=False).input_ids
        chunks = chunk_text_ids(ids, args.size, args.overlap)

        for idx, chunk_ids in enumerate(chunks):
            chunk_text = tokenizer.decode(chunk_ids, skip_special_tokens=True)
            out_rec = {
                "id": f"{orig_id}_{idx}",
                "source_id": orig_id,
                "chunk_index": idx,
                "text": chunk_text,
            }
            out_fp.write(json.dumps(out_rec, ensure_ascii=False) + "\n")
            total_chunks += 1

    out_fp.close()
    print(f"Wrote {total_chunks} chunks to {args.output}")


if __name__ == "__main__":
    main()
