# Prompt 04 — Create the Azure Advisor Cost Optimization Live Report

Attach `reports/advisor-cost-optimization.html` and paste:

---

Create a Live Report from the attached template `advisor-cost-optimization.html` using the `advisor-cost-optimization` skill, for every in-scope subscription in `cost-environment.md`.

1. Copy the template to `tmp/advisor-<random>.html`.
2. Run the Advisor query and take 3 sample rows first to confirm the `extendedProperties` field names in this tenant. Then run the reservations GET call and the five orphaned-resource queries.
3. Replace ONLY the `var DATA = {...}` object between `// >>> DATA:report` and `// <<< DATA:report`, following the skill's output contract. Savings are annual numbers, not strings. Set `scopeLabel` to the subscription name(s) and ID(s) and `currency` to the real currency.
4. Save with name "Azure Advisor Cost Optimization" and `allowedTools: []`.
5. Put the report ID into `cost-environment.md`. In the skill's memory notes, record any `extendedProperties` field-name differences you found.
6. Summarize the top 5 savings opportunities. Do not delete or change any resources.
