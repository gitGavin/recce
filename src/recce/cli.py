"""Recce CLI — run competitive intelligence agents from the terminal."""

import os
import sys
import re
import time
from datetime import date

from recce.scout import run_scout
from recce.writer import run_writer
from recce.critic import run_critic
from recce.reviser import run_reviser

from langsmith import traceable


def slugify(text: str) -> str:
    """Turn a product name into a filesystem-safe slug."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

def call_with_retry(fn, *args, max_retries=3):
    """Call a function, retrying on rate limit errors with increasing waits."""
    for attempt in range(max_retries):
        try:
            return fn(*args)
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e):
                wait = 60 * (attempt + 1)  # 60s, 120s, 180s
                print(f"  Rate limited. Waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                raise
    print("  Failed after max retries.")
    sys.exit(1)

@traceable(name="Recce Pipeline")
def main():
    if len(sys.argv) < 2:
        print("Usage: python -m recce.cli 'Product Name'")
        sys.exit(1)

    product = sys.argv[1]
    slug = slugify(product)
    run_dir = f"runs/{slug}-{date.today()}"
    os.makedirs(run_dir, exist_ok=True)

    print(f"=== Recce: {product} ===")
    print()

    # Step 1: Scout
    print("Scout gathering sources...")
    scout_notes = call_with_retry(run_scout, product)
    scout_path = f"{run_dir}/scout_notes.md"
    with open(scout_path, "w") as f:
        f.write(scout_notes)
    print(f"  Saved: {scout_path}")

    # Step 2: Writer
    print("Writer drafting one-pager...")
    draft = call_with_retry(run_writer, scout_notes)
    draft_path = f"{run_dir}/draft.md"
    with open(draft_path, "w") as f:
        f.write(draft)
    print(f"  Saved: {draft_path}")

    # Step 3: Critic
    print("Critic reviewing draft...")
    critique = call_with_retry(run_critic, draft, scout_notes)
    critique_path = f"{run_dir}/critique.md"
    with open(critique_path, "w") as f:
        f.write(critique)
    print(f"  Saved: {critique_path}")

    # Step 4: Reviser
    print("Reviser incorporating feedback...")
    final = call_with_retry(run_reviser, draft, critique, scout_notes)
    final_path = f"{run_dir}/final.md"
    with open(final_path, "w") as f:
        f.write(final)
    print(f"  Saved: {final_path}")

    # Done
    print()
    print(f"=== Done. Output in {run_dir}/ ===")
    print()
    print(final)


if __name__ == "__main__":
    main()