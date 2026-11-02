# Prompt 06 — Ad-hoc prompts (copy as needed)

- **Why did cost change?** — "Using the cost-month-to-month skill, compare this month (projected) with last month for <subscription>. Show the top 10 resources by contribution to the change, new and stopped resources, and the likely cause for each top mover (check Resource Graph creation dates and Activity Log for SKU/tier changes)."
- **Specific month pair** — "Compare <YYYY-MM> with <YYYY-MM> (both full months) by ServiceName and ResourceId. Table plus bar chart of the top 15."
- **Cost by RG / region / type** — "Month-to-date cost for <subscription> grouped by ResourceGroupName (or ResourceLocation / ResourceType), with the delta vs last month."
- **Savings quick wins** — "Using the advisor-cost-optimization skill, list the top 10 savings opportunities with estimated annual savings and the exact az command I would run for each. Don't execute anything."
- **Budget check** — "Using the budget-overview skill, which budgets will exceed 100% by month end at the current run rate?"
- **Refresh one report now** — "Refresh the <report name> Live Report now, following the refresh workflow in the cost-analysis playbook."
- **New tenant sanity check** — "Re-verify every query in the three cost skills in this environment and update cost-environment.md with what works and what doesn't."
