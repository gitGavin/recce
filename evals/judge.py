"""LLM-as-judge evaluator for Recce outputs."""

import os
import json
from anthropic import Anthropic

def run_eval(final_output: str, scout_notes: str) -> dict:
    """
    Evaluate a Recce final one-pager against the 5-criterion rubric.
    Returns a dict with pass/fail for each criterion and explanations.
    """
    client = Anthropic()

    system_prompt = """You are an evaluation judge for a competitive intelligence tool.

    You will receive two inputs:
    1. A final one-pager (the output being evaluated)
    2. The original scout notes (the source of truth)

    Score the one-pager on exactly 5 criteria. For each criterion, respond 
    with PASS or FAIL and a 1-2 sentence explanation.

    Criteria:

    1. CITATION DENSITY
    PASS if: ≥3 distinct sources cited, each citation maps to a specific claim.
    FAIL if: fewer than 3 citations, or citations are decorative.

    2. RECENCY
    PASS if: at least 2/3 of cited sources are from the last 12 months.
    FAIL if: majority of sources are stale without acknowledgment.

    3. COVERAGE
    PASS if: all 6 sections (Positioning, Pricing, Key Features, Differentiators, 
    Gaps/Weaknesses, PM Recommendation) are present with ≥2 sentences or an 
    explicit "No public information found."
    FAIL if: any section is missing, empty, or has only one vague sentence.

    4. ACTIONABILITY
    PASS if: PM Recommendation names a specific action with a timeframe or trigger.
    FAIL if: recommendation uses hedge language without specifics.

    5. FAITHFULNESS
    PASS if: every factual claim in the one-pager traces to the scout notes.
    FAIL if: any claim appears that is not in the scout notes.
    This is the hardest criterion. Cross-reference carefully. Check specific 
    numbers, dates, feature names, and pricing claims against the scout notes.

    You MUST respond in this exact JSON format and nothing else. No preamble, 
    no markdown backticks, just the JSON object:

    {
    "citation_density": {
        "result": "PASS" or "FAIL",
        "explanation": "..."
    },
    "recency": {
        "result": "PASS" or "FAIL",
        "explanation": "..."
    },
    "coverage": {
        "result": "PASS" or "FAIL",
        "explanation": "..."
    },
    "actionability": {
        "result": "PASS" or "FAIL",
        "explanation": "..."
    },
    "faithfulness": {
        "result": "PASS" or "FAIL",
        "explanation": "..."
    }
    }"""

    model = os.getenv("RECCE_MODEL", "claude-sonnet-4-5")

    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": f"Evaluate this one-pager against the scout notes.\n\n"
                           f"## FINAL ONE-PAGER:\n\n{final_output}\n\n"
                           f"## SCOUT NOTES:\n\n{scout_notes}",
            }
        ],
    )

    result_text = ""
    for block in response.content:
        if block.type == "text":
            result_text += block.text

    # Parse JSON response
    try:
        result = json.loads(result_text.strip())
    except json.JSONDecodeError:
        # If Claude wrapped it in backticks, strip them
        cleaned = result_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]  # remove first line
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("\n", 1)[0]  # remove last line
        result = json.loads(cleaned.strip())

    return result


def print_results(results: dict):
    """Pretty-print eval results."""
    print()
    print("=" * 50)
    print("EVAL RESULTS")
    print("=" * 50)

    pass_count = 0
    total = len(results)

    for criterion, data in results.items():
        status = data["result"]
        icon = "✅" if status == "PASS" else "❌"
        if status == "PASS":
            pass_count += 1
        name = criterion.replace("_", " ").upper()
        print(f"\n{icon} {name}: {status}")
        print(f"   {data['explanation']}")

    print()
    print(f"Score: {pass_count}/{total} passed")
    print("=" * 50)