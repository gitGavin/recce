# Build Log

A running log of decisions, dead ends, and things that broke. Written for my future self and for interviews.

---

## 2026-04-15 — Week 1, Day 1

Decided to name the project Recce. Other candidates were Probe and Scry. Recce won because [fill in your real reason — don't copy mine].

Scaffolded the repo with PRD, README, and reading list. Deliberately did not write any code yet — Week 1 is for locking the design and the vocabulary, not for shipping. The risk I'm managing: starting to code before the design is defensible means I'll end up rewriting the design to match the code, which is backwards.

## 2026-04-20 — Week 1: PRD v0.2 design decisions

After reading Anthropic's "Building Effective Agents" and the context engineering post, I revised three design choices in the PRD.

**Changed agent pattern from evaluator-optimizer to prompt chaining.** The evaluator-optimizer pattern loops until a quality threshold is met, which is powerful but adds retry logic, cost unpredictability, and debugging complexity. The actual failure mode I'm solving — "plausible but shallow" output — is catchable in a single critique-and-revise pass. Prompt chaining (scout → writer → critic → reviser) gives me predictable cost, predictable latency, and intermediate artifacts I can inspect when something breaks. If Week 4 evals show one pass isn't enough, I can upgrade to a loop without rewriting the pipeline.

**Standardized on Sonnet for all agents instead of Opus for the writer.** After reading the cost/latency tradeoff discussions, I don't think the quality gap justifies the cost gap for a portfolio project where I'll run this dozens of times during development. I'm keeping the model as a config variable so I can A/B test with Opus during eval week and let the data decide.

**Cut JSON output from scope.** Nobody will consume structured output in the 6-week window. Markdown is the artifact that matters for examples, dogfooding, and the Loom demo. Removing it also avoids a premature decision about whether to use tool_use for structured output or just parse markdown.

**Added the critic → reviser contract.** This was the non-obvious design detail that came out of the pattern change. In evaluator-optimizer, the loop naturally defines "done" (score ≥ threshold). In prompt chaining, you need an explicit contract: the critic outputs a numbered list of specific, actionable weaknesses — not a score, not vibes — and the reviser addresses each one without introducing new unsourced claims. This keeps the chain deterministic and debuggable.
