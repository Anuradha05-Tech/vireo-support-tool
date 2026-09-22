# Vireo Audio — Support Intelligence Tool
## Architecture & Scope Document — v2, updated after reading the real README, policy PDF, and email thread

**What changed from v1:** the real data model, the real cost figures, and a hard
leaderboard constraint are now known — this version replaces guesses with facts.
The biggest change: you likely don't need to invent a complaint taxonomy at all
(there's already a `category` field), and there's a stronger, policy-defined
business metric available than "biggest complaint category."

---

## 1. Restating the actual problem

Priya's literal ask: weekly digest + leaderboard. But three other people are in
that email thread with their own stakes, and a strong submission answers all of
them, not just Priya:
- **Arjun (Finance):** wants contacts *removed from the queue*, not just counted,
  and is explicitly worried about an AI bill surprising him — "no surprise bill
  in November."
- **Neha (Ops):** flagged that chat agents keep hearing "I already told your
  colleague this," and explicitly said don't rank her Tier 2 warranty team on
  ticket volume — their cases are multi-touch by design.
- **Priya:** corrected Arjun's cost-per-contact guess (₹180) with the real
  figure from the policy doc (₹290 blended) — meaning she already knows the
  real numbers and will notice if yours don't match.

A submission that (a) uses the real ₹290 figure, not a guess, (b) respects the
Tier 2 exclusion Neha explicitly asked for, and (c) follows up on her "already
told your colleague" comment with a real repeat-contact number, is answering
the room, not just the headline request.

---

## 2. Time budget (5 hours, hard cap) — revised, taxonomy-discovery time reallocated

| Phase | Time | Output |
|---|---|---|
| Data exploration (confirm schema, run data-quality checks below) | 30 min | `data_profile.md` |
| Category-tag audit (NOT a full taxonomy build — see §5) | 20 min | audit notes |
| Repeat-contact detection pipeline | 50 min | `repeat_contacts.parquet` |
| Weekly digest generator (uses existing `category`) | 35 min | digest report |
| Agent leaderboard (Tier 1 only, resolved+closed) | 25 min | leaderboard report |
| Business-goal number (repeat-contact cost model) | 30 min | number + memo draft |
| Validation (category-tag accuracy + repeat-contact spot-check) | 30 min | accuracy report |
| Minimal UI / report styling | 25 min | HTML reports |
| README, cleanup, submission form, video | 35 min | polish |

The taxonomy-discovery step from v1 is gone — the 30 minutes it would have cost
is now spent on the repeat-contact pipeline, which is the real differentiator.

---

## 3. Explicit scope decisions

**In scope:**
- Weekly digest using the **existing** `category` field (bot-assigned at intake,
  agent-correctable at closure) — no new taxonomy invented
- A light AI audit of whether that existing tag is trustworthy (sample-based)
- A repeat-contact detection pipeline, built from the policy's own definition
  (§10), with a measured ₹ cost
- Agent leaderboard restricted to Tier 1, using `status in {resolved, closed}`
  per the policy's Attendance definition, split from Tier 2 entirely
- A validation sample with a measured error rate

**Deliberately out of scope (say so, and say why):**
- Building a new complaint taxonomy from scratch — the intake bot already does
  this; reinventing it duplicates existing infrastructure for no benefit
- Full ticket-by-ticket LLM reclassification of all ~20k+ tickets — expensive,
  and Arjun explicitly flagged cost as a concern; auditing a sample is cheaper
  and answers the same question ("can we trust this field") more directly
- Fixing CSAT methodology beyond the blank/0 normalization — deeper CSAT
  analysis wasn't asked for
- Root-causing *why* a repeat-contact spike happens (firmware release, bad
  batch/lot) — flag as a natural next step, don't try to prove causation here
- A per-agent quality score beyond volume — not asked for, and building one
  without care would repeat the exact mistake Neha warned about (unfairly
  penalizing agents doing harder work)

---

## 4. Data model — confirmed from the real README

**`tickets.csv`** (one row per ticket, Jan 2025–Jun 2026, IST as displayed):
`ticket_id, created_at, first_response_at, resolved_at, status, channel,
customer_id, order_id, product_sku, category, priority, assigned_team,
agent_id, transfers, csat_score, refund_amount_inr, refund_reason_code,
replacement_issued, customer_message, agent_notes, source_system`

- `status`: `resolved | closed (auto-closed, no reply) | open | pending`
- `category`: **set by the intake bot at creation; agents may correct on
  closure** — use this directly, don't rebuild it
- `order_id`: blank when not quoted; fall back to `customer_id + product_sku`
- `csat_score`: blank = no response (current system); **`0` = no response in
  legacy rows — not a real score of 0, must be excluded from any average**
- `source_system`: `helpdesk | legacy_fd` — legacy rows were migrated, some
  re-imported (§9), and their monetary values may be in a different unit —
  sanity-check before trusting `refund_amount_inr` on legacy rows

**`agents.csv`**: one row per assignment — `agent_id, name, site, team, shift,
tier, from_date, to_date`. An agent can have multiple rows (site/shift/tier
changes). **`tier` matters: Tier 2 (Escalations & Warranty) must never be
compared to Tier 1 on ticket-volume metrics — this is a hard policy rule
(§6) and an explicit ask from Neha in the email thread.**

**`orders.csv`**: `order_id, customer_id, sku, order_date, channel, qty,
order_value_inr, lot_code` — `lot_code` is worth keeping; a manufacturing lot
tie-in to a spike is exactly the kind of "found something nobody asked for"
answer that's cheap if the join is already there.

**`customers.csv`**: `customer_id, name, city, state, signup_date, care_plus`

**`products.csv`**: `sku, product_name, family, launch_date, unit_cost_inr,
retail_price_inr, warranty_months` — `unit_cost_inr` feeds the replacement
cost formula directly (§5 below).

**`support-policy.pdf` — the real cost figures, use these, not placeholders:**
- Blended cost per contact: **₹290** (chat ₹210, email ₹260, voice ₹520,
  social ₹240) — this is the figure Priya herself confirmed in the email
  thread, correcting Arjun's ₹180 guess. Use ₹290, not a re-derived estimate.
- Internal transfer cost: ₹305/transfer
- Agent cost: ₹165/agent-hour, 8-hour shift
- SLA breach credit: ₹350 automatic store credit if first response misses
  target (chat 15 min, voice 2 hr, social 4 hr, email 8 hr)
- Replacement cost: `unit_cost_inr` (from products.csv) + ₹340 reverse
  pickup/forward shipping
- Goodwill credit cap: ₹500/ticket
- **Repeat contact, defined precisely in §10:** if the same customer contacts
  again about the same issue within 30 days of resolution, it's a repeat
  contact, costed at the contact cost of the channel used. This is the
  definition your business-goal metric should implement directly.

---

## 5. Pipeline architecture — revised

```
tickets.csv ──► [1] Data-quality pass
                     - normalize legacy csat_score 0 → null
                     - sanity-check legacy refund_amount_inr scale
                     - dedupe check on ticket_id (legacy re-imports)
                     - fallback join order_id via customer_id+product_sku
                     - drop/flag partial first & last weeks
                     │
                     ▼
              [2] Category-tag audit (sample only, not full reclassification)
        sample ~100 tickets → read customer_message → does the bot's
        `category` tag look right? → audit_report.md with an agreement %
                     │
                     ▼
tickets.csv ──► [3] Weekly digest — groupby(week, category) on the EXISTING
                    category field. No LLM classification needed for this part.
                     │
tickets.csv +   ──► [4] Repeat-contact detection (the core business-goal input)
customers.csv        for each resolved ticket: does the same customer_id have
                      another ticket (same category and/or product_sku as
                      proxy for "same issue") within 30 days after resolved_at?
                      → repeat_contacts.parquet: ticket_id, is_repeat, channel,
                        contact_cost
                     │
                     ├──► [5] Business-goal calc: repeat-contact rate ×
                     │        blended/channel contact cost → ₹/quarter,
                     │        vs. a realistic target rate
                     │
                     ├──► [6] (Bonus, cheap) LLM sweep of customer_message for
                     │        "I already told you / already reported this"
                     │        language — flags likely repeat contacts the
                     │        30-day structural join might miss (different
                     │        channel, different category tag, just outside
                     │        30 days). This directly answers Neha's anecdote.
                     │
                     ▼
              [7] Validation: hand-check both the category-tag audit sample
                  AND a sample of the repeat-contact flags (did the join
                  actually catch real repeats, any false positives?)

agents.csv + tickets.csv ──► [separate] Leaderboard
  filter tier == 'Tier 1' (or equivalent per your agents.csv values)
  status in {resolved, closed}   ← per policy §10 Attendance definition
  groupby(agent_id, week) → counts, rank
  Tier 2 agents: NOT ranked by volume — if you want to show them at all,
  use median days-to-resolution instead (policy §6 explicitly says Tier 2
  is measured on resolution time, not ticket count)
```

**Why this is cheaper and better than the v1 plan:** the original plan spent
most of the AI budget re-inventing a taxonomy and reclassifying every ticket —
duplicating work the intake bot already does. The real leverage is in (a)
auditing whether the existing tag can be trusted, which needs only a sample,
and (b) detecting repeat contacts, which is mostly a **join + date-window
check**, not an LLM task at all. LLM usage becomes small, targeted, and cheap
— directly addressing Arjun's cost worry instead of validating it.

---

## 6. Tech stack (unchanged)

- **Language:** Python
- **Storage/processing:** pandas or DuckDB — DuckDB is genuinely convenient
  here given 5 CSVs with several join keys (`customer_id`, `product_sku`,
  `order_id` with its fallback rule, `agent_id`)
- **Classification/audit model:** a cheap, fast LLM tier is enough — the
  category audit is small-sample and the "already told you" sweep is a
  simple binary flag per message, neither needs a frontier model
- **PDF extraction:** `pdfplumber` for `support-policy.pdf` (already done
  above, but re-extract in code so your pipeline is reproducible, not
  hand-copied)
- **Report/UI:** static HTML per `06_REPORT_DESIGN.md`
- **Caching:** cache any LLM call by `ticket_id`, same as before

---

## 7. The business-goal number — revised, policy-grounded method

1. Run the repeat-contact join (§5, step 4): for each resolved ticket, check
   whether the same customer has another ticket within 30 days, matched on
   `category` and/or `product_sku` as a proxy for "same issue" (the data has
   no direct issue-linking field, so state this proxy explicitly as an
   assumption in the memo).
2. Compute the current repeat-contact rate over a recent period (e.g. last
   quarter of data): `repeat_tickets / total_resolved_tickets`.
3. Cost each repeat contact at its channel's contact cost (₹210/260/520/240,
   or ₹290 blended if you're not breaking out by channel).
4. State it exactly like this: *"N% of resolved tickets generate a repeat
   contact within 30 days, costing ≈ ₹A/quarter. Cutting that to a target of
   M% would save ≈ ₹B/quarter."*
5. Optionally strengthen it with step 6 from the pipeline (the "already told
   you" language sweep) as a second, smaller number: *"On top of that, we
   found K tickets where the customer explicitly referenced a prior contact
   that the 30-day structural check didn't catch — suggesting the true rate
   may be higher."* This is your unasked-for finding, not required, but
   cheap and directly tied to what Neha actually said.

This replaces the v1 "biggest complaint category" approach. Keep that as a
fallback only if the repeat-contact numbers turn out too small or too noisy
to be a compelling headline once you see the real data.

---

## 8. Validation — two things to check now, not one

- **Category-tag audit:** sample ~100 tickets, read the `customer_message`,
  judge whether the bot's `category` (or the agent's correction) looks right.
  Report agreement %.
- **Repeat-contact join accuracy:** sample ~30–50 flagged repeat contacts,
  read both tickets, confirm they're actually about the same issue (not a
  false positive from the category/sku proxy matching unrelated issues).
  Report a precision estimate.
- Both become submission-form answers and memo lines, same as before.

---

## 9. Cost estimate — now grounded in Arjun's actual concern

Template, same shape as before, but explicitly answer "no surprise bill":

```
Category-tag audit: ~100 tickets × 1 short LLM call each
"Already told you" sweep: ~1 short LLM call per ticket, but only over
  customer_message (short text), on the full ticket set OR a recent window
  — decide based on time/cost tradeoff and say which you chose
Cost per call:                          ₹Z
Total one-time run cost:                ₹Z × N
Vireo's volume: ~650 tickets/week → ~2,600/month
Monthly cost if the sweep runs weekly on new tickets only (not the full
  18-month backlog every time):         ₹Z × 650/week ≈ ₹[monthly]
```

The "runs weekly on new tickets only, not a full backlog re-scan" framing is
what directly answers Arjun's "surprise bill in November" worry — say this
explicitly in the memo, it's a one-line reassurance that costs you nothing
to include.

---

## 10. What each deliverable maps to

| Submission form question | Comes from |
|---|---|
| What did you build / business outcome | §7 repeat-contact number + digest + leaderboard |
| Cost per run / per month | §9 |
| How do you know it works | §8 |
| Did you change/narrow/push back on the ask | §3 (note: dropped taxonomy-building, added repeat-contact framing not literally asked for) |
| What's wrong with what you're handing in | Known limitations §11 |
| What did you leave out and why | §3 |
| Anything unasked-for | The repeat-contact metric itself, plus the "already told you" language sweep — both go beyond the literal digest/leaderboard ask |
| What did you use AI for | Category audit + language sweep + memo drafting — log as you go |
| Three things for Monday | Where the 30-day repeat-contact window logic lives, the Tier 2 exclusion rule, biggest known gap |
| Honest hours | Track from first prompt |

