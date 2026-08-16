from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import fields
from pathlib import Path

from .extractor import Job, SelectorConfig, extract_jobs


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract jobs from an authorized local HTML file")
    parser.add_argument("--html", required=True, type=Path)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = _arguments()
    config = SelectorConfig(**json.loads(args.config.read_text(encoding="utf-8")))
    result = extract_jobs(args.html.read_text(encoding="utf-8"), args.base_url, config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.suffix.lower() == ".csv":
        with args.output.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=[field.name for field in fields(Job)])
            writer.writeheader()
            writer.writerows(job.to_dict() for job in result.jobs)
    else:
        args.output.write_text(json.dumps([job.to_dict() for job in result.jobs], indent=2), encoding="utf-8")
    for warning in result.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    print(f"extracted {len(result.jobs)} jobs to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
