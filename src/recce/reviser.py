"""Reviser agent — incorporates critic feedback into the final one-pager."""

import os
from anthropic import Anthropic
from langsmith.wrappers import wrap_anthropic


def run_reviser(draft: str, critique: str, scout_notes: str) -> str:
    """
    Takes the draft, the critic's feedback, and the original scout notes.
    Returns a revised one-pager that addresses all weaknesses.
    """
    client = wrap_anthropic(Anthropic())

    system_prompt = """You are a senior PM revising a competitive intelligence one-pager.

    You will receive three inputs:
    1. The original draft one-pager
    2. A critic's review listing specific weaknesses and fixes
    3. The original scout notes (sources)

    Your job is to produce a revised one-pager that addresses EVERY weakness 
    the critic identified.

    Rules:
    - Address each numbered weakness from the critic's review. Do not skip any.
    - Do NOT introduce new claims, facts, or data that are not in the scout notes. 
    You can restructure, reword, and fill gaps from scout notes, but you cannot 
    invent information.
    - Keep the same section structure as the original draft.
    - Keep the total length under 800 words.
    - If the critic says a section needs more content but the scout notes have 
    nothing relevant, write "No public information found" for that section.

    Output the revised one-pager in markdown. Do not include commentary about 
    what you changed — just output the final document."""

    model = os.getenv("RECCE_MODEL", "claude-sonnet-4-5")

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": f"Revise this draft based on the critic's feedback.\n\n"
                           f"## DRAFT:\n\n{draft}\n\n"
                           f"## CRITIC'S FEEDBACK:\n\n{critique}\n\n"
                           f"## SCOUT NOTES (source of truth):\n\n{scout_notes}",
            }
        ],
    )

    result_text = ""
    for block in response.content:
        if block.type == "text":
            result_text += block.text

    return result_text