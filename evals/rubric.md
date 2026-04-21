# Recce Eval Rubric

5 criteria, each scored PASS or FAIL. Binary — no 1-5 scales.
(See Hamel Husain's "Your AI Product Needs Evals" on why binary beats scales.)

## 1. Citation Density
- PASS: The final one-pager cites ≥3 distinct sources, and each citation 
  maps to a specific claim in the text.
- FAIL: Fewer than 3 citations, or citations are decorative (placed at 
  end of paragraph without linking to a specific claim).

## 2. Recency
- PASS: At least 2/3 of cited sources are dated within the last 12 months.
  Any source older than 12 months is explicitly noted as foundational context.
- FAIL: Majority of sources are stale, or old sources are used without 
  acknowledging their age.

## 3. Coverage
- PASS: All 6 required sections (Positioning, Pricing, Key Features, 
  Differentiators, Gaps/Weaknesses, PM Recommendation) are present and 
  contain substantive content (≥2 sentences) or an explicit "No public 
  information found" note.
- FAIL: Any section is missing, empty, or contains only one vague sentence.

## 4. Actionability
- PASS: The PM Recommendation names a specific action, includes a timeframe 
  or trigger, and explains why. Example: "Pilot Linear Agents on one 
  internal team within 30 days to evaluate whether its delegation model 
  reduces triage time."
- FAIL: Recommendation uses hedge language ("consider," "monitor," 
  "evaluate when ready") without specifics.

## 5. Faithfulness (no hallucination)
- PASS: Every factual claim in the final one-pager can be traced to a 
  specific source in the scout notes. No invented stats, dates, or features.
- FAIL: Any claim in the final one-pager does not appear in the scout notes.