# Kiro

**A multi-agent competitive intelligence tool for product managers.**

Give it a product name. Get back a PM-ready one-pager in under 5 minutes: positioning, pricing, features, gaps, and a recommendation — with citations.

```bash
$ kiro "Linear Agents"
→ Scout gathering sources... (12 sources found)
→ Writer drafting one-pager...
→ Critic reviewing against rubric... (score: 87/100)
→ Output: ./runs/linear-agents-2026-04-13.md
```

---

## Why this exists

PMs burn 2–4 hours every time an exec asks "what is X doing in space Y?" The work is not hard, it is tedious: open tabs, skim, copy-paste, structure, cite, recommend. Existing tools either produce prose blobs with no structure, rely on stale training data, or cost thousands per seat.

Kiro is the tool I wanted for my own job. It is built around one opinion: **a single LLM prompt cannot do competitive intelligence well, but a small number of specialized agents can.** One agent sources. One writes. One critiques. The PM reads the final output and can trace every claim back to a source.

This is a portfolio project. It is also a tool I use on real work. If those two things stop being true at the same time, I have lost the plot.

## Status

🚧 **Week 1 of 6.** PRD locked, scaffold up, first Claude call working. See [PRD.md](./PRD.md) for the full design and [BUILD_LOG.md](./BUILD_LOG.md) for what broke along the way.

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
  │  WRITER   │  Opus
  │           │  Drafts the one-pager against a fixed
  │           │  section template and citation rules
  └─────┬─────┘
        │ draft + citations
        ▼
  ┌───────────┐
  │  CRITIC   │  Sonnet
  │           │  Scores against a 5-criterion rubric,
  │           │  must find ≥2 weaknesses before approving
  └─────┬─────┘
        │ (revise once if score < 80)
        ▼
  [ final markdown + JSON ]
```

This is an **evaluator-optimizer** pattern ([Anthropic's taxonomy](https://www.anthropic.com/engineering/building-effective-agents)). I picked it over alternatives (single prompt, parallel agents, hierarchical orchestrator) because the real failure mode of LLM-generated strategy docs is "plausible but weak" — a critic that must find weaknesses catches that failure mode cheaply.

## Design decisions

The interesting parts of this project are the choices, not the code. The full decision table is in [PRD.md](./PRD.md#design-decisions--tradeoffs), but the headlines:

- **Raw SDK, no framework.** I want to understand the orchestration for interviews, not hide it behind LangGraph.
- **Model routing.** Opus on the writer (hard synthesis), Sonnet on the scout and critic (structured work). Revisited after evals.
- **Evaluator-optimizer over parallel or hierarchical.** Matches the actual failure mode and is cheap.
- **CLI, not a web UI.** 1/10 the effort, loses almost nothing. A Loom handles "how does it feel to use."

## Evals

Coming in Week 4. The planned rubric (see `evals/rubric.md` when it exists):

1. **Citation density** — ≥3 distinct sources, each linked to a specific claim.
2. **Recency** — most cited sources ≤12 months old, with exceptions flagged.
3. **Coverage** — all 6 required sections present and non-empty.
4. **Actionability** — recommendation is specific and testable, not "monitor the space."
5. **Adversarial robustness** — on known-bad drafts, critic catches ≥1 real flaw.

Results will be published in the README, including the ones Kiro fails. Honest limitations are more credible than hidden ones.

## What I learned building this

See [WRITEUP.md](./WRITEUP.md) (Week 5) for the full teardown. Short version coming there covers: why the naive version failed, what the critic pattern actually changed in output quality, where evals surprised me, and what I would do with another month.

## What this is not

- Not a chatbot. One input, one output, done.
- Not a framework or a library. It is one tool, for one job.
- Not a SaaS. There is no backend, no auth, no database.
- Not a finished product. It is a portfolio artifact that happens to be useful to one PM (me).

## Running it

```bash
# Week 2, not yet. Check back end of Week 2.
```

## About

Built by [Gavin Jin](https://www.linkedin.com/in/...) as part of a 6-week sprint to sharpen my AI PM craft outside my day job leading [Project ARIA](https://...) at Cisco. If you are hiring AI PMs and want to talk about any of the decisions in the PRD, my inbox is open.
