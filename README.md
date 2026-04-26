# Recce

**A multi-agent competitive intelligence tool for product managers.**
🎥 [3-min walkthrough and demo](https://www.loom.com/share/fc16361d6da546a19e2f982822ff99cb)

Give it a product name. Get back a PM-ready one-pager in under 5 minutes: positioning, pricing, features, gaps, and a recommendation — with citations.

```bash
$ python -m recce.cli "Linear Agents"
=== Recce: Linear Agents ===
Scout gathering sources...
Writer drafting one-pager...
Critic reviewing draft...
Reviser incorporating feedback...
=== Done. Output in runs/linear-agents-2026-04-20/ ===
```

---

## Why this exists

PMs burn 2–4 hours every time an exec asks "what is X doing in space Y?" The work is not hard, it is tedious: open tabs, skim, copy-paste, structure, cite, recommend. Existing tools either produce prose blobs with no structure, rely on stale training data, or cost thousands per seat.

Recce is the tool I wanted for my own job. It is built around one opinion: **a single LLM prompt cannot do competitive intelligence well, but a small number of specialized agents in a chain can.** One agent sources. One writes. One critiques. One revises. The PM reads the final output and can trace every claim back to a source.

This is a portfolio project. It is also a tool I use on real work. If those two things stop being true at the same time, I have lost the plot.

## Status

🚀 **Week 3 of 6.** Full 4-agent chain live — scout, writer, critic, reviser. See [PRD.md](./PRD.md) for the design, [BUILD_LOG.md](./BUILD_LOG.md) for what broke along the way, and `examples/` for sample output.

## How it works

```
  [product name]
        │
        ▼
  ┌───────────┐
  │   SCOUT   │  Sonnet + web_search
  │           │  Gathers 5–15 recent public sources,
  │           │  extracts claims, discards low-quality
  └─────┬─────┘
        │ structured notes
        ▼
  ┌───────────┐
  │  WRITER   │  Sonnet
  │           │  Drafts the one-pager against a fixed
  │           │  section template and citation rules
  └─────┬─────┘
        │ draft + citations
        ▼
  ┌───────────┐
  │  CRITIC   │  Sonnet
  │           │  Finds specific weaknesses — must identify
  │           │  ≥2 with actionable fixes. No scores, no vibes.
  └─────┬─────┘
        │ numbered list of weaknesses + fixes
        ▼
  ┌───────────┐
  │  REVISER  │  Sonnet
  │           │  Addresses each weakness. Cannot introduce
  │           │  new claims not in scout notes.
  └─────┬─────┘
        │
        ▼
  [ final markdown one-pager ]
```

This is a **prompt chaining** pattern ([Anthropic's taxonomy](https://www.anthropic.com/research/building-effective-agents)). I chose it over evaluator-optimizer because the main failure mode — "plausible but shallow" output — is fixable in a single critique-and-revise pass. Looping adds cost and latency with diminishing returns. See [PRD.md](./PRD.md#why-prompt-chaining-not-evaluator-optimizer) for the full rationale.

## Design decisions

The interesting parts of this project are the choices, not the code. The full decision table is in [PRD.md](./PRD.md#design-decisions--tradeoffs), but the headlines:

- **Prompt chaining over evaluator-optimizer.** One critique-and-revise pass catches the failure mode cheaply. Upgradeable to a loop if evals justify it.
- **Raw SDK, no framework.** I want to understand the orchestration, not hide it behind LangGraph.
- **Sonnet everywhere, configurable via env var.** Cost-efficient, quality sufficient. Can A/B test with Opus during eval week.
- **CLI, not a web UI.** 1/10 the effort, loses almost nothing. A Loom handles "how does it feel to use."
- **Critic outputs a numbered weakness list, not a score.** Specific weaknesses give the reviser actionable instructions. Scores are ambiguous.

## Running it

```bash
# Clone and set up
git clone https://github.com/gitGavin/recce.git
cd recce
python -m venv .venv
source .venv/bin/activate
pip install anthropic

# Set your API key
export ANTHROPIC_API_KEY="your-key"
export PYTHONPATH=src

# Run
python -m recce.cli "Product Name"

# Output appears in runs/{product-slug}-{date}/
# Files: scout_notes.md, draft.md, critique.md, final.md
```

Each run makes 4 API calls with pauses between them to respect rate limits. Expect ~3-5 minutes per run.

## Example output

See `examples/linear-agents/` for a complete run with all 4 intermediate artifacts:
- `scout_notes.md` — raw sources gathered by the scout
- `draft.md` — first draft from the writer
- `critique.md` — weaknesses identified by the critic
- `final.md` — revised one-pager addressing the critique

## Eval Results

Ran against 4 products using LLM-as-judge (Sonnet). Binary pass/fail 
on 5 criteria. Full rubric in `evals/rubric.md`.

| Run | Citations | Recency | Coverage | Actionability | Faithfulness | Score |
|-----|-----------|---------|----------|---------------|--------------|-------|
| Claude Cowork | ✅ | ✅ | ✅ | ✅ | ❌ | 4/5 |
| Snowflake Cortex | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 |
| Tableau Pulse | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 |
| v0 | ✅ | ✅ | ✅ | ✅ | ❌ | 4/5 |
| **Pass rate** | 4/4 | 4/4 | 4/4 | 4/4 | 2/4 | |

### Known weaknesses

**Faithfulness is the weakest criterion (50% pass rate).** Both failures 
share the same pattern: the reviser subtly restructures or consolidates 
claims in ways that shift attribution or merge separate facts. This is not 
hallucination from nothing — it is lossy compression of real information. 
The fix would be stricter reviser prompt constraints on paraphrasing, 
or a post-revision faithfulness check before output.

### Judge validation

I manually scored the Claude Cowork run against all 5 criteria and compared 
to the LLM judge. Agreement: 4/5. For the v0 run, the judge flagged a 
faithfulness failure on the Free tier "$5 monthly credits" claim, but manual 
review confirms this fact appears in the scout notes — the model consolidated 
two separate sentences into one, which the judge misread as fabrication. 
Actual faithfulness pass rate is likely 3/4, not 2/4.

This highlights a known limitation of LLM-as-judge: it can be overly strict 
when source information is spread across multiple sentences and the output 
consolidates it. A more robust eval would check semantic equivalence rather 
than near-exact matching.

## Observability & Evaluation Platform

Added [LangSmith](https://smith.langchain.com) for two purposes:

**Tracing.** Every agent call is logged with full prompt, response, token count, and latency. Each Recce run appears as a nested trace — scout → writer → critic → reviser — enabling prompt-level debugging without print statements.

**Evaluation.** The same 5-criterion rubric from the repo-based eval suite also runs through LangSmith's evaluation framework. This provides a visual dashboard for comparing eval results across experiments — useful when iterating on prompts and measuring whether changes improve or regress quality.

The repo-based eval suite (`evals/run_evals.py`) remains the portable, transparent version anyone can run. LangSmith adds the operational layer for ongoing development.

```bash
# Run repo-based evals (no LangSmith needed)
python evals/run_evals.py

# Run LangSmith evals (requires LANGSMITH_API_KEY)
python evals/create_dataset.py    # upload runs as dataset
python evals/langsmith_eval.py    # run judge against dataset
```


## What I learned building this

See [WRITEUP.md](./WRITEUP.md) (Week 5) for the full teardown. See [BUILD_LOG.md](./BUILD_LOG.md) for the running record of decisions and debugging.

## What this is not

- Not a chatbot. One input, one output, done.
- Not a framework or a library. It is one tool, for one job.
- Not a SaaS. There is no backend, no auth, no database.
- Not a finished product. It is a portfolio artifact that happens to be useful to one PM (me).

## About

Built by [Gavin Jin](https://www.linkedin.com/in/gavinjin/) as part of a 6-week sprint to sharpen my AI PM craft outside my day job. If you are hiring AI PMs and want to talk about any of the decisions in the PRD, my inbox is open.
