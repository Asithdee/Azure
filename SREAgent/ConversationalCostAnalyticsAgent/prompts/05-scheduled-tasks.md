# Prompt 05 — Weekly refresh scheduled tasks

Paste after prompts 02–04 have created the reports. The agent fills in the IDs from `cost-environment.md`.

---

Create these two scheduled tasks. Use the report IDs and subscriptions from `cost-environment.md`, then write the task IDs back into that file.

**Task A — "Weekly Cost Report Refresh"** · cron `0 7 * * 1` (Mondays 07:00 UTC) · new thread per run: no (same thread)

Agent prompt for Task A:
> Read `memories/synthesizedKnowledge/cost-environment.md` and the `cost-month-to-month` skill. For the in-scope subscriptions, query the current month (MTD) and the previous full month per ResourceId+ServiceName, plus the last-12-month trend by ServiceName. Call GetReport for the Month-to-Month report ID, replace only the DATA:monthlyData, DATA:resources and DATA:dates blocks and the refresh-text span, and save with the same reportId and allowedTools []. Then refresh the Subscription Cost & Budget report the same way with the `budget-overview` skill (DATA:report block). Post a summary: MTD, projected, previous month, delta %, top 3 movers, new resources, budgets over 80%. If a query fails with authorization or throttling, say so in the summary and don't overwrite the report with partial data.

**Task B — "Weekly Advisor Cost Optimization Refresh"** · cron `0 8 * * 1` (Mondays 08:00 UTC)

Agent prompt for Task B:
> Read `memories/synthesizedKnowledge/cost-environment.md` and the `advisor-cost-optimization` skill. Re-run the Advisor, reservations and orphaned-resource queries for the in-scope subscriptions. Call GetReport for the Advisor report ID, replace only the DATA:report block, and save with the same reportId and allowedTools []. Post a summary of total annual savings available and any new orphaned resources compared with the previous snapshot. Read-only: do not modify or delete resources.
