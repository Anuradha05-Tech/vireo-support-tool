# Build Prompts — Vireo Audio Support Tool (v2)

Updated against the real README, `support-policy.pdf`, and email thread.
Read `01_ARCHITECTURE.md` v2 first — the taxonomy-building stage from v1 is
gone, replaced with a category-tag audit and a repeat-contact pipeline.

Keep `prompt_log.md` updated live, same as before.

---

## Stage 0 — Repo scaffolding (unchanged)

```
Set up a new Python project called vireo-support-tool for analyzing customer
support tickets. Create this structure:

vireo-support-tool/
  README.md
  requirements.txt
  .env.example
  .gitignore (must exclude data/, .env, __pycache__, *.pyc)
  docs/         <- I'll put planning docs here, don't generate content for these
  data/         <- I will drop the provided CSVs and PDF here, keep this gitignored
  src/
  reports/
  validation/

Use pandas, duckdb, python-dotenv, and an LLM SDK (I'll tell you which). Add
pdfplumber for PDF text extraction. Set up src/config.py for paths and
constants. Initialize git.

I've included docs/01_ARCHITECTURE.md as background on the intended pipeline
and scope. Treat it as context, not a literal spec to execute line by line —
the field names in it are already confirmed against the real README, but
verify them yourself against the actual CSV headers in Stage 1 before relying
on anything downstream.
```

---

## Stage 1 — Data exploration + data-quality checks

```
I've placed these files in ./data/: tickets.csv, agents.csv, orders.csv,
customers.csv, products.csv, support-policy.pdf, README.txt, email-thread.txt.

Write src/profile_data.py that:
1. Confirms tickets.csv actually has these columns: ticket_id, created_at,
   first_response_at, resolved_at, status, channel, customer_id, order_id,
   product_sku, category, priority, assigned_team, agent_id, transfers,
   csat_score, refund_amount_inr, refund_reason_code, replacement_issued,
   customer_message, agent_notes, source_system. Flag any mismatch loudly.
2. Prints row counts, null rates per column, date range, and unique value
   counts/lists for status, channel, category, priority, assigned_team,
   refund_reason_code, source_system.
3. Confirms agents.csv has a tier column and prints its unique values (we
   need to identify which value means "Tier 2" for the leaderboard exclusion).
4. Runs these specific data-quality checks and prints the results:
   a. csat_score: count of 0-values broken down by source_system (legacy_fd
      rows using 0 for "no response" need to be nulled out before any average
      — confirm the scale of the problem here, don't fix it yet)
   b. refund_amount_inr: summary stats (mean/median/max) broken down by
      source_system, to sanity-check whether legacy_fd values look like a
      different unit than helpdesk values
   c. ticket_id: check for duplicates, and for any pattern suggesting legacy
      re-imported IDs collide with current IDs
   d. order_id: null rate, and how many of those could be resolved via the
      customer_id + product_sku fallback against orders.csv
5. Writes everything above to data_profile.md, plus the full text of
   README.txt and email-thread.txt for reference.

Run it and show me the full output before we do anything else.
```

*Stop here and actually read the output. Confirm which `tier` value in
`agents.csv` corresponds to "Tier 2" before Stage 5. Confirm the scale of the
CSAT and legacy-refund issues before Stage 6.*

---

## Stage 2 — Data-quality normalization

```
Based on the findings in data_profile.md, write src/data_quality.py that
produces a cleaned working table (or a set of cleaning functions used by later
scripts) that:
1. Nulls out csat_score where it's 0 AND source_system == 'legacy_fd'
   (leave 0 as-is for source_system == 'helpdesk' only if that system also
   uses 0 for a real score of 0 — confirm this from the README/profile output,
   don't assume).
2. Flags (doesn't necessarily drop) refund_amount_inr rows where
   source_system == 'legacy_fd' if the profiling step found a suspicious scale
   mismatch — add a refund_amount_suspect boolean column rather than silently
   altering values.
3. Deduplicates on ticket_id if the profiling step found real duplicates,
   keeping [decide: latest by created_at, or flag for manual review — tell me
   which you're choosing and why].
4. Resolves order_id where blank using customer_id + product_sku match against
   orders.csv, filling a resolved_order_id column (leave original order_id
   untouched).
5. Adds a week column (ISO week, based on resolved_at for resolved tickets)
   for later grouping, and flags partial first/last weeks in the data.

This is a shared utility other scripts will import — don't duplicate this
logic in multiple files.
```

