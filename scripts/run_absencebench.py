"""Create a reproducible AbsenceBench preparation record for Shadow Seed Learning."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from shadowseed.benchmark.absencebench import build_preparation_record


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Maak een reproduceerbaar voorbereidingsrecord voor AbsenceBench."
    )
    parser.add_argument(
        "--output",
        default="runs/absencebench/preparation.json",
        help="Pad naar het JSON-bestand voor de voorbereidingsstatus.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    record = build_preparation_record()
    output_path.write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"AbsenceBench voorbereidingsrecord geschreven naar: {output_path}")
    print("Executionstatus:", record["executionstatus"])
    print("Execution-gap aanwezig:", "ja" if record["execution_gap_aanwezig"] else "nee")


if __name__ == "__main__":
    main()
