# Video Script Outline — 3 minutes max

The brief asks for three specific things: prompts used, what changed between versions,
what you threw away. Don't narrate a feature tour — that's not what's graded. Structure
the whole recording around those three questions, in order, and stop.

Record last, after the build is done — you're narrating decisions you already made,
not discovering them live. Have `prompt_log.md` open in one tab as your source of
truth so you're not reconstructing from memory.

---

## Timing budget (3:00 total, be strict)

| Segment | Time | Content |
|---|---|---|
| Cold open | 0:00–0:15 | One sentence: what you built and the ₹ number. No "hi my name is." |
| Prompts you used | 0:15–1:15 | 2–3 actual prompts, shown on screen, with one line each on what they got you |
| What changed between versions | 1:15–2:15 | One concrete before/after (taxonomy, prompt, or approach) |
| What you threw away | 2:15–2:50 | One thing you built and cut, and why |
| Close | 2:50–3:00 | Where the memo/repo/report are — no summary, no sign-off speech |

---

## Segment-by-segment script

### 0:00–0:15 — Cold open
Say the outcome, not the process, first:
> "I built a tool that classifies Vireo's support tickets into complaint categories
> and found that [category] is costing about ₹[A] a quarter. Here's how I built it
> and what I'd change."

Screen: the digest report, already loaded, showing the top category.

### 0:15–1:15 — Prompts you used
Don't read prompts verbatim off screen for a full minute — pick the 2, at most 3,
that mattered:
1. The taxonomy-discovery prompt (Stage 2) — show `taxonomy.json`, say in one line
   why you constrained it to a closed list instead of open-ended classification.
2. The classification prompt (Stage 3) — show one example ticket going in, one
   category coming out.
3. (Optional, only if time) The business-goal prompt (Stage 6) — show the ₹
   arithmetic it produced.

For each: show the prompt on screen for 2–3 seconds, say what it got you, move on.
Don't explain the code — the prompt is the interesting part here, not the Python.

### 1:15–2:15 — What changed between versions
Pick ONE real example, not a list. Good candidates:
- "My first taxonomy had 20+ overlapping categories the LLM invented per batch —
  I merged it down to 12 and gave each a one-line definition so classification
  would actually be consistent."
- "I first tried classifying tickets with an open prompt with no fixed category
  list — results weren't groupable into a digest, so I switched to closed-list
  classification against a frozen taxonomy."
- "My first cost estimate used ticket count alone — switched to count × per-ticket
  cost from the policy doc once I realized a smaller but pricier category mattered
  more."

Show the before and after on screen (diff, or just two screenshots side by side).
This is the segment that proves you iterated, not just executed — spend the most
care here.

### 2:15–2:50 — What you threw away
One thing, stated plainly, with the real reason:
> "I built a per-ticket sentiment score early on, but it didn't change which
> categories rose to the top of the digest, so I cut it — it was adding cost
> without adding signal."

Or, if you cut something for time rather than judgment, say that too — honesty
about a time cut is fine and expected, don't dress it up as a design decision if
it wasn't one.

### 2:50–3:00 — Close
> "Full repo, memo, and reports are linked in the submission. Thanks."

No recap. Stop talking, cut the recording.

---

## Recording notes

- Phone recording of your screen is explicitly fine per the brief — don't burn
  time on screen-recording software setup if your phone works.
- Do one dry run of the full script with a stopwatch before the real take — 3
  minutes goes faster than it sounds when you're clicking between windows.
- Have every screen you'll show (taxonomy.json, a before/after, the digest page)
  already open in tabs before you hit record — don't navigate live, it eats time
  and looks unrehearsed.
- If you go over 3:00, cut from the prompts segment first (drop to 2 prompts),
  never from the "what changed" or "what you threw away" segments — those are
  the ones the brief specifically asks for.
