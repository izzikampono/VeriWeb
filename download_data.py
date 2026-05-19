import argparse
from huggingface_hub import snapshot_download


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download VeriWeb dataset")
    parser.add_argument(
        "--task-id",
        type=int,
        default=105,
        help="Task ID to download (default: 105) , see category.json for available task ids ",
    )
    parser.add_argument(
        "--repo-id",
        type=str,
        default="2077AIDataFoundation/VeriWeb",
        help="Hugging Face dataset repository ID",
    )
    parser.add_argument(
        "--repo-type",
        type=str,
        default="dataset",
        choices=["dataset", "model", "space"],
        help="Repository type on Hugging Face",
    )
    parser.add_argument(
        "--local-dir",
        type=str,
        default=None,
        help="Output directory (default: ./veriweb/images/<task-id>)",
    )
    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    task_id = args.task_id
    local_dir = args.local_dir or f"./veriweb/images/{task_id}"

    snapshot_download(
        repo_id=args.repo_id,
        repo_type=args.repo_type,
        allow_patterns=[f"data/{task_id}/*"],  # start with one task
        local_dir=local_dir,
    )



if __name__ == "__main__":
    args = parse_args()
    main(args)