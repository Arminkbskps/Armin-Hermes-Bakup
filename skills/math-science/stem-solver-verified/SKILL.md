---
name: stem-solver-verified
description: "Use when solving math, physics, or chemistry problems."
version: 1.0.0
author: Armin & Hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [stem, math, physics, chemistry, sympy, chempy, verification]
---

# STEM Solver & Symbolic Verifier

Procedure for solving high school (Sampad / Konkur / Olympiad) mathematics, physics, and chemistry problems with 100% calculation reliability.

## Procedure
1. **Model & State**: Extract all given variables, constraints, and target unknowns.
2. **Formal SymPy / ChemPy Execution**:
   - Always run Python code in background to verify equations, roots, integrals, derivatives, limits, and chemical balances symbolically.
   - Never perform long algebraic divisions, large matrix determinants, or stoichiometric balancing in mental approximations.
3. **Step-by-Step Persian Solution & Delivery Rules**:
   - **Curriculum Calibration**: Explain clear conceptual steps following Iranian high-school curriculum standards (e.g. Grade 10 Lesson 2 trigonometry) without unsolicited calculus shortcuts.
   - **Tone & Register**: Keep the voice friendly, clear, and encouraging (صمیمی، دقیق، رفیقانه), explaining the intuition behind each algebraic step.
   - **Telegram Chat Formatting**: Convert all LaTeX to clean, readable Unicode math in chat prose (`sin²x`, `cos θ`, `α`, `√( ... )`, `±`, `(a / b)`); never leak unrendered LaTeX control codes.
   - **No Ugly Sketches**: Never draw crude ASCII art or sloppy text diagrams. Use exact vector SVG when figures are required, or rely on clean structured algebraic layout.
   - **Companion PDF Document**: Always compile and attach a clean, print-ready A4 PDF booklet with Vazirmatn font alongside the chat response.
   - State the final result clearly with units and four-choice option match (گزینه ۱، ۲، ۳ یا ۴).
