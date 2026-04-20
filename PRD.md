# PRD: Recce — Competitive Intelligence Agent for PMs

**Author:** Gavin Jin
**Status:** v0.2 — revised after Week 1 reading
**Last updated:** Week 1

---

## Changelog

- **v0.2:** Changed agent pattern from evaluator-optimizer to prompt chaining based on Week 1 reading (Anthropic "Building Effective Agents"). Standardized on Sonnet for all agents with model as a config variable. Removed JSON output from scope — markdown only for v1–v2.
- **v0.1:** Initial draft.

---

## TL;DR

Recce is a multi-agent system that turns a product name into a PM-ready competitive one-pager in under 5 minutes. Four agents run in a linear chain: a scout gathers recent public sources, a writer drafts a structured teardown, a critic identifies specific weaknesses, and a reviser produces the final output incorporating the critic's feedback.

It is built to be used by me (a working PM) on real competitive intelligence tasks, not as a demo. If it is not useful to me by the end of Week 2, the project has failed its most important test.

## Problem

PMs regularly need to answer: *"What is company X doing in space Y, and what does it mean for us?"* The current workflow is:

1. Open 10 browser tabs, search for recent news, blog posts, pricing pages, changelogs.
2. Skim, copy-paste into a doc, try to structure it.
3. Write a one-pager with positioning, pricing, feature gaps, and a recommendation.
4. Realize half the sources are stale or contradictory. Start over.

This takes 2–4 hours for a mediocre result. The bottleneck is not reading speed — it is the structuring and the tradeoff between breadth (cover everything) and depth (actually synthesize).

Existing tools either fail at structure (general chatbots return prose blobs with no rubric), fail at recency (training-data answers), or fail at cost/control (enterprise CI platforms are $$$ and opaque).

## Why agents, not a single prompt

A single-shot prompt can produce a one-pager, but fails on three things Recce needs:

1. **Sourcing discipline.** A scout agent with web search, run separately from the writer, forces the system to collect evidence before it synthesizes — which catches hallucinations the writer would otherwise confabulate.
2. **Structured critique.** A critic agent that identifies specific, actionable weaknesses (not vibes, not a score) catches the "sounds good, says nothing" failure mode that is the #1 problem with LLM-generated strategy docs.
3. **Auditability.** Separate agents produce separate artifacts (scout notes, draft, critique, final). A PM reading the output can trace *why* a claim appears, not just *that* it appears.

## Why prompt chaining, not evaluator-optimizer

The Anthropic "Building Effective Agents" taxonomy describes five workflow patterns. The two most relevant to Recce are:

- **Prompt chaining:** a linear pipeline where each step passes a well-defined artifact to the next. No loops.
- **Evaluator-optimizer:** one agent generates, another evaluates, and the process loops until a quality threshold is met.

I chose **prompt chaining** (scout → writer → critic → reviser) because:

1. **The failure mode is fixable in one pass.** The main risk is "plausible but shallow" output. A single critique-and-revise pass catches this. Looping adds cost and latency with diminishing returns — the marginal quality gain from a second critique pass is small relative to the marginal cost.
2. **Predictable cost and latency.** Four sequential calls with known token budgets. No risk of runaway loops or ballooning API costs during development.
3. **Debuggable.** Each step produces a saved artifact. When something breaks, I know which step broke it by inspecting the intermediate outputs.
4. **Upgradeable.** If Week 4 evals show that one revision pass is insufficient, I can upgrade the critic → reviser step to a loop without rewriting the rest of the pipeline. Design for chaining now, leave the door open for evaluator-optimizer later.

## Agent chain and contracts

```
  [product name]
        │
        ▼
  ┌───────────┐
  │   SCOUT   │  Sonnet + web_search tool
  │           │  Input: product name (string)
  │           │  Output: structured notes with ≤15 sources,
  │           │  each tagged with: URL, title, date, 
  │           │  key claims extracted, source quality flag
  └─────┬─────┘
        │ scout_notes (structured text)
        ▼
  ┌───────────┐
  │  WRITER   │  Sonnet
  │           │  Input: scout_notes
  │           │  Output: markdown one-pager following the
  │           │  section template, with inline citations
  │           │  referencing scout sources
  └─────┬─────┘
        │ draft (markdown)
        ▼
  ┌───────────┐
  │  CRITIC   │  Sonnet
  │           │  Input: draft + scout_notes (for citation checking)
  │           │  Output: a numbered list of specific, actionable
  │           │  weaknesses. Must identify ≥2. Each weakness
  │           │  names the section, states what is wrong, and
  │           │  states what a fix looks like. No scores, no
  │           │  vibes, no "overall good job."
  └─────┬─────┘
        │ critique (structured list of weaknesses)
        ▼
  ┌───────────┐
  │  REVISER  │  Sonnet
  │           │  Input: draft + critique
  │           │  Output: final markdown one-pager with all
  │           │  weaknesses addressed. Must not introduce
  │           │  new claims not supported by scout_notes.
  └─────┬─────┘
        │
        ▼
  [ final markdown one-pager ]
```

### Critic → Reviser contract (critical design detail)

The critic does **not** produce a score or a pass/fail judgment. It produces a list like:

```
1. Section "Pricing" is empty — source #3 mentions a freemium tier with usage-based pricing above 1000 queries/month. Add this.
2. Section "Recommendation" says "continue to monitor" — this is not actionable. Rewrite to specify what action the PM should take and by when.
3. Section "Key Features" lists 5 features but only 2 have citations. Either cite the others from scout notes or remove them.
```

