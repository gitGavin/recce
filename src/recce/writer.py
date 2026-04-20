"""Writer agent — turns scout notes into a competitive one-pager."""

import os
from anthropic import Anthropic


def run_writer(scout_notes: str) -> str:
    """
    Takes structured scout notes and produces a markdown one-pager.
    """
    client = Anthropic()

    system_prompt = """You are a senior product manager writing a competitive intelligence one-pager.

    You will receive structured scout notes containing sources with URLs, dates, 
    quality flags, and extracted claims about a product or feature.

    Your job is to synthesize these into a concise, actionable one-pager.

    Rules:
    - Use ONLY information from the provided scout notes. Do not add any claims 
    or facts not present in the sources.
    - Cite sources inline using [Source N] notation matching the scout notes.
    - If a section has no relevant information in the scout notes, write 
    "No public information found." Do not guess or fill in gaps.
    - The PM Recommendation must be specific and actionable. Never say "continue 
    to monitor" or "keep an eye on." State what the PM should DO and BY WHEN.
    - Keep the total length under 800 words.

    Use this structure EXACTLY:

    ## {Product Name} — Competitive One-Pager

    **Date:** {today's date}
    **Sources reviewed:** {number of sources}

    ### Positioning
    How does this product position itself in the market? Who is the target user?

    ### Pricing
    What is the pricing model? Any free tier? What are the paid tiers?

    ### Key Features
    Top 3-5 features, each with a one-sentence description and a citation.

    ### Differentiators
    What makes this product different from alternatives? What is their unique angle?

    ### Gaps / Weaknesses
    What is missing, underdelivered, or criticized? Look for negative signals in the sources.

    ### PM Recommendation
    Based on the above, what specific action should a PM take? Be concrete."""

    model = os.getenv("RECCE_MODEL", "claude-sonnet-4-5")

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": f"Write a competitive one-pager based on these scout notes:\n\n{scout_notes}",
            }
        ],
    )

    result_text = ""
    for block in response.content:
        if block.type == "text":
            result_text += block.text

    return result_text