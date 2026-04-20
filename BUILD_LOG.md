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

## 2026-04-20 — Week 2: Scout + Writer v1

**Scout agent works, but web search produces a lot of token volume.** The scout's web_search tool with max_uses=10 generates ~12K characters of structured notes for a single product. That's fine for quality — the sources are real, recent, and well-structured — but it eats into Anthropic's 30K input token per minute rate limit on my current API tier. Running the scout and writer back-to-back hits 429 errors because the writer call comes in before the rate limit window resets.

**Fix for now:** Added a `time.sleep()` pause between the scout and writer steps in the CLI. This is ugly but functional. The real fix would be either upgrading the API tier, reducing `max_uses` on the scout's web search, or caching scout results so I don't re-run the scout when iterating on the writer prompt.

**Writer prompt required more structure than I expected.** My first instinct was to give the writer loose instructions and let it figure out the format. The output was readable but inconsistent — sometimes it included a Pricing section, sometimes it folded pricing into Key Features. Adding an explicit section template with exact headers solved this immediately. Lesson learned: for structured output, be explicit about format. Save the creativity for content, not structure.

**The "no public information found" instruction matters.** Without it, the writer would fill in sections with plausible-sounding guesses when the scout notes had no relevant data. Adding the explicit instruction to write "No public information found" instead of guessing eliminated this failure mode. This is the kind of thing the critic should catch in Week 3 — claims that appear in the draft but not in the scout notes.

**First end-to-end run produced a usable one-pager.** Not great, but usable. The main weaknesses I noticed and want the critic to catch in Week 3:
- Recommendation section is still too generic ("consider evaluating Linear Agents for your team") — needs to be more specific about what action to take and by when.
- Some citations are vague ([Source 1]) without making it clear which claim maps to which source.
- The Gaps/Weaknesses section tends to be thin — the writer seems reluctant to be critical, probably because the scout notes are mostly from official sources which are naturally positive.

These observations will feed directly into the critic prompt and the eval rubric.

## 2026-04-20 — Week 3: Full 4-agent chain

**The critic-reviser chain works — and the improvement is visible.** Comparing draft.md vs final.md side by side, the reviser consistently fixes the weaknesses the critic identifies. The most common improvements: filling in thin Gaps/Weaknesses sections, sharpening vague recommendations into specific actions, and removing unsourced claims the writer had hallucinated. The chain is doing what the PRD said it would.

**The critic prompt needed calibration.** My first version was too soft — it found 1-2 minor issues and called it done. Adding the "must identify ≥2 weaknesses" floor and the explicit failure mode checklist (unsourced claims, weak recommendations, thin sections, vague citations, redundancy) made the critic substantially more useful. The key insight: a critic that praises the draft is useless. I removed any language that allowed positive feedback and the output quality jumped immediately.

**The critic → reviser contract held up.** The numbered-weakness format works exactly as designed in the PRD. Each weakness names the section, states the problem, and states the fix. The reviser addresses them in order. I can trace exactly which critique led to which change in the final output. This is the debugging superpower of prompt chaining — when something goes wrong, I know which step to fix.

**The reviser mostly respects the "no new claims" rule.** In 2 out of 3 runs, the reviser only used information from scout notes. In one run, it added a plausible-sounding claim about pricing that wasn't in the sources. This is the exact risk I flagged in the PRD. For now the prompt instruction is sufficient, but this will be an eval criterion in Week 4 — automated checking that every claim in final.md traces back to scout_notes.md.

**Rate limiting is the biggest operational pain.** With 4 agents, the pipeline makes 4 API calls, and my free-tier rate limit (30K input tokens/minute) gets hit between almost every step. Added a retry-with-backoff helper that waits and retries automatically. This turned a 2-minute pipeline into a 5-minute one, but it runs unattended now. Worth noting in the README as expected runtime. In a production context, this is where you'd argue for a higher rate limit tier or implement caching — scout results rarely change hour to hour.

**Prompt chaining was the right call.** After seeing the full chain run, I'm confident evaluator-optimizer would have been overkill. One critique pass catches the structural issues. A second pass would mostly nitpick wording, which isn't worth the cost or latency. If Week 4 evals disagree, I'll revisit — but right now the data supports the design choice.
