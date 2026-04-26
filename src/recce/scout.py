"""Scout agent — gathers competitive intelligence sources for a given product."""

import os
from anthropic import Anthropic
from langsmith.wrappers import wrap_anthropic


def run_scout(product_name: str) -> str:
    """
    Takes a product name, searches the web for recent competitive intel,
    and returns structured notes about what it found.
    """
    client = wrap_anthropic(Anthropic())

    system_prompt = """You are a competitive intelligence researcher working for a product manager.

    Your job is to gather recent, factual information about a specific product or feature.

    Instructions:
    - Search for the product using multiple specific queries (e.g., the product name, 
    the product name + "pricing", the product name + "review", the product name + 
    "changelog" or "release notes").
    - Find 5-15 recent, credible sources. Prioritize: official product pages, company 
    blogs, reputable tech press (TechCrunch, The Verge, etc.), analyst reports. 
    Deprioritize: forums, social media, SEO spam.
    - Discard any source older than 12 months unless it is foundational (e.g., the 
    original product launch announcement).
    - For EACH source, extract:
    - URL
    - Title
    - Publication date (or "undated" if not available)
    - 2-3 key claims or facts from that source
    - A quality flag: HIGH (official source or reputable press), MEDIUM (blog, 
        industry site), or LOW (forum, social, unverified)

    Output format — use this EXACTLY:

    ## Scout Notes: {product_name}
    ### Sources

    **Source 1**
    - URL: {url}
    - Title: {title}
    - Date: {date}
    - Quality: {HIGH/MEDIUM/LOW}
    - Key claims:
    - {claim 1}
    - {claim 2}

    **Source 2**
    ...

    ### Summary
    Write 2-3 sentences summarizing the overall competitive picture based on 
    the sources above. Note any gaps — topics where you could not find reliable 
    information (e.g., "No pricing information found in public sources.")."""

    model = os.getenv("RECCE_MODEL", "claude-sonnet-4-5")

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=system_prompt,
        tools=[
            {
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 10,
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"Research this product: {product_name}",
            }
        ],
    )

    result_text = ""
    for block in response.content:
        if block.type == "text":
            result_text += block.text

    return result_text