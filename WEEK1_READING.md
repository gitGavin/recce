# Week 1 Reading List — AI PM Calibration Sprint

**Goal:** Get fluent in the current vocabulary and mental models of 2026 AI PM work. You are not studying — you are calibrating. Skim hard, take notes on *vocabulary and mental models*, skip anything that reads like a tutorial.

**Time budget:** 4 hours total for reading. The remaining Week 1 hours go to the repo scaffold and the PRD.
**Posture:** Opinionated skimming. If a piece does not teach you a new word, a new framework, or a new failure mode in the first 3 minutes, close it and move on.

---

## Tier 1 — Non-negotiable (≈2 hours)

These are the four pieces that the rest of the plan assumes you have read. If you only do Tier 1 this week, you are still in good shape.

### 1. Anthropic — "Building Effective Agents" (Schluntz & Zhang)
https://www.anthropic.com/engineering/building-effective-agents

*Why:* The current lingua franca for agent design patterns. When an interviewer says "is this an orchestrator-workers pattern or an evaluator-optimizer?" this is the post they read. You need the taxonomy in your head verbatim.

*What to extract:*
- The workflow-vs-agent distinction (workflows = predefined code paths, agents = LLMs dynamically directing themselves).
- The five workflow patterns: prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer.
- Why they recommend starting with raw SDK calls instead of frameworks.
- The line "find the simplest solution possible, and only increase complexity when needed" — this is your Kiro design principle.

*Companion code (skim, do not study):* https://github.com/anthropics/anthropic-cookbook/tree/main/patterns/agents

### 2. Anthropic — "Effective Context Engineering for AI Agents"
https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

*Why:* This is where the vocabulary shift from "prompt engineering" to "context engineering" got codified. Interviewers in 2026 use "context engineering" the way they used "prompt engineering" in 2024. If you still call it prompt engineering, you are signaling that you are a year behind.

*What to extract:*
- The definition: context engineering = curating and maintaining the optimal set of tokens during inference, including everything that lands in context outside the prompt.
- The "just-in-time" vs "upfront retrieval" distinction.
- The hybrid strategy example (Claude Code's CLAUDE.md + glob/grep).
- Why context is "a critical but finite resource."

### 3. Hamel Husain — "Your AI Product Needs Evals"
https://hamel.dev/blog/posts/evals/

*Why:* Evals are the #1 thing AI PM interviews probe on in 2026, and this is the canonical post. Hamel's thesis — that most teams fail at #1 (evaluating quality) and #2 (debugging via logging), then obsess over #3 (prompt engineering and fine-tuning) — maps directly onto what goes wrong in real AI products.

*What to extract:*
- The three-level eval hierarchy (unit tests → model-based → human review), their costs, and when to run each.
- Why binary pass/fail beats 1-5 scales (this one sentence will win you interview points).
- The "virtuous cycle" framing: eval → debug → change, on repeat.
- The Rechat case study as a template for how to talk about your own Kiro evals in Week 4.

### 4. Hamel Husain — "A Field Guide to Rapidly Improving AI Products"
https://hamel.dev/blog/posts/field-guide/

*Why:* This is the operational companion to the evals post. It is also the clearest articulation of the "error analysis is all you need" approach, which is how you should plan Kiro's v2 → v2.1 iteration.

*What to extract:*
- Error analysis as the source of eval criteria (not the other way around).
- Why synthetic data is underrated for bootstrapping evals when you don't have user data yet (directly applicable to Kiro).
- The "criteria drift" phenomenon — you cannot fully define eval criteria until you have seen a range of outputs.

---

## Tier 2 — High value if time permits (≈1.5 hours)

Read these if you finish Tier 1 with hours left. Ranked by ROI.

### 5. Anthropic — "Writing Effective Tools for AI Agents"
https://www.anthropic.com/engineering/writing-tools-for-agents

*Why:* If Kiro's scout agent is going to use the web search tool well, you need to understand the tool-use mental model. Also answers the "how do you decide what tools to give an agent?" interview question.

*Extract:* the namespacing discussion, the "test tools with Claude Code" technique, the bias toward fewer thoughtful tools over many narrow ones.

### 6. Hamel Husain — "Using LLM-as-a-Judge for Evaluation: A Complete Guide"
https://hamel.dev/blog/posts/llm-judge/

*Why:* Your Week 4 eval suite will use LLM-as-judge for several criteria. This post tells you how to do it without the common failure modes (too many metrics, arbitrary scales, no domain expert validation).

*Extract:* the binary-judgment principle, the "validate your judge against human labels" workflow, the synthetic data generation recipe.

### 7. Lenny's Newsletter — "Evals, error analysis, and better prompts" (Hamel interview)
https://www.lennysnewsletter.com/p/evals-error-analysis-and-better-prompts

*Why:* PM-framed version of Hamel's work. Useful specifically because it is pitched at PMs, so the language and framing is closer to what you will hear in interviews. Also worth it for the Nurture Boss case study as a second template alongside Rechat.

*Extract:* the error analysis framework, the custom annotation system idea, the "vibe checking vs data-driven" framing.

---

## Tier 3 — Optional, read opportunistically (≈30 min, or skip)

Only if you finish Tier 1 + 2 and have time, or on a walk via audio.

### 8. Hamel Husain — "LLM Evals: Everything You Need to Know" (FAQ)
https://hamel.dev/blog/posts/evals-faq/

A dense FAQ that distills 700+ students' questions. High signal-per-word but repetitive with posts above. Good for filling gaps; skim the table of contents and only read sections on topics you still feel fuzzy on.

### 9. Anthropic — "Building Effective AI Agents" (resources page)
https://resources.anthropic.com/building-effective-ai-agents

A longer-form companion piece with real customer examples (Coinbase, Intercom, Thomson Reuters). Useful if you want named case studies to reference in interviews. Skim only.

---

## What I deliberately left off this list

You will see these in every "AI PM reading list" floating around, and they are not on yours because they are low ROI for your specific sprint:

- **Anything on fine-tuning, RLHF, or RLAIF.** Out of scope for applied/agent PM roles, and the vocabulary will date fast.
- **"Attention is All You Need" and transformer papers.** Unnecessary. No interviewer for an Applied AI PM role will quiz you on multi-head attention. If they do, the job is wrong for you.
- **Long RAG deep dives.** RAG matters, but a PRD-level understanding of "retrieval + generation, with tradeoffs on chunking, embedding choice, and recency" is all you need. A full deep dive is Week 10 territory, not Week 1.
- **LangChain / LlamaIndex / CrewAI documentation.** We are deliberately *not* using a framework for Kiro. Reading the docs now would pull you in the wrong direction.
- **Twitter/X threads from AI influencers.** Noisy, repetitive, and the good stuff gets collected into blog posts like the ones above anyway.
- **Courses (Maven, DeepLearning.AI, etc.).** Hamel and Shreya's eval course is excellent and I would recommend it later — but it is 3–4 hrs/week for 4 weeks, which is your entire weekly budget. Do the sprint first, take the course after if you want to go deeper.

---

## Note-taking format (optional but recommended)

Create a `NOTES.md` in your repo (you can delete it before making the repo public, or keep it — your call). For each Tier 1 piece, capture:

1. **Three new terms or frameworks** you want to be able to use in an interview.
2. **One design decision it changed** in your Kiro PRD.
3. **One interview question** you can now answer better than you could yesterday.

If a piece does not generate at least one of each, it was not worth reading and you should recalibrate.

---

## What "done" looks like for Week 1

By end of Week 1 you should be able to, without looking anything up:

- Name the five Anthropic agent workflow patterns and give a one-sentence description of each.
- Explain the difference between prompt engineering and context engineering in a way a non-technical exec would understand.
- Argue for binary pass/fail evals over a 1–5 scale, and say when you would use which.
- Point at Kiro's design and say "this is an evaluator-optimizer pattern, here is why I picked it over alternatives."

If you can do those four things, you are calibrated. Move on to Week 2 and start shipping.
