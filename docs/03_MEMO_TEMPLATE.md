# Memo template — memo.md

Fill in every `[ ]` with a real number or sentence once your pipeline has run. Keep the
whole thing to one page / ~11 minutes of reading. No jargon, no code, no screenshots
of terminal output — Priya is Head of Customer Experience, not an engineer.

---

```markdown
# Weekly Support Insight Tool — Summary for Priya

**From:** [Your name]
**Date:** [date]

## The short version

We built a tool that reads every support ticket's opening message and closing note,
sorts complaints into [N] categories, and produces a weekly digest plus an agent
leaderboard automatically. Running it on your 18 months of data, one problem stands
out clearly:

**[Category name] tickets are currently [X]% of all tickets — costing Vireo
roughly ₹[A] a quarter.** Bringing that down to [M]% would save about ₹[B] a
quarter.

## What the tool does

Every week, it will hand you:
1. A ranked list of what customers are complaining about, and whether each is
   getting more or less common vs. the week before.
2. A few real examples per category, so you can see the actual words customers use,
   not just a number.
3. An agent leaderboard: tickets closed per agent per week.

## The number, in full

- [Category] made up [X]% of tickets between [date range].
- Based on your support policy, each [category] ticket costs approximately
  ₹[cost] in [replacement / refund / agent handling time — whichever applies].
- At current volume (~[T] tickets/quarter in this category), that's ≈ ₹[A]/quarter.
- A realistic target of [M]% (a [X-M] point drop) would save ≈ ₹[B]/quarter.
- [One sentence on *why* you picked this category over others — biggest $ impact,
  not just biggest count.]

## How much we trust this

We hand-checked [N] tickets against the tool's category assignments ourselves.
It matched a human [accuracy]% of the time. It mostly struggles with
[one concrete failure mode, e.g. "tickets that describe two problems at once"].
We'd treat the weekly digest as directionally reliable, not as a precise count,
until [suggested next step, e.g. "we tune it on a larger hand-labeled set"].

## What we didn't build (on purpose)

Given the time we had, we chose not to build:
- [item 1, one line why]
- [item 2, one line why]

These are quick to add later if useful.

## What we'd do next, if this moves forward

- [1-2 concrete next steps, e.g. "extend the taxonomy to product-line-specific
  issues," "add a root-cause flag when a category spikes sharply in one week"]

## Three things for whoever picks this up

1. [e.g. "The category list is frozen in taxonomy.json — don't regenerate it without
   review, it's what makes weeks comparable to each other."]
2. [e.g. "Classification results are cached by ticket ID — re-running the pipeline
   is cheap, it won't re-pay to classify tickets it's already seen."]
3. [e.g. "The biggest known gap is X — see the README's Known Limitations section."]
```

---

## Notes on filling this in well

- **Lead with the number.** Priya's first question will be "so what should I do."
  Don't make her read four paragraphs to find it.
- **Show the arithmetic once, in the "number in full" section, then stop.** One clear
  calculation earns more trust than three vague ones.
- **The "what we didn't build" and "what's wrong with this" sections are worth writing
  honestly** — the brief says these can only raise your score, and a memo that admits
  a real limitation reads as more credible than one that doesn't.
- **Don't paste raw customer complaint text into the memo** if it contains anything
  identifying (order numbers, phone numbers) — paraphrase the example instead of
  quoting it verbatim.
- Keep total length to roughly 400-500 words. If it's running long, cut from
  "what we'd do next" before cutting the number or the validation section.
