---
name: Cost Analysis Playbook (portable)
description: Environment-agnostic playbook for Azure cost analysis with SRE Agent - tool mapping, failed approaches to avoid, Live Report refresh workflow. Upload as a knowledge document in any new agent.
---

# Cost Analysis Playbook

Environment-specific values live in `{{...}}` placeholders. After import, the bootstrap prompt records the real
values in this agent's memory (`memories/synthesizedKnowledge/cost-environment.md`).

- Primary subscription: `{{SUBSCRIPTION_ID}}` ({{SUBSCRIPTION_NAME}})
- Billing currency: `{{CURRENCY}}`
- Live Reports: Month-to-Month `{{REPORT_ID_MOM}}`, Advisor `{{REPORT_ID_ADVISOR}}`, Budget `{{REPORT_ID_BUDGET}}`

## Skills
- `cost-month-to-month` — Cost Management queries, MoM math, 12-month trend.
- `advisor-cost-optimization` — Advisor recommendations, reservations, savings plans, orphaned resources.
- `budget-overview` — MTD / last month / forecast and budget utilization.

## Hard-won rules (verified in a previous environment; re-verify once in each new one)
| Do | Don't |
|---|---|
| Cost Management `query`/`forecast` via `RunAzCliWriteCommands` + `az rest --method post` | `RunAzCliReadCommands` with POST (rejected as a write) |
| Resource Graph and GET calls via `RunAzCliReadCommands` | `az costmanagement` (extension missing) or `az consumption usage list` (unavailable) |
| Parse `cliExecutionResult.output` as a JSON string | Run `az` in the terminal (not authenticated) |
| Bake data into Live Reports, `allowedTools: []` | Put built-in tools in `allowedTools` (rejected — only connector tools allowed) |
| Aggregate cost rows by ResourceId | Treat each row as one resource (one row per ServiceName) |

## Live Report refresh workflow (all three reports)
1. Run the skill's queries.
2. `GetReport(reportId)` → returns a working-copy HTML path.
3. Replace ONLY the code between `// >>> DATA:<name>` and `// <<< DATA:<name>` markers (keep markers).
4. Month-to-Month report also: update `DATA:dates` (`DAYS_ELAPSED`, `DAYS_IN_MONTH`) and the `refresh-text` span.
5. `SaveReport` with the same `reportId`, `allowedTools: []`. Never create a duplicate report.
6. Post a 5-line summary (total, projected, delta %, top 3 movers, new resources).

## Gotchas
- Current month is partial; cost lags 8–24 h.
- Requires Cost Management Reader on the scope for the agent's managed identity.
- 429 throttling → backoff, serialize multi-subscription loops.
- ActualCost vs AmortizedCost for reservations.
