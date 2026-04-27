"""
Stream model files from HuggingFace directly to S3 (no local disk needed).

Usage:
    python upload_hf_to_s3.py --repo-id fdtn-ai/Foundation-Sec-8B-Reasoning \
                              --s3-uri s3://your-bucket/foundation-sec-8b-reasoning/

Requires: pip install huggingface_hub boto3
For gated models, set the HF_TOKEN environment variable.
"""

import argparse
import os

import boto3
from huggingface_hub import HfFileSystem
from tqdm import tqdm


def parse_s3_uri(s3_uri):
    if not s3_uri.startswith("s3://"):
        raise ValueError(f"Invalid S3 URI: {s3_uri}")
    path = s3_uri[5:]
    parts = path.split("/", 1)
    bucket = parts[0]
    prefix = parts[1] if len(parts) > 1 else ""
    return bucket, prefix


def sync_hf_to_s3(repo_id, s3_uri):
    fs = HfFileSystem()
    s3_client = boto3.client("s3")

    bucket, s3_prefix = parse_s3_uri(s3_uri)
    if s3_prefix and not s3_prefix.endswith("/"):
        s3_prefix += "/"

    print(f"Scanning HuggingFace repo: {repo_id}")
    files = fs.ls(repo_id, detail=False)
    hf_files = [f for f in files if fs.isfile(f)]
    print(f"Found {len(hf_files)} files. Starting transfer to S3...\n")

    for hf_file in hf_files:
        filename = hf_file.replace(f"{repo_id}/", "")
        if filename.endswith(".bin"):
            print(f"  Skipping {filename} (prefer safetensors)")
            continue

        s3_key = f"{s3_prefix}{filename}"
        file_size = fs.info(hf_file).get("size", 0)

        with fs.open(hf_file, "rb") as remote_file:
            with tqdm(
                total=file_size,
                unit="B",
                unit_scale=True,
                desc=filename,
            ) as pbar:
                s3_client.upload_fileobj(
                    remote_file, bucket, s3_key, Callback=pbar.update
                )

    print("\nUpload complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stream HuggingFace model to S3")
    parser.add_argument(
        "--repo-id",
        default="fdtn-ai/Foundation-Sec-8B-Reasoning",
        help="HuggingFace model ID (default: fdtn-ai/Foundation-Sec-8B-Reasoning)",
    )
    parser.add_argument(
        "--s3-uri",
        required=True,
        help="S3 destination URI (e.g. s3://your-bucket/foundation-sec-8b-reasoning/)",
    )
    args = parser.parse_args()
    sync_hf_to_s3(args.repo_id, args.s3_uri)
