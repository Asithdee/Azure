# Prompt 03 — Create the Subscription Cost & Budget Overview Live Report

Attach `reports/subscription-cost-budget.html` and paste:

---

Create a Live Report from the attached template `subscription-cost-budget.html` using the `budget-overview` skill, for every in-scope subscription in `cost-environment.md`.

1. Copy the template to `tmp/budget-<random>.html`.
2. Collect for each subscription: actual MTD, last month, end-of-month forecast (fall back to linear projection if forecast fails, and say so), and all budgets.
3. Replace ONLY the `const DATA = {...}` object between `// >>> DATA:report` and `// <<< DATA:report`, following the output contract in the skill. Use the real currency code.
4. Save with name "Subscription Cost & Budget Overview" and `allowedTools: []`.
5. Put the report ID into `cost-environment.md`, and tell me which budgets are over 100% (actual or forecast).