The reviser incorporates each item from the list into the draft and produces the final output. The reviser is **not** allowed to add new claims that aren't in the scout notes — it can only restructure, fill gaps from existing scout notes, and sharpen language.

This contract keeps the chain deterministic and makes debugging straightforward: if the final output is bad, either the critic missed the problem (inspect the critique) or the reviser ignored the feedback (compare critique to final).

## Users & use cases

**Primary user:** Me, for real competitive intel on Cisco BI/AI tooling competitors.
**Secondary user:** Any PM preparing for a strategy review, a roadmap defense, or an "are we behind on X?" exec question.

**In scope (v1–v2):**
- Input: a product or feature name (e.g., "Linear Agents," "Notion AI," "Hex Magic").
- Output: a markdown one-pager with sections for Positioning, Pricing, Key Features, Differentiators, Gaps, and a PM Recommendation.
- 3–10 cited sources per run.

**Out of scope:**
- JSON or structured data output (markdown only — add later if needed).
- Real-time monitoring / alerting.
- Proprietary data (internal docs, private Slack, etc).
- Anything requiring auth or a backend beyond a CLI.
- Chat interface. Recce is a one-shot tool, not a conversation.

## Design decisions & tradeoffs

| Decision | Chose | Rejected | Why |
|---|---|---|---|
| Agent pattern | Prompt chaining (scout → writer → critic → reviser) | Evaluator-optimizer (loop until score threshold) | Failure mode is fixable in one pass. Looping adds cost/latency with diminishing returns. Upgradeable if evals prove otherwise. |
| Orchestration | Raw Python, sequential Anthropic SDK calls | LangGraph, CrewAI, AutoGen | Want to *understand* the orchestration, not hide it behind a framework. Will revisit in v3. |
| Model | Sonnet for all agents, configurable via env var | Opus for writer; mixed routing | Sonnet is sufficient quality for all four stages. Config variable allows A/B testing during eval week without code changes. Cost stays predictable. |
| Interface | CLI + markdown file output | Web UI, Streamlit, Slack bot | CLI is 1/10th the effort and loses almost nothing for the target use case. A Loom walkthrough handles "how does it feel to use." |
| Source retrieval | Anthropic web search tool | Custom scraping, SerpAPI, Tavily | Built in, works, no extra dependency. Move if it becomes the bottleneck. |
| Critic output format | Numbered list of specific weaknesses | Score, pass/fail, prose review | Specific weaknesses give the reviser actionable instructions. Scores are ambiguous and resist debugging. |
| Revision passes | Exactly one | Loop until threshold | Predictable cost, simple to debug. Upgrade to loop if evals justify it. |
| Sources of truth | Public web only | Paid databases, company intranets | Scope control. Anything that needs auth is out. |

## Success criteria

Recce is successful if:

1. **Dogfood test:** I use it on 3 real competitors during Weeks 2–4 and the output saves me >60 min per run compared to doing it by hand.
2. **Eval pass rate:** On the 5-rubric eval suite (see `evals/`), v2 scores ≥80% on runs against 3 held-out test products.
3. **Interview test:** I can walk a hiring manager through the design decisions in 10 minutes and defend every tradeoff in the table above.

Non-goals as success criteria: stars on GitHub, traffic, other users. Those are nice, not the point.

## Known risks & how I will handle them

- **Risk: the web search tool returns stale or low-quality sources.** Mitigation: the scout agent explicitly filters for recency and source quality, and the critic penalizes low citation density. If still bad, add a manual source-allowlist flag.
- **Risk: the critic rubber-stamps the writer.** Mitigation: the critic is prompted to find at least 2 weaknesses before it is allowed to approve. The critic's output format (numbered list of specific issues) makes rubber-stamping structurally difficult — an empty list is obviously wrong.
- **Risk: the reviser introduces hallucinated claims.** Mitigation: the reviser prompt explicitly forbids new claims not in scout notes. Eval suite includes a "no new unsourced claims" criterion.
- **Risk: cost blows up.** Mitigation: Sonnet everywhere keeps per-run cost low. Cache scout results per product. Log token usage per run and put it in the README.
- **Risk: I over-build instead of ship.** Mitigation: v1 ships end of Week 2 with 2 agents (scout + writer) and hardcoded prompts. Critic and reviser added in Week 3. Everything else is iteration on a working base.

## Milestones

- **v0.1 (end Week 1):** Repo, PRD, hello-world Claude call, decision doc committed.
- **v1.0 (end Week 2):** 2 agents (scout + writer), 3 example runs checked in, usable from CLI.
- **v2.0 (end Week 3):** 4 agents (scout → writer → critic → reviser), BUILD_LOG with real entries.
- **v2.1 (end Week 4):** Eval suite with published results, including failure cases.
- **v2.2 (end Week 5):** Written teardown + Loom walkthrough.
- **v2.2-final (end Week 6):** Interview-ready polish.

## What I will not build in v1

Listing these explicitly so I do not drift:

- Web UI, Streamlit, or any frontend
- Authentication or multi-user support
- A database (filesystem is fine)
- Fine-tuning
- RAG over a custom corpus
- JSON or structured data output beyond markdown
- Observability beyond print statements and a run log
- A framework (LangChain, CrewAI, etc.)
- Tests beyond the eval suite
- CI/CD
- An evaluator-optimizer loop (unless evals justify it)

Each of these is a reasonable v3 conversation in an interview. None are on the critical path to a portfolio artifact.
