# Report Design Plan — Digest & Leaderboard Pages

Two internal reports, read by Priya (non-technical) and whoever inherits this on
Monday. Not a marketing page — the job is fast comprehension, not persuasion. The
design should look like it came from someone who thinks about consumer audio
hardware, not from a generic SaaS-dashboard template. Budget: this should take
you 15–20 extra minutes on top of what Stage 4/5 already costs — it's CSS on top
of the report scripts you're already building, not a separate project.

---

## Design plan

**Grounding:** Vireo makes physical audio hardware — earbuds, headphones, speakers,
watches. The visual language should nod to that world (signal, levels, frequency,
precision) without being a literal waveform-image cliché plastered everywhere.

**Color** (paper-light, not dark-mode — this gets read in daylight, in a hurry):
- `--paper: #F6F5F1` — background, warm off-white, not the flagged AI-cliché cream
- `--ink: #1B1D1F` — primary text, near-black not pure black
- `--rule: #C9C6BE` — hairline dividers, borders
- `--signal: #2F6F62` — primary accent (muted teal-green, evokes a level meter's
  "good" zone) — used for the single most important number per page, nothing else
- `--spike: #B5482F` — used only on data that's genuinely trending up/worse
  (a rising complaint category), never as decoration
- `--muted: #6B6862` — secondary text, captions, timestamps

**Type:**
- One grotesk sans for everything (body + numbers): something with real
  personality, not the default — e.g. **Space Grotesk** or **IBM Plex Sans**
  for a slightly technical, hardware-spec-sheet feel. Load from Google Fonts
  with a system-stack fallback (`ui-sans-serif, system-ui, sans-serif`) in case
  the machine viewing it is offline.
- Numbers (ticket counts, percentages, ₹ figures) get **tabular figures**
  (`font-variant-numeric: tabular-nums`) so columns of numbers actually align —
  this one detail does more for a "considered" feel than almost anything else.
- Type scale: page title 28px/1.15, section headers 16px/600 weight, body 14px,
  captions/timestamps 12px in `--muted`. Don't add a second display typeface —
  weight and size carry the hierarchy.

**Layout — digest page (ASCII wireframe):**
```
┌────────────────────────────────────────────┐
│ Weekly Support Digest                       │
│ Week of [date]–[date]              [--muted]│
├────────────────────────────────────────────┤
│ ▍ Top mover this week           [--signal]  │
│ ▍ [Category name]  [X]%  ▲[delta]pp         │
│   ["one representative complaint, plain    │
│    text, not a quote block"]                │
├────────────────────────────────────────────┤
│ All categories, ranked                      │
│ Category            Count   Δ vs last week  │
│ ──────────────────────────────────────────  │
│ [row]                                       │
│ [row]                                       │
│ [row]  ← rows with --spike deltas get a     │
│         small ▲ in --spike color, nothing   │
│         else changes per-row (no card per   │
│         category, no rounded chips)         │
└────────────────────────────────────────────┘
```
One real hierarchy device: a left-side vertical rule (▍) in `--signal` marking
the single top-mover callout, so the eye lands there first. Everything else is a
plain ranked table — resist the urge to turn each category into its own card;
a table of 10-15 rows is more scannable than 10-15 boxes.

**Layout — leaderboard page:**
```
┌────────────────────────────────────────────┐
│ Agent Leaderboard                           │
│ Week of [date]–[date]                       │
├────────────────────────────────────────────┤
│ Rank  Agent          Closed   vs last week  │
│ ──────────────────────────────────────────  │
│  1    [name]           [n]      [±n]        │
│  2    [name]           [n]      [±n]        │
│  ...                                        │
├────────────────────────────────────────────┤
│ Note: ranked by tickets closed only — does  │
│ not account for ticket difficulty.  [--muted, 12px, one line]│
└────────────────────────────────────────────┘
```
The one-line caveat at the bottom is not decoration — it's the honest disclosure
from your memo's "known limitations," restated where whoever reads the
leaderboard will actually see it before drawing conclusions from rank alone.

**Principles:**
1. One accent color used exactly once per page for the single most important
   thing (the top-mover callout on the digest, nothing equivalent needed on the
   leaderboard). Everything else is ink-on-paper with a hairline rule.
2. Tables over cards. This is dense operational data for people who read it
   weekly — cards look good in a portfolio screenshot and slow down real reading.
3. No rounded-corner-and-shadow treatment on every block ("SaaS card kit").
   Flat, hairline-bordered sections only.
4. No tracked-out ALL-CAPS labels, no em-dash "WORD — fragment" headers, no →
   arrows on links. Plain sentence case throughout — this is an internal ops
   report, not a landing page.
5. Numbers align. Tabular figures, right-aligned number columns, consistent
   decimal places.

---

## Self-check against generic-AI-design defaults

- Not cream-background + terracotta accent (different palette, different accent
  hue and role — teal/green used once per page, not as a brand wash)
- Not dark-mode + neon accent
- Not the SaaS card kit (explicitly chose tables over cards, no shared
  border-radius-plus-shadow treatment)
- No tracked-out eyebrow labels, no middle-dot meta strings, no → on links —
  checked against the principles list above
- Numbered markers not used anywhere (nothing here is a sequence/process)

---

## Ready-to-use prompt for your coding agent

Paste this in after Stage 4 and Stage 5's data-generation scripts already work —
this is a styling pass on top of working reports, not a rewrite of the logic.

```
Restyle reports/digest_latest.html and reports/leaderboard_latest.html (keep the
data-generation logic in weekly_digest.py and leaderboard.py exactly as is, this
is CSS/HTML structure only) using this design system:

CSS variables:
  --paper: #F6F5F1
  --ink: #1B1D1F
  --rule: #C9C6BE
  --signal: #2F6F62
  --spike: #B5482F
  --muted: #6B6862

Typography: Space Grotesk from Google Fonts (link tag, with a fallback stack of
ui-sans-serif, system-ui, sans-serif in case the page is opened offline). Page
title 28px/1.15/600, section headers 16px/600, body 14px/1.5, captions 12px in
--muted. Apply font-variant-numeric: tabular-nums to every number in a table so
columns align.

Digest page layout:
- Header: report title, week date range in --muted, no logo/branding needed
- A single top-mover callout block with a 4px left border in --signal, showing
  the category name, its share this week, and the week-over-week delta with a
  ▲ or ▼ marker, plus one representative example ticket in plain text (not a
  blockquote-styled box, just indented plain text)
- Below that: a plain table of all categories ranked by count, columns
  Category / Count / Δ vs last week, hairline row dividers (--rule), right-
  aligned numeric columns, rows where the delta is positive and above a
  meaningful threshold get the delta number colored --spike
- No rounded corners, no box-shadows, no per-category cards

Leaderboard page layout:
- Header: report title, week date range
- A plain ranked table: Rank / Agent / Tickets closed / Δ vs last week,
  hairline dividers, right-aligned numbers
- A one-line caveat in --muted, 12px, below the table: "Ranked by tickets
  closed only — does not account for ticket difficulty."

Both pages: max content width ~720px, centered, generous whitespace (32-40px
section padding), background --paper, text --ink. Responsive down to mobile
(single column, table scrolls horizontally inside a contained wrapper rather
than the page scrolling sideways). No JavaScript needed — these are static
generated reports.

Show me both rendered pages when done.
```