---

## Stage 3 — Category-tag audit (replaces taxonomy-building)

```
Using tickets.csv's category column (already populated by the intake bot,
agent-corrected on closure), write src/category_audit.py that:
1. Takes a stratified random sample of ~100 tickets across the existing
   category values.
2. For each, sends the customer_message and the assigned category to the LLM,
   asking it to judge in one word (agree/disagree) whether the category looks
   right for that message, with a one-line reason if it disagrees.
3. Reports an agreement % and lists the specific tickets where the LLM
   disagreed, with its reasoning.
4. Writes results to validation/category_audit_sample.csv and a short
   audit_report.md summary.

Do NOT build a new taxonomy or reclassify tickets wholesale here — this is a
sample-based trust check on the field that already exists, not a
replacement for it.

Run it and show me the agreement rate and disagreement examples.
```

---

## Stage 4 — Repeat-contact detection (the core business-goal input)

```
Implement the repeat-contact definition from support-policy.pdf §10 exactly:
"if the same customer contacts again about the same issue within 30 days of
resolution, it's a repeat contact, costed at the contact cost of the channel
used." Write src/repeat_contacts.py that:

1. For every ticket with status in (resolved, closed) and a non-null
   resolved_at, checks whether the same customer_id has another ticket
   created within 30 days AFTER that resolved_at.
2. Since there's no direct issue-link field, match "same issue" using
   category (exact match) AND/OR product_sku (exact match) — implement both
   and let me compare how much the resulting rate differs, then we'll pick
   one and state it as an assumption.
3. For each detected repeat contact, assigns a cost using the channel-specific
   contact cost from support-policy.pdf (chat ₹210, email ₹260, voice ₹520,
   social ₹240 — use the channel of the REPEAT ticket, not the original).
4. Outputs data/repeat_contacts.parquet: original_ticket_id, repeat_ticket_id,
   customer_id, days_between, matched_on (category/sku/both), channel, cost.
5. Prints a summary: total repeat contacts found, as a % of all resolved
   tickets in a recent period (last quarter of data), and total ₹ cost.

Run it with both matching strategies (category-only vs category+sku) and
show me both rates so I can decide which is more defensible.
```

*This is the step to sit with the longest — pick the matching strategy that's
most defensible, not the one that produces the biggest number. State your
choice and reasoning in the memo.*

---

## Stage 5 — (Bonus, cheap) "already told you" language sweep

```
Only do this after Stage 4 works. Write src/repeat_language_sweep.py that:
1. Takes customer_message text from tickets NOT already flagged as a repeat
   contact by the Stage 4 structural join.
2. Runs a cheap LLM classification (or even a keyword/regex pre-filter first,
   LLM only on matches, to keep cost near zero) to flag messages that
   reference a prior unresolved contact — phrases like "already told,"
   "spoke to someone before," "as I mentioned earlier," "again," "still
   waiting since," etc. Ask for a boolean flag plus the matched phrase.
3. Reports how many such tickets exist that the structural 30-day join
   missed, and what that implies about the true repeat-contact rate
   (probably higher than Stage 4's number alone).

Keep this cheap: pre-filter with keywords first, only send likely matches to
the LLM. Report the estimated cost of this step separately from Stage 3/4.
```

---

## Stage 6 — Weekly digest

```
Using the cleaned tickets table and the existing category field, write
src/weekly_digest.py that:
1. Groups tickets by week (from Stage 2's week column) and category,
   producing counts per (week, category).
2. For the most recent complete week, computes top 5 categories by volume and
   % change vs the prior week.
3. Pulls 2-3 representative customer_message examples per top category
   (short, truncated).
4. Also surfaces the repeat-contact rate for that week from Stage 4's output,
   as a headline number alongside the category breakdown — this ties the
   digest directly to the business-goal metric, not just a category count.
5. Renders reports/digest_latest.html per the design in docs/06_REPORT_DESIGN.md.
6. Drops/flags partial first and last weeks.

Run it and show me the resulting HTML.
```

---

## Stage 7 — Agent leaderboard (Tier 1 only, corrected status definition)

