import json
import re
from html import unescape


def clean_text(t: str) -> str:
    t = unescape(t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


with (
    open("data/raw/text-corpus_test.jsonl") as fin,
    open("data/processed/text-corpus_test.jsonl", "w") as fout,
):
    for line in fin:
        obj = json.loads(line)
        obj["text"] = clean_text(obj["passage"])
        fout.write(json.dumps(obj) + "\n")
