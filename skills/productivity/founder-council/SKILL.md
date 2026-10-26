---
name: founder-council
description: "Use when stress-testing business decisions with 7 advisors."
category: productivity
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [business, advisory-council, roast-room, decision-making, pricing, strategy, executive-report, pdf]
---

# Founder Council (The Roast Room Protocol)

Convene an executive advisory council of seven specialized operators to debate and stress-test hard business, pricing, hiring, scaling, or product decisions across three structured rounds, culminating in a scored verdict and an executive PDF deliverable.

## The Seven Seats & Pillars

| Seat | Operator | Pillar | Core Question Owned |
| :--- | :--- | :--- | :--- |
| **Bezos** | Jeff Bezos | Strategy & Reversibility | Is this the right bet, and is it a Type 1 (irreversible) or Type 2 (two-way) door? |
| **Graham** | Paul Graham | Product & Hyper-Fans | Do people actually want this, and does it do things that don't scale first? |
| **Hormozi** | Alex Hormozi | Offers, Pricing & Margins | Will people pay, how much, and what are the unit economics (volume vs margin)? |
| **Gary V** | Gary Vaynerchuk | Attention & Culture | Where does the organic attention come from, and how is the story documented? |
| **Martell** | Dan Martell | Founder Time & Calendar | Who executes this, what is the Buyback Rate, and does it destroy the founder's focus? |
| **Wickman** | Gino Wickman | Operations & Core Focus | Does this align with the Core Focus, and is there a clean single 5-step SOP? |
| **Buffett** | Warren Buffett | Capital & Margin of Safety | What is the downside risk, is cash preserved, and is there inventory suicide risk? |

---

## The 4-Step Council Procedure

### Step 1: Formulate the Decision Brief
Structure the decision strictly around:
1. **The Core Question**: One clear line.
2. **Options A, B, and C**:
   - Option A: The focused, high-margin, or boutique path (usually limited-batch or high-ticket).
   - Option B: The mass-scale, platform, or volume path (always-on, outsourced, low-margin).
   - Option C: The digital, community, or alternative hybrid path.
3. **Founder Constraints**: Real-world time availability (hours/week), financial runway, and external commitments (e.g. academic exams, full-time job).
4. **Seat Weights (1 to 3)**: Assign higher weights to pillars matching the primary risk (e.g. Martell = 3 if founder has severe time constraints; Hormozi = 3 if pricing is the core puzzle).

### Step 2: Round 1 (Opening Cards) & Crux Identification
Each seat issues an independent opening card containing:
- **Stance**: Strong Yes, Conditional Yes, No.
- **Option Scores**: Rated 0–10 for each option.
- **Ruin Risk Flag**: `none`, `moderate`, or `critical` (vetoes the option if triggered).
- **The Core Argument**: Grounded in that expert's primary framework (Type 1/2 doors, Grand Slam offers, Negative Working Capital, Buyback Rate).

**Chair Unanimity Guard**: If Round 1 is unanimous, the Chair must identify the unargued counterweight and force the debate in Round 2. Do not accept immediate harmony.

### Step 3: Round 2 & 3 (Debate & Amendments)
- **Round 2 (Confrontation)**: Put the seats against each other on the primary "Cruxes" (e.g. Hormozi pushing high pricing vs Buffett insisting on verifiable quality; Martell defending founder calendar vs scale advocates).
- **Round 3 (Ratification)**: Vote on adopted amendments:
  1. *Cash Protection Amendment*: Negative Working Capital (pre-orders or customer deposits before production).
  2. *Calendar Firebreak Amendment*: Strict freeze on operational launches during critical founder examination or blackout windows.
  3. *Perceived Value / Club Amendment*: Bundling exclusive physical/digital numbered member tokens to elevate status.

### Step 4: Executive Bilingual / Persian PDF Generation
When the user requests an executive PDF deliverable in Persian or English, use the headless Chromium pipeline:
1. Construct a clean, modern HTML layout (`dir="rtl"` for Persian) with print CSS:
   - `@page { size: A4 portrait; margin: 14mm 14mm 16mm 14mm; }`
   - Include header, verdict banner with score pill, options comparison grid, advisor table, cruxes, and 90-day action steps.
2. Embed the Persian font (Vazirmatn) directly as a Base64 Data URI inside `@font-face` to eliminate cross-origin or local font-loading sandbox failures.
3. Render via headless Chromium:
   ```bash
   chromium --headless --no-sandbox --disable-gpu \
     --run-all-compositor-stages-before-draw \
     --print-to-pdf=/path/to/verdict.pdf /path/to/report.html
   ```
4. Verify page count and file size using `pypdf`, then provide the file path (`MEDIA:...`) and cloud backup link.

---

## Operational Pitfalls & Rules

- **The Founder Calendar Veto (Martell Rule)**: Never endorse an operationally complex, low-margin platform (Option B) for a solo founder with strict external time commitments (such as high school, university, or a primary job). The cognitive drain of customer service and logistics creates a catastrophic ruin risk.
- **Inventory Suicide (Buffett Rule)**: In physical goods and retail, reject self-funded massive batch production. Enforce pre-orders or micro-batches to ensure cash is collected before capital is committed to suppliers.
- **Visual Room Integration (`roast-room`)**: When running inside or alongside the `roast-room` workspace, save session files (`brief.md`, `round-1.md`, `round-2.md`, `round-3.md`, `verdict.md`, `events.json`) under `sessions/<date>-<slug>/` so the local dashboard (`http://localhost:4730`) automatically indexes and replays the meeting.
