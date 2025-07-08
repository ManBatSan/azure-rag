import argparse
import json
import os

from datasets import load_dataset


def main(dataset_name: str, config_name: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    print(f"Loading dataset {dataset_name} with config '{config_name}'...")
    dataset = load_dataset(dataset_name, config_name)

    for split, data in dataset.items():
        out_path = os.path.join(output_dir, f"{config_name}_{split}.jsonl")
        print(f"Saving {split} to {out_path}...")
        with open(out_path, "w", encoding="utf-8") as f:
            for example in data:
                f.write(json.dumps(example) + "\n")

    print("Download complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download a Hugging Face dataset config to JSONL")
    parser.add_argument(
        "--dataset",
        type=str,
        default="enelpol/rag-mini-bioasq",
        help="Hugging Face dataset name",
    )
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Dataset config name (e.g. question-answer-passages, text-corpus)",
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "..", "data", "raw"),
        help="Output directory",
    )
    args = parser.parse_args()

    main(args.dataset, args.config, args.out_dir)
