# PRD: Kiro — Competitive Intelligence Agent for PMs

**Author:** Gavin Jin
**Status:** Draft v0.1
**Last updated:** Week 1

---

## TL;DR

Kiro is a multi-agent system that turns a product name into a PM-ready competitive one-pager in under 5 minutes. A scout agent gathers recent public information, a writer agent drafts a structured teardown, and a critic agent reviews the draft against a quality rubric before the final output is returned.

It is built to be used by me (a working PM) on real competitive intelligence tasks, not as a demo. If it is not useful to me by the end of Week 2, the project has failed its most important test.

## Problem

PMs regularly need to answer: *"What is company X doing in space Y, and what does it mean for us?"* The current workflow is:

1. Open 10 browser tabs, search for recent news, blog posts, pricing pages, changelogs.
2. Skim, copy-paste into a doc, try to structure it.
3. Write a one-pager with positioning, pricing, feature gaps, and a recommendation.
4. Realize half the sources are stale or contradictory. Start over.

This takes 2–4 hours for a mediocre result. The bottleneck is not reading speed — it is the structuring and the tradeoff between breadth (cover everything) and depth (actually synthesize).

Existing tools either fail at structure (general chatbots return prose blobs with no rubric), fail at recency (training-data answers), or fail at cost/control (enterprise CI platforms are $$$ and opaque).

## Why an agent, not a prompt

A single-shot prompt can produce a one-pager, but fails on three things Kiro needs:

1. **Sourcing discipline.** A scout agent with web search, run separately from the writer, forces the system to collect evidence before it synthesizes — which catches hallucinations the writer would otherwise confabulate.
2. **Critique under a rubric.** A critic agent that scores the draft against fixed criteria (coverage, actionability, citation density) catches the "sounds good, says nothing" failure mode that is the #1 problem with LLM-generated strategy docs.
3. **Auditability.** Separate agents produce separate artifacts (scout notes, draft, critique, final). A PM reading the output can trace *why* a claim appears, not just *that* it appears.

## Users & use cases

**Primary user:** Me, for real competitive intel on Cisco BI/AI tooling competitors.
**Secondary user:** Any PM preparing for a strategy review, a roadmap defense, or an "are we behind on X?" exec question.

**In scope (v1–v2):**
- Input: a product or feature name (e.g., "Linear Agents," "Notion AI," "Hex Magic").
- Output: a markdown one-pager with sections for Positioning, Pricing, Key Features, Differentiators, Gaps, and a PM Recommendation.
- Structured JSON output alongside markdown for downstream use.
- 3–10 cited sources per run.

**Out of scope:**
- Real-time monitoring / alerting.
- Proprietary data (internal docs, private Slack, etc).
- Anything requiring auth or a backend beyond a CLI.
- Chat interface. Kiro is a one-shot tool, not a conversation.

## Design decisions & tradeoffs

| Decision | Chose | Rejected | Why |
|---|---|---|---|
| Orchestration | Raw Python, sequential Anthropic SDK calls | LangGraph, CrewAI, AutoGen | Want to *understand* the orchestration for interviews, not hide it behind a framework. Will revisit in v3. |
| Agent pattern | Evaluator-optimizer (scout → writer → critic → optional revise) | Single prompt; parallel agents; hierarchical orchestrator | Matches the actual failure mode (draft is plausible but weak), and is cheap to run. |
| Model routing | Sonnet for scout + critic, Opus for writer | All Opus; all Sonnet | Writer does the hard synthesis and deserves the better model; scout and critic are more structured and cheaper. Revisit after evals. |
| Interface | CLI + markdown file output | Web UI, Streamlit, Slack bot | CLI is 1/10th the effort and loses almost nothing for the target use case. A Loom walkthrough handles "how does it feel to use." |
| Source retrieval | Anthropic web search tool | Custom scraping, SerpAPI, Tavily | Built in, works, no extra dependency. Move if it becomes the bottleneck. |
| Sources of truth | Public web only | Paid databases, company intranets | Scope control. Anything that needs auth is out. |

## Success criteria

Kiro is successful if:

1. **Dogfood test:** I use it on 3 real competitors during Weeks 2–4 and the output saves me >60 min per run compared to doing it by hand.
2. **Eval pass rate:** On the 5-rubric eval suite (see `evals/`), v2 scores ≥80% on runs against 3 held-out test products.
3. **Interview test:** I can walk a hiring manager through the design decisions in 10 minutes and defend every tradeoff in the table above.

Non-goals as success criteria: stars on GitHub, traffic, other users. Those are nice, not the point.

## Known risks & how I will handle them

- **Risk: the web search tool returns stale or low-quality sources.** Mitigation: the scout agent explicitly filters for recency and source quality, and the critic penalizes low citation density. If still bad, add a manual source-allowlist flag.
- **Risk: the critic rubber-stamps the writer.** Mitigation: the critic is prompted to find at least 2 weaknesses before it is allowed to approve, and eval runs include "adversarial" drafts to make sure the critic catches known-bad outputs.
- **Risk: cost blows up.** Mitigation: cache scout results per product, cap max critic-revise loops at 1, log token usage per run and put it in the README.
- **Risk: I over-build instead of ship.** Mitigation: v1 ships end of Week 2 with 2 agents and hardcoded prompts. Everything else is iteration on a working base.

## Milestones

- **v0.1 (end Week 1):** Repo, PRD, hello-world Claude call, decision doc committed.
- **v1.0 (end Week 2):** 2 agents (scout + writer), 3 example runs checked in, usable from CLI.
- **v2.0 (end Week 3):** 3 agents with critic + revise loop, BUILD_LOG with real entries.
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
- Observability beyond print statements and a run log
- A framework (LangChain, CrewAI, etc.)
- Tests beyond the eval suite
- CI/CD

Each of these is a reasonable v3 conversation in an interview. None are on the critical path to a portfolio artifact.
