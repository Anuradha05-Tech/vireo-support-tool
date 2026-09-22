# Submission Form — Answer Key

Draft these alongside the build, not after. Each one below has: what it's really
asking, a fill-in-the-blank draft, and a note on what makes a strong vs. weak answer.
Keep every answer tight — this form is read fast; nobody wants an essay per box.

---

### 1. What did you build, and what business outcome does it move? State the number and the money.

**Really asking:** can you connect a technical artifact to a dollar figure in two sentences.

**Draft:**
> Built a tool that classifies support tickets into [N] complaint categories and
> generates a weekly digest plus an agent leaderboard. [Category] accounts for
> [X]% of tickets, costing ≈ ₹[A]/quarter; cutting it to [M]% would save
> ≈ ₹[B]/quarter.

Weak version: describes the tool's features without ever stating a number. Always
lead with the number.

---

### 2. What does one run cost, and what would a month cost at Vireo's volume (roughly 650 tickets a week)?

**Really asking:** can you do the unit-economics arithmetic and did you actually run it.

**Draft:**
> One classification call: [X] tokens in / [Y] out ≈ ₹[Z]. Full run on [N] tickets
> ≈ ₹[total]. At 650 tickets/week (≈2,600/month): ≈ ₹[monthly]. [If free/local
> model: "Ran on [model] locally — ₹0 marginal cost per ticket."]

Show the arithmetic, don't just state a final number — this question is explicitly
testing whether you can show your work.

---

### 3. How do you know it works? Sample size, how you checked, error rate, and the kind of case it gets wrong.

**Really asking:** did you validate or did you just ship it.

**Draft:**
> Hand-labeled [N] tickets (stratified across categories) and compared to the
> model's output: [accuracy]% agreement. Most common failure: [concrete failure
> mode, e.g. "tickets describing two issues at once get assigned to whichever is
> mentioned first"].

Never answer this with just "it works well." Sample size and a real failure mode
are non-negotiable here.

---

### 4. Did you change, narrow, or push back on the client's ask? What, when, and why.

**Really asking:** do you have judgment, or did you just execute the literal brief.

**Draft:**
> Narrowed classification to single-label (one category per ticket) rather than
> multi-label — most tickets have one dominant issue, and single-label keeps the
> weekly digest comparable week to week. Chose not to rebuild the taxonomy on
> every run — froze it after initial discovery so category names stay stable
> and comparable over time, at the cost of it going stale if Vireo's product
> mix changes significantly.

Pull directly from Section 3 of `01_ARCHITECTURE.md` (your out-of-scope list) —
that's exactly this answer, already written.

---

### 5. What is wrong with what you are handing us? Be specific: bugs, shortcuts, things you know are off.

**Really asking:** can you self-critique honestly, or will you oversell your own work later.

**Draft:**
> [Concrete, e.g.] Taxonomy was built from a 300-ticket sample — rare complaint
> types may be under-represented or missing entirely. Single-label classification
> under-counts tickets that genuinely describe two problems. Business-cost figure
> uses [proxy] rather than an exact per-ticket cost, since the policy doc didn't
> break costs out at that granularity. Leaderboard counts raw tickets closed,
> which doesn't account for ticket difficulty — an agent who gets harder tickets
> looks worse on this metric for reasons unrelated to performance.

Be specific and real — this question explicitly can only help your score, so a
vague "nothing major" reads worse than a precise list of three real issues.

---

### 6. What did you deliberately leave out, and why that rather than something else?

**Really asking:** same as #4, but forward-looking — what didn't make the cut.

**Draft:**
> Left out: real-time ingestion (weekly batch matches what was actually asked),
> a multi-page interactive dashboard (one clean report answers the brief without
> the extra build time), and root-cause analysis of why a category spikes (would
> need more signal than ticket text alone — e.g. release dates — to do honestly
> rather than guess at).

Reuse Section 3 of the architecture doc again — say specifically why *these*
items lost out to what you kept, not just that you ran out of time.

---

### 7. Anything you built or found that nobody asked for?

**Really asking:** do you go beyond the literal spec when you see something useful.

**Draft:**
> [Fill in whatever you actually add — options, roughly in order of cheapness:]
> - Flagged which complaint category is trending up fastest month-over-month, not
>   just this week's top category — surfaces emerging problems earlier.
> - Broke the digest down by product line as well as category, since [product]
>   drives a disproportionate share of [category] complaints.
> - Noted a data quality issue nobody asked about (e.g. a gap in ticket dates for
>   one week, or an agent with no roster entry) that would silently skew the
>   leaderboard if not caught.

Pick ONE of these and actually build it if time allows — even the data-quality
catch counts and costs almost nothing to report.

---

### 8. What did you use AI for? Which tools and models, where they helped, where they wasted your time, what you threw away. Link your screen recording here.

**Really asking:** honest process transparency, matching what's in the video.

**Draft:**
> Used [Claude/GPT-X/etc.] for taxonomy discovery, ticket classification, and
> drafting this memo's prose. [Coding agent, e.g. Claude Code] for the pipeline
> scaffolding and scripts. AI was fast for the classification loop and slow/
> unhelpful for [something specific, e.g. "guessing exact cost figures from the
> PDF — it hallucinated a number once, I switched to extracting the text and
> reading it myself"]. Threw away [reuse your "what you threw away" video answer].
> Recording: [Drive link]

Name the actual failure, not a generic one — "it sometimes made mistakes" is
worthless here; "it hallucinated a cost figure and I caught it by cross-checking
the PDF" is a real, specific, creditable answer.

---

### 9. Your Public Google Drive Link

[Paste link. Confirm it's actually set to public before submitting — test in an
incognito window.]

---

### 10. Someone picks this up on Monday and you are unreachable. The three things they need to know.

**Really asking:** can you write for a stranger inheriting your code, not just for yourself.

**Draft:**
> 1. [e.g. "taxonomy.json is frozen by design — don't regenerate it without
>    review, categories need to stay stable across weeks to be comparable."]
> 2. [e.g. "classification results are cached by ticket_id in [file] — re-running
>    the pipeline only classifies new tickets, it won't re-spend on old ones."]
> 3. [e.g. "the business-cost number uses [proxy] as a stand-in for exact
>    per-ticket cost — see Known Limitations in the README before quoting it
>    externally."]

Pull straight from your README's "Known Limitations" section — if that section is
good, this answer writes itself.

---

### 11. Honest hours spent. One number.

Track from your very first prompt (including data exploration), not from when you
felt like "real work" started. If you go over 5 hours, say the real number — the
brief explicitly says going over isn't penalized as long as you're honest, and an
implausibly exact "5.0" looks worse than a real "6.25."

---

### 12. GitHub Repo Link (Public)

[Paste link. Confirm public visibility and that `data/` and `.env` are NOT
committed — check this in the actual GitHub UI, not just your local `.gitignore`,
since a file already committed before you gitignored it will still be there.]
