"""Inspect Hugging Face seed assets for research-pipeline suitability.

This script does not treat Hugging Face datasets as authoritative evidence. It
only records metadata that helps decide whether a dataset can seed discovery.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "data" / "exports" / "huggingface_asset_inspection.json"

DATASETS = [
    "opensporks/crunchbase",
    "calebheinzman/Crunchbase_People",
    "tor24/indian-startup-funding-2015-2024",
    "aggubandar/startup-funding-llm-data",
    "XJCEO/Bloomberg_Financial_News",
    "zeroshot/twitter-financial-news-topic",
]


def get_json(url: str) -> dict:
    with urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def inspect_dataset(repo_id: str) -> dict:
    encoded = quote(repo_id, safe="")
    result: dict = {"repo_id": repo_id}

    try:
        api = get_json(f"https://huggingface.co/api/datasets/{repo_id}")
        result["last_modified"] = api.get("lastModified")
        result["downloads"] = api.get("downloads")
        result["likes"] = api.get("likes")
        result["tags"] = api.get("tags", [])
        result["license_tags"] = [
            tag for tag in api.get("tags", []) if str(tag).startswith("license:")
        ]
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        result["api_error"] = str(exc)

    try:
        splits = get_json(f"https://datasets-server.huggingface.co/splits?dataset={encoded}")
        result["viewer_splits"] = splits.get("splits", [])
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        result["viewer_error"] = str(exc)

    return result


def main() -> int:
    inspected = [inspect_dataset(repo_id) for repo_id in DATASETS]
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(inspected, indent=2), encoding="utf-8")
    print(f"Wrote Hugging Face inspection to {OUT_PATH}")
    for item in inspected:
        license_tags = ", ".join(item.get("license_tags", [])) or "license unknown"
        split_count = len(item.get("viewer_splits", []))
        print(f"- {item['repo_id']}: {license_tags}; splits={split_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
