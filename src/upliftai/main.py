# src/upliftai/main.py
import os, sys, json
from dotenv import load_dotenv
from upliftai.crew import UpliftCrew

def main():
    load_dotenv()

    result = UpliftCrew().crew().kickoff()
    out_str = str(result).strip()

    # Validate strict JSON before saving
    try:
        parsed = json.loads(out_str)
    except Exception:
        print("\nModel did not return strict JSON. First 1k chars:\n")
        print(out_str[:1000])
        raise

    out_path = "/app/output/program.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)

    print(f"Saved JSON -> {out_path}")

if __name__ == "__main__":
    main()
