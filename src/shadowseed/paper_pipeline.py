import json
import re
from pathlib import Path

OUTPUT_DIR = Path("results/paper_ingest")


def simple_claim_split(text: str):
    # naive sentence split
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if len(s.strip()) > 40]


def claim_to_seed(claim: str):
    # extremely naive heuristic
    return {
        "seed_text": claim,
        "status": "candidate",
        "atomic": len(claim.split(",")) < 2,
    }


def run_pipeline(input_dir: str = "data/papers"):
    input_path = Path(input_dir)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for file in input_path.glob("*.txt"):
        text = file.read_text(encoding="utf-8")
        claims = simple_claim_split(text)

        seeds = [claim_to_seed(c) for c in claims]

        scenarios = [
            {
                "question": f"What is missing or unclear in: {c[:80]}",
                "expected_additions": ["clarification", "context", "validation"],
            }
            for c in claims[:5]
        ]

        out_dir = OUTPUT_DIR / file.stem
        out_dir.mkdir(exist_ok=True)

        (out_dir / "claims.json").write_text(json.dumps(claims, indent=2), encoding="utf-8")
        (out_dir / "seeds.json").write_text(json.dumps(seeds, indent=2), encoding="utf-8")
        (out_dir / "scenarios.json").write_text(json.dumps(scenarios, indent=2), encoding="utf-8")


if __name__ == "__main__":
    run_pipeline()
