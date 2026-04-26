"""Run Recce evals through LangSmith's evaluation framework."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from langsmith import Client, evaluate
from judge import run_eval

client = Client()


def recce_eval_target(inputs: dict) -> dict:
    """The 'target' function LangSmith calls for each example.
    Since we already have the outputs, just pass them through."""
    return {
        "final_output": inputs["final_output"],
        "scout_notes": inputs["scout_notes"],
        "run_name": inputs["run_name"],
    }


def citation_density(run, example) -> dict:
    """Evaluate citation density."""
    results = _get_eval_results(run)
    passed = results["citation_density"]["result"] == "PASS"
    return {
        "key": "citation_density",
        "score": 1 if passed else 0,
        "comment": results["citation_density"]["explanation"],
    }


def recency(run, example) -> dict:
    """Evaluate source recency."""
    results = _get_eval_results(run)
    passed = results["recency"]["result"] == "PASS"
    return {
        "key": "recency",
        "score": 1 if passed else 0,
        "comment": results["recency"]["explanation"],
    }


def coverage(run, example) -> dict:
    """Evaluate section coverage."""
    results = _get_eval_results(run)
    passed = results["coverage"]["result"] == "PASS"
    return {
        "key": "coverage",
        "score": 1 if passed else 0,
        "comment": results["coverage"]["explanation"],
    }


def actionability(run, example) -> dict:
    """Evaluate recommendation actionability."""
    results = _get_eval_results(run)
    passed = results["actionability"]["result"] == "PASS"
    return {
        "key": "actionability",
        "score": 1 if passed else 0,
        "comment": results["actionability"]["explanation"],
    }


def faithfulness(run, example) -> dict:
    """Evaluate faithfulness to scout notes."""
    results = _get_eval_results(run)
    passed = results["faithfulness"]["result"] == "PASS"
    return {
        "key": "faithfulness",
        "score": 1 if passed else 0,
        "comment": results["faithfulness"]["explanation"],
    }


# Cache eval results so we only call the judge once per example
_eval_cache = {}

def _get_eval_results(run) -> dict:
    """Run the judge once per example and cache the results."""
    run_id = str(run.id)
    if run_id not in _eval_cache:
        outputs = run.outputs
        _eval_cache[run_id] = run_eval(
            outputs["final_output"],
            outputs["scout_notes"],
        )
    return _eval_cache[run_id]


def main():
    dataset_name = "Recce Eval Dataset"

    print(f"Running evals against: {dataset_name}")
    print("This will take a few minutes (rate limits between judge calls)...\n")

    results = evaluate(
        recce_eval_target,
        data=dataset_name,
        evaluators=[
            citation_density,
            recency,
            coverage,
            actionability,
            faithfulness,
        ],
        experiment_prefix="recce-eval",
    )

    print("\nDone! View results at https://smith.langchain.com")
    print("Go to Datasets > Recce Eval Dataset > Experiments")


if __name__ == "__main__":
    main()
