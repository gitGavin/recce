"""Run evals against all completed Recce runs."""

import os
import sys
import json
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from judge import run_eval, print_results


def find_runs(runs_dir: str) -> list:
    """Find all completed runs that have both final.md and scout_notes.md."""
    runs = []
    if not os.path.exists(runs_dir):
        return runs
    for name in sorted(os.listdir(runs_dir)):
        run_path = os.path.join(runs_dir, name)
        final_path = os.path.join(run_path, "final.md")
        scout_path = os.path.join(run_path, "scout_notes.md")
        if os.path.isdir(run_path) and os.path.exists(final_path) and os.path.exists(scout_path):
            runs.append({
                "name": name,
                "final_path": final_path,
                "scout_path": scout_path,
            })
    return runs


def main():
    runs_dir = os.path.join(os.path.dirname(__file__), "..", "runs")
    runs = find_runs(runs_dir)

    if not runs:
        print("No completed runs found in runs/. Run recce first.")
        sys.exit(1)

    print(f"Found {len(runs)} completed runs.\n")

    all_results = {}

    for i, run in enumerate(runs):
        print(f"--- Evaluating: {run['name']} ---")

        with open(run["final_path"]) as f:
            final = f.read()
        with open(run["scout_path"]) as f:
            scout = f.read()

        results = run_eval(final, scout)
        print_results(results)
        all_results[run["name"]] = results

        # Save individual eval results
        eval_path = os.path.join(os.path.dirname(run["final_path"]), "eval_results.json")
        with open(eval_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Saved: {eval_path}")

        # Rate limit pause between runs
        if i < len(runs) - 1:
            print("\nWaiting 60s for rate limit...")
            time.sleep(60)

    # Print summary table
    print("\n")
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    criteria = ["citation_density", "recency", "coverage", "actionability", "faithfulness"]

    # Header
    header = f"{'Run':<35}"
    for c in criteria:
        header += f" {c[:8]:>8}"
    header += f" {'Total':>6}"
    print(header)
    print("-" * 70)

    # Rows
    for run_name, results in all_results.items():
        row = f"{run_name:<35}"
        passes = 0
        for c in criteria:
            status = results[c]["result"]
            icon = "✅" if status == "PASS" else "❌"
            row += f" {icon:>8}"
            if status == "PASS":
                passes += 1
        row += f" {passes}/5"
        print(row)

    # Per-criterion pass rate
    print("-" * 70)
    rate_row = f"{'Pass rate':<35}"
    for c in criteria:
        passes = sum(1 for r in all_results.values() if r[c]["result"] == "PASS")
        total = len(all_results)
        rate_row += f" {passes}/{total:>5}"
    print(rate_row)


if __name__ == "__main__":
    main()