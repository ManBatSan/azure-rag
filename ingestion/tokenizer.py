from transformers import AutoTokenizer


def get_tokenizer():
    return AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")


if __name__ == "__main__":
    tok = get_tokenizer()
    sample = "Hello world! This is a tokenizer test."
    print(tok(sample))
