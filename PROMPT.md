# Credit Intelligence Brief — Autonomous Generation Prompt
# Used by GitHub Actions + Claude Code. Run daily, no human required.

You are generating the Credit Intelligence Brief for today. This is a fully autonomous run — do not ask questions. Make decisions and proceed.

---

## STEP 1 — Determine Edition Number and Date

Read `brief-archive.html`. Find the highest edition number in the `briefs` array (look for `edition: "XXX"`). The new edition number is that value + 1 (zero-padded to 3 digits).

Today's date: run `date +"%Y-%m-%d"` and `date +"%A, %B %-d, %Y"` in bash to get the file-safe date and the display date.

The output file is: `briefs/brief-YYYY-MM-DD.html`

---

## STEP 2 — Run 7 Parallel Research Searches

Use WebSearch to research the following 7 areas. Search for news from the last 24–48 hours. Collect specific claims, numbers, and sources before writing anything.

1. **FOMC / Federal Reserve** — rate decisions, Fed speeches, forward guidance, inflation data (CPI, PCE), rate path expectations
2. **Private credit / commercial credit** — defaults, redemption gates, fund stress, CLO issuance, lending standards (SLOOS), delinquency rates
3. **Diesel / fuel prices** — EIA weekly retail diesel price, EIA Short-Term Energy Outlook, fleet cost data
4. **Payments / fintech** — BNPL delinquency, stablecoin regulation (GENIUS Act), OCC charter activity, instant payments, embedded finance
5. **Credit risk / macro** — commercial real estate, C&I loan volumes, covenant trends, SMB credit access, SBA data
6. **Trade policy / tariffs** — Section 301 investigations, Section 122 tariff status, Trump-Xi negotiations, tariff expiry dates
7. **Banking regulation** — Basel III endgame, OCC/FDIC/Fed rule changes, fintech charter applications, CFPB activity

---

## STEP 3 — Truth Layer

Before writing, verify every specific claim you plan to use:
- Every number must have an explicit source and date
- No paywalled sources
- No extrapolation beyond what sources state
- Cross-check any claim that appears in only one source
- Flag any claim you cannot verify — omit it rather than include it unverified
- All data must be from the last 7 days OR be explicitly dated when cited

Count: verified claims, sources cited, cross-checked claims. These go in the Validation Bar.

---

## STEP 4 — Read the Latest Brief for Format Reference

Read `briefs/brief-2026-04-27.html` (or the most recent file in `briefs/` — run `ls -t briefs/brief-20*.html | head -1` to find it). Study the full HTML structure so your new brief matches it exactly.

Key structural elements to match:
- `<header class="brief-header">` with edition badge, h1, h2 headline, header-meta spans
- Action bar with print + share buttons
- Validation bar (✓ claims verified, sources cited, cross-checked, paywalled, dated)
- Bias Legend (3 axes: Monetary, Regulatory, Business)
- 8 sections with exact class names: `section-label` + `section-title`
- `story-card` blocks with `story-head`, `story-body`, `synthesis-box`, `story-footer`, `other-side`
- `macro-signal-card` for Section 02
- Chart.js charts (2 charts minimum, loaded from cdnjs.cloudflare.com)
- `thought-seed` block with academic paper translation
- Footer with edition info and archive link

The CSS is at `<link rel="stylesheet" href="brief-style.css">` — use the same link.

---

## STEP 5 — Generate the Brief

Write the complete HTML file. Required sections:

**Section 01 — Executive Brief** (2 story-cards minimum)
- Lead story: the single most important credit-relevant event from the last 24 hours
- Second story: the second most important development
- Each story: 3 paragraphs minimum, synthesis-box, source citations with badge types (gov/trade/synth/data), bias meters (3 axes), "Other Side" steel-man counterargument

**Section 02 — Macro Signal**
- macro-signal-card format
- 2 Chart.js charts (fed rate path, diesel trend, gate wave, tariff timeline, or other data-driven chart relevant to today)
- Specific credit action paragraph at bottom

**Section 03 — Fuel Card & Fleet Intelligence**
- story-card format
- Current EIA weekly diesel price
- Fleet credit portfolio implications
- Synthesis box with specific portfolio action

**Section 04 — Deep Dive**
- story-card format
- 3-paragraph analysis of the week's most complex credit story
- Synthesis box with 2 specific credit actions

