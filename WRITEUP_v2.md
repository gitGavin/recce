# Building Recce: What I Learned Shipping a Multi-Agent AI Tool

🎥 [3-min walkthrough video](YOUR-LOOM-LINK-HERE)

---

## The Problem

Every PM I know does competitive intelligence the same way: open a dozen browser tabs, skim articles and pricing pages, copy-paste into a Google Doc, try to organize it into something an exec can read, realize half the sources are stale, and start over. It takes 2–4 hours to produce a one-pager that's mediocre at best.

The frustrating part isn't the reading — it's the structuring. You need to hold 10 sources in your head, cross-reference claims, identify gaps, and write a recommendation that's specific enough to be useful. By the time you're done, you've spent a senior PM's afternoon on work that feels like it should take 15 minutes.

I've tried the obvious solution: paste everything into Claude or ChatGPT and ask for a summary. The output reads well. It also cites sources that don't exist, invents plausible-sounding pricing, and recommends "continue to monitor the competitive landscape" — which is the PM equivalent of saying nothing. A single LLM prompt can't do this job well. I wanted to understand why, and whether a different architecture could.

## Why a Single Prompt Fails

Before building Recce, I tested the naive approach: one prompt, one call, one output. The results were fluent and completely unreliable. Three specific failure modes:

**Hallucinated sources.** Without a dedicated research step, the model fills gaps with plausible-sounding citations. It will confidently cite a TechCrunch article that doesn't exist. A reader who doesn't verify every link (which is most readers) will trust the output and make decisions based on invented evidence.

**Vague recommendations.** A single prompt optimizes for sounding comprehensive, not for being useful. The recommendation section defaults to safe, hedge-heavy language — "consider evaluating," "monitor for developments," "assess fit for your use case." None of these tell a PM what to actually do.

**No auditability.** When the output is wrong, you can't tell which part of the process broke. Was the source bad? Was the synthesis wrong? Was the recommendation disconnected from the evidence? With a single prompt, the entire pipeline is a black box.

Recce's architecture exists to solve these three problems specifically.

## The Design

Recce is a 4-agent prompt chain: scout → writer → critic → reviser. Each agent has a single job, a defined input/output contract, and produces a saved artifact.

**The scout** searches the web for recent public sources about a product, extracts key claims from each, and tags every source with a quality flag (HIGH/MEDIUM/LOW) and a date. This separation forces the system to gather evidence before synthesizing — which is the single most effective defense against hallucination.

**The writer** takes the scout notes and produces a one-pager following a fixed section template: Positioning, Pricing, Key Features, Differentiators, Gaps/Weaknesses, and PM Recommendation. It can only use information from the scout notes. This constraint is explicit in the prompt.

**The critic** reviews the draft against the scout notes and produces a numbered list of specific, actionable weaknesses. Not a score. Not vibes. Not a compliment sandwich. Each weakness names the section, states what's wrong, and states what the fix looks like. The critic must find at least 2 weaknesses — an empty list is structurally impossible.

**The reviser** takes the draft plus the critic's feedback and produces the final one-pager, addressing each weakness. It cannot introduce new claims not in the scout notes.

I chose prompt chaining over the evaluator-optimizer pattern (where the critic loops until a quality threshold is met) because the failure mode I'm solving — "plausible but shallow" — is fixable in one pass. Looping adds cost, latency, and debugging complexity with diminishing returns. If my eval data had shown otherwise, I would have upgraded. It didn't.

I used the Anthropic SDK directly, with no framework (no LangChain, no CrewAI, no LangGraph). For a portfolio project where the goal is to demonstrate understanding, frameworks hide the very things I want to show. Every design decision in Recce — model routing, prompt structure, agent boundaries, error handling — is visible in the code because there's nothing abstracting it away.

## What the Evals Caught

I built a 5-criterion eval suite using LLM-as-judge: citation density, recency, coverage, actionability, and faithfulness. Each criterion is binary pass/fail — no 1–5 scales. I ran it against 4 products.

Results:

| Criterion | Pass Rate | Notes |
|-----------|-----------|-------|
| Citation density | 4/4 | Consistently cites 10+ sources per one-pager |
| Recency | 4/4 | Scout's date filtering works |
| Coverage | 4/4 | All 6 sections substantive in every run |
| Actionability | 4/4 | Critic-reviser chain eliminated hedge language |
| Faithfulness | 2/4 | The interesting failure — see below |

**Faithfulness was the weakest criterion, and the failure mode was surprising.** I expected outright hallucination — made-up facts with no source. Instead, both failures were *lossy compression*: the reviser consolidated real information from the scout notes in ways that subtly shifted attribution. In one run, a third-party blogger's characterization was attributed to the company itself. In another, two separate facts about a pricing tier were merged into one sentence that slightly misrepresented the source structure.

This distinction matters because the fix is different. Hallucination requires guardrails or retrieval constraints. Lossy compression requires stricter paraphrasing rules in the reviser prompt — specifically, preserving attribution when consolidating claims from different sources.

**The judge itself had a false positive.** Manual validation of one run revealed that the judge flagged a consolidation as fabrication when the information was actually present in the scout notes, just spread across two sentences. This is a known limitation of LLM-as-judge — it struggles with semantic equivalence when source information is distributed. Catching this is exactly why you validate automated evals against human judgment. The actual faithfulness pass rate is likely 3/4, not 2/4.

## What I'd Do With Another Month

Three things, ranked by impact:

**1. Fix the faithfulness failure.** The reviser prompt needs a stronger constraint on consolidation: "When combining information from multiple sentences in the scout notes, preserve the original attribution. Do not merge claims from different sources into a single sentence." I'd re-run evals after the prompt change and publish the before/after comparison. If the prompt fix alone isn't sufficient, I'd consider adding a lightweight post-revision faithfulness checker — effectively a fifth agent — but I'd want data showing the prompt fix alone doesn't work before adding that cost and latency.

**2. Cache scout results.** The scout's web search is the most expensive and slowest step. For products that don't change daily, caching scout results for 24–48 hours would cut repeat-run cost by 60% and latency by half. This is a straightforward engineering improvement with clear ROI.

**3. Add a simple web interface.** Not because the CLI is bad — for me, it's the right tool. But if I were shipping this to a team, a Streamlit wrapper that shows scout notes, draft, critique, and final side by side would make the chain's value visible to non-technical PMs. The architecture already supports this — every intermediate artifact is saved as a file.

## What I Learned About Being an AI PM

**Evals are the product, not the polish.** I expected evals to be a validation step at the end — something you bolt on to confirm the system works. Instead, the eval results were the most important artifact in the entire project. They told me where the system actually fails (faithfulness, not coverage), what kind of failure it is (lossy compression, not hallucination), and what to fix next. Without evals, I would have kept tweaking prompts based on vibes. With evals, I had data.

**The prompt is not the product.** Early in the build, I spent too long perfecting the writer prompt before I had the critic in place. The quality improvement from adding a critic-reviser pass dwarfed anything I could achieve by rewriting the writer prompt alone. The architecture — how agents are composed, what contracts they follow, how information flows between them — matters more than any individual prompt.

**Context engineering is a real discipline.** The shift from "prompt engineering" to "context engineering" isn't just vocabulary — it's a fundamentally different design problem. The scout notes are not a prompt; they are context that the writer, critic, and reviser all consume differently. Deciding what information to include, exclude, and structure in that context determined output quality more than the instructions in any individual prompt.

**Shipping beats studying.** I read the Anthropic "Building Effective Agents" post in Week 1 and understood the five workflow patterns intellectually. By Week 3, after actually building a prompt chain and hitting real problems — rate limits, lossy compression, critics that rubber-stamp — I understood them practically. The gap between those two kinds of understanding is enormous, and it only closes by building.

---

*Built by Gavin Jin as part of a 6-week sprint to sharpen my AI PM craft outside my day job. Code, eval results, and build log at [github.com/gitGavin/recce](https://github.com/gitGavin/recce). If you're hiring AI PMs, my inbox is open.*
