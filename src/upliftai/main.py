# src/upliftai/main.py
import os, sys, json, argparse
from pathlib import Path
from dotenv import load_dotenv
from upliftai.crew import UpliftCrew

def _read_text(p: str) -> str:
    return Path(p).read_text(encoding="utf-8")

def main():
    load_dotenv()

    ap = argparse.ArgumentParser(description="upliftAI: YAML-driven generator")
    ap.add_argument("--profile", required=True, help="Path to a json/jsonc profile (mounted inside container)")
    ap.add_argument("--out-base", default="/app/output", help="Base output directory")
    args = ap.parse_args()

    # inject the profile text into the task placeholders
    inputs = {"profile_text": _read_text(args.profile)}

    result = UpliftCrew().crew().kickoff(inputs=inputs)
    out_str = str(result).strip()

    # Validate strict JSON before saving
    try:
        parsed = json.loads(out_str)
    except Exception:
        print("\nModel did not return strict JSON. First 1k chars:\n")
        print(out_str[:1000])
        raise

    # put result under output/<profile-stem>/program.json
    slug = Path(args.profile).stem  # e.g., obese, fit, athlete
    out_dir = Path(args.out_base) / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "program.json"

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)

    print(f"Saved JSON -> {out_path}")

if __name__ == "__main__":
    main()