```
Using tickets.csv joined to agents.csv, write src/leaderboard.py that:
1. Filters agents.csv to tier == 'Tier 1' equivalents ONLY (exclude the Tier 2
   / Escalations & Warranty value we confirmed in Stage 1) — this is a hard
   rule from support-policy.pdf §6 and an explicit client request, not
   optional.
2. Counts tickets per agent per week where status is 'resolved' OR 'closed'
   (per policy §10's Attendance definition — NOT status == 'closed' alone,
   which specifically means auto-closed-no-reply and would undercount).
3. Produces a ranked table: agent name, tickets this week, tickets prior
   week, rank.
4. Separately, for Tier 2 agents, computes median days-to-resolution instead
   of a ticket count (per policy §6 — they're measured on resolution time,
   not volume) and renders it as a clearly separate, non-ranked section if
   included at all.
5. Renders reports/leaderboard_latest.html per docs/06_REPORT_DESIGN.md,
   including the one-line caveat about the metric's limits.

Run it and show me the output.
```

---

## Stage 8 — Business-goal number

```
Using data/repeat_contacts.parquet from Stage 4, write src/business_goal.py
that:
1. Computes the repeat-contact rate over the last full quarter of data:
   repeat contacts / total resolved tickets in that period.
2. Computes the current ₹ cost per quarter (sum of the cost column from
   Stage 4's output, for that period).
3. Takes a target rate (I'll tell you the number — pick something realistic,
   a few percentage points lower, not a fantasy target) and computes the ₹
   savings per quarter at that target.
4. If Stage 5 was run, adds a second line noting the Stage 5 finding as
   additional, not double-counted, context (don't add its ₹ cost to the main
   number since it's an estimate of under-detection, not a separate cost).
5. Prints a clear paragraph with the arithmetic shown, ready to paste into
   the memo.

Show me the output.
```

---

## Stage 9 — Validation

```
Write src/validate.py that:
1. For the category audit (Stage 3): already produces an agreement % — just
   confirm it's written to validation/category_audit_sample.csv.
2. For repeat-contact detection (Stage 4): sample 40 flagged repeat contacts,
   write both tickets' customer_message side by side to
   validation/repeat_contact_sample.csv with a blank column for me to mark
   true_positive (Y/N) by hand.

After I fill in true_positive, write a function that computes precision
(true positives / total flagged) and writes validation/validation_report.md
summarizing both checks: category-audit agreement % and repeat-contact
precision %, with 2-3 concrete examples of what went wrong in each.
```

*Fill in `true_positive` yourself — this is the human-check step.*

---

## Stage 10 — README (must run on a clean machine)

```
Write the top-level README.md. It must let someone with a clean machine and
no context reproduce the whole thing:
1. Prerequisites (Python version, system deps for pdfplumber/duckdb).
2. pip install -r requirements.txt
3. Where to place the provided data files (data/, exact filenames).
4. .env setup — copy .env.example, add API key.
5. Exact command sequence: profile_data.py → data_quality.py →
   category_audit.py → repeat_contacts.py → (optional) repeat_language_sweep.py
   → weekly_digest.py → leaderboard.py → business_goal.py → validate.py.
6. Where outputs land.
7. Approximate run time and cost for the full pipeline.
8. Known Limitations section: the category/sku matching proxy for "same
   issue" in repeat-contact detection, the legacy-data caveats found in
   profiling, single-source-of-truth reliance on the intake bot's category
   tag (audited on a sample, not verified on every ticket), Tier 2 excluded
   from the leaderboard by design.
```

---

## Stage 11 — Final check before submission

```
Review the full repo for:
1. Any raw customer PII (names, phone numbers, order numbers) accidentally
   committed in example outputs, logs, or README — scrub or synthesize.
2. Confirm data/ and .env are gitignored and not committed.
3. Confirm requirements.txt has pinned versions matching what's installed.
4. Dry run: delete local cache/venv, reinstall from requirements.txt only,
   re-run the README's commands exactly as written to confirm it works from
   a clean machine.

Report anything broken.
```

---

## Things to write yourself, not delegate

- **`memo.md`** — use `03_MEMO_TEMPLATE.md`, now filled with the repeat-contact
  number and the ₹290 blended figure (Priya's own number, not a guess).
- **Manual labels** in `validation/repeat_contact_sample.csv` and any
  disagreement review in the category audit.
- **`prompt_log.md`** — keep live.
- **The matching-strategy decision in Stage 4** (category vs sku vs both) —
  an agent can run both, but you should pick and justify the one you ship.
- **The screen recording** — script it from `04_VIDEO_SCRIPT.md`; the "what
  changed between versions" segment now has an obvious real example: pivoting
  from taxonomy-building to the existing-category-audit approach once you saw
  the README, and possibly the category-vs-sku matching decision in Stage 4.