---

## 11. Repo structure (adds a repeat-contact module)

```
vireo-support-tool/
  docs/                       # this file + build prompts + memo + design + video script + form answers
  README.md
  data/                       # gitignored
  src/
    profile_data.py
    data_quality.py           # csat normalization, refund scale check, dedupe, join fallback
    category_audit.py         # replaces build_taxonomy.py from v1
    repeat_contacts.py        # the core business-goal input
    weekly_digest.py
    leaderboard.py
    business_goal.py
    validate.py
  reports/
    digest_latest.html
    leaderboard_latest.html
  validation/
    category_audit_sample.csv
    repeat_contact_sample.csv
    validation_report.md
  memo.md
  requirements.txt
  .env.example
```

---

## 12. Known risks / data-quality gotchas — confirmed, not hypothetical

- **CSAT 0-vs-blank:** legacy rows use `0` for no response; must normalize
  before any average, or your CSAT numbers (if you report any) are simply wrong
- **Legacy monetary unit risk:** §9 says the legacy tool stored money in "its
  own native unit" — sanity-check `refund_amount_inr` distribution by
  `source_system` before trusting it in any cost calc
- **Legacy ticket ID oddities:** Sameer's email warns some IDs "will look
  odd" from re-import — check for duplicates before counting
- **Tier 2 leaderboard exclusion is not optional** — it's a policy rule and
  an explicit client ask, not a nice-to-have
- **`status == "closed"` alone undercounts real work** — use
  `resolved + closed` together per the policy's Attendance definition
- **"Same issue" for repeat-contact matching is a proxy, not ground truth** —
  you're matching on `category`/`product_sku` because there's no direct
  issue-link field; say this plainly in the memo as a stated assumption
- **PII in free text:** `customer_message`/`agent_notes` may contain names,
  order numbers, phone numbers — never put raw excerpts in your public GitHub
  repo's example outputs; paraphrase or synthesize examples instead