**Section 05 — Emerging Risks**
- story-card format with `border-top-color:#e74c3c`
- A risk that is building but not yet in mainstream coverage
- Watch list synthesis box

**Section 06 — Data Snapshot**
- 6 metric tiles (28px bold number + label each)
- Each tile: background #f0f3f7, border-radius 6px
- Grid: `grid-template-columns: repeat(3, 1fr)`

**Section 07 — SMB Pulse**
- story-card format
- SMB lending standards, SBA developments, credit access trends
- Synthesis box framing the origination opportunity

**Section 08 — Thought Seed**
- Academic paper: choose a paper directly relevant to today's lead story
- Paper must be: real, cited correctly (journal, year, authors), highly cited (>500 citations preferred)
- Required sub-sections: "What the Paper Says" (3 paragraphs), "Why This Matters Right Now" (2 paragraphs), "Original Commercial Credit Translation — Not in the Paper" (3 specific diagnostic tools or frameworks derived from the paper), "Implementation Path" (5 bullet steps), Confidence Level (🟢/🟡/🔴), "Steel-Manned Counterargument"

**Writing standards:**
- No bullet points in body text — prose paragraphs only
- Minimum 3 paragraphs per story-card
- Every claim cited inline in the source box
- Bias meter dots: percentages 0% = hawk/interventionist/incumbent, 100% = dove/free-market/disruption
- The headline (h2) must be specific and dense — it should function as a one-paragraph summary
- The header-meta macro ticker spans must list 8–10 specific data points with × separators

---

## STEP 6 — Format Pre-Flight Check

Before saving, verify:
- [ ] Edition number is correct (last + 1)
- [ ] Today's date appears in title, header, footer, share links, email links
- [ ] CSS link is `href="brief-style.css"` (not a full path)
- [ ] Archive link in footer is `href="../brief-archive.html"`
- [ ] Chart.js loaded from `https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js`
- [ ] All 8 section-label + section-title pairs present
- [ ] Both Chart.js charts have unique canvas IDs referenced in the script
- [ ] Thought Seed paper is real and citation is accurate
- [ ] Share email link has today's date and edition number encoded correctly
- [ ] Footer shows correct edition number and date

---

## STEP 7 — Save the Brief

Write the complete HTML to `briefs/brief-YYYY-MM-DD.html`.

---

## STEP 8 — Update brief-archive.html

Read `brief-archive.html`. In the JavaScript `const briefs = [` array, insert a new entry as the FIRST item (before the current first entry). Format:

```javascript
  {
    date: "MONTH DAY, YEAR",
    dateSort: "YYYY-MM-DD",
    edition: "NNN",
    file: "briefs/brief-YYYY-MM-DD.html",
    headline: "EXACT HEADLINE FROM THE BRIEF H2",
    thoughtSeed: "AUTHOR (JOURNAL YEAR) — 'PAPER TITLE' — ONE SENTENCE ON THE COMMERCIAL CREDIT ANGLE",
    tags: ["credit", "risk", "macro", "fuel", "smb", "payments", "regulatory"],
    readTime: "~20 min",
    macro: "KEY DATAPOINT 1 × KEY DATAPOINT 2 × KEY DATAPOINT 3 × KEY DATAPOINT 4 × KEY DATAPOINT 5"
  },
```

The `tags` array should only include tags relevant to this edition's content. Available tags: `credit`, `risk`, `macro`, `fuel`, `fleet`, `smb`, `payments`, `regulatory`, `em`.

The `macro` field should be 5–8 specific data points from the brief separated by ×.

---

## STEP 9 — Git Commit and Push

Run these bash commands in the repo root:

```bash
git config user.email "mohnishraj77@gmail.com"
git config user.name "Mohnish"
git add briefs/brief-YYYY-MM-DD.html brief-archive.html
git commit -m "Add Edition #NNN — MONTH DAY, YEAR (Credit Intelligence Brief)"
git push origin main
```

Replace YYYY-MM-DD, NNN, MONTH DAY, YEAR with the actual values.

The push will succeed because GitHub Actions provides a pre-authenticated GITHUB_TOKEN with write access to the repository.

---

## STEP 10 — Report

Output a brief confirmation:
- Edition number and date
- File path of the new brief
- Number of claims verified, sources cited
- The Thought Seed paper chosen and why
- Confirmation that git push succeeded (or the error if it failed)
- GitHub Pages URL: `https://mohnishraj.github.io/fintech-brief/briefs/brief-YYYY-MM-DD.html`
