---
name: superforecasting
description: "Probabilistic forecasting, scenario analysis, and prediction science."
version: 1.0.0
author: Philip Tetlock Good Judgment Project principles + Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [forecasting, prediction, superforecasting, probability, bayesian, scenario-planning, analysis, intelligence]
    category: research
    related_skills: [polymarket, stocks, competitor-news-monitor, dcf-model]
---

# Superforecasting & Probabilistic Prediction Skill

Produce disciplined, calibrated probabilistic forecasts for geopolitics, technology (AGI timelines, model releases), economic events, financial outcomes, and startup decisions.

Grounded in the science of **Philip Tetlock’s Superforecasting**, the **Good Judgment Project**, and **Metaculus** standards.

---

## When to Use

- User asks: "What is the probability of X happening by year Y?"
- User asks for future predictions, scenario planning, or "will event Z occur?"
- User asks to forecast technology milestones, market shifts, or geopolitical risks.
- User wants an analytical, calibrated prediction rather than vague fortune-telling.

---

## Core Tenets of Superforecasting

1. **Precision Over Vagueness:**
   - Ban vague words like "soon", "likely", "significant risk", "may happen".
   - Replace with exact calibrated numerical probabilities (e.g. `68%`, not "probably") and definite resolution criteria with dates.

2. **Outside View First (Base Rate Anchor):**
   - Before analyzing the specific case (Inside View), establish the historical frequency of similar events.
   - *Example:* "How often do tech acquisitions above $10B succeed?" Anchor to the historical base rate (e.g., 30%) before adjusting for company specifics.

3. **Fermi Decomposition:**
   - Break an unanswerable question into manageable sub-components:
     $$P(\text{Outcome}) = P(A) \times P(B \mid A) \times P(C \mid A \cap B)$$
   - Combine uncertainty intervals rather than guessing single-point estimates.

4. **Bayesian Belief Updating:**
   - When new evidence emerges, calculate its Diagnostic Ratio / Bayes Factor:
     $$\text{Posterior Odds} = \text{Prior Odds} \times \frac{P(\text{Evidence} \mid \text{Hypothesis})}{P(\text{Evidence} \mid \neg\text{Hypothesis})}$$
   - Update beliefs incrementally; avoid overreacting to noise or underreacting to real signals.

5. **Pre-Mortem & Counter-Factual Stress Testing:**
   - Assume your forecast failed completely: *Why did it fail? What blind spots were ignored?*
   - Identify "Dragon Kings" (rare, high-impact systemic shifts) and black swans.

---

## The 5-Step Forecasting Procedure

### Step 1: Clarify the Resolution Criteria
Define the exact question, the resolution date, and objective proof sources (e.g., "Will Anthropic release Claude 4 by Dec 31, 2026, confirmed via official blog or press release?").

### Step 2: Establish the Outside View (Base Rate)
Search historical precedents. What is the average time between flagship model releases? What is the base rate of similar startups reaching profitability?

### Step 3: Weigh the Inside View (Evidence & Drivers)
Enumerate driving forces:
- **Tailwinds (Forces pushing for YES)**
- **Headwinds (Forces pushing for NO)**
Assign qualitative/quantitative weights to each driver.

### Step 4: Quantitative Calculation (CLI Helper)
Run the bundled helper in terminal:
```bash
SCRIPT=~/.hermes/skills/research/superforecasting/scripts/forecast_tools.py

# 1. Update belief based on evidence strength
python3 $SCRIPT bayes 0.35 2.2

# 2. Fermi estimation across confidence bounds
python3 $SCRIPT fermi 2,4 1.5,3.0 10,25

# 3. Monte Carlo arrival time projection
python3 $SCRIPT mc 18 5 --target 12
```

### Step 5: Deliverable Structure
Present a structured forecast card:
- **Central Probability Estimate:** (e.g., `72% [60% - 82% 80% CI]`)
- **Key Cruxes & Drivers:** (Top 3 factors that would change the forecast)
- **Base Rate vs Current Stance:** Why we deviate from the base rate
- **Pre-Mortem (Failure Scenarios):** What could make this forecast wrong
- **Indicators to Watch:** Leading signals that warrant an immediate Bayesian update
