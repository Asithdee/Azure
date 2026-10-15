---
name: azure-cost-analysis
description: "Analyze Azure cost changes month-over-month per subscription. Shows which subscriptions went up or down in cost, attributes the change to individual resources (percentage and dollar value vs the previous month), and identifies newly deployed resources with their contribution to the current month's spend. WHEN: cost increase, cost decrease, month over month cost, why did my bill go up, cost by subscription, which resources increased cost, new resources cost, spend analysis, cost trend, cost comparison, MoM cost, cost drivers, cost attribution. DO NOT USE FOR: deploying/changing resources, cost optimization recommendations/rightsizing (use azqr or advisor), real-time billing alerts."
license: MIT
metadata:
  author: SREAgent
  version: "2.0.0"
---

# Azure Cost Analysis

Analyze how Azure cost changed **month-over-month**, per subscription, and attribute the
change down to individual resources — including resources newly deployed this month.

This skill is **query-driven**: issue the Cost Management query and Azure Resource Graph
(KQL) queries directly with your available Azure tools. Do not run local scripts.

## When to Use This Skill

Use this skill when the user wants to:
- See the **cost increase or decrease** for each subscription, month by month.
- Understand **which resources** drove a cost change (with **dollar value and percentage**
  vs the previous month).
- Find **newly deployed resources** and their contribution to the current month's cost.
- Get a **tenant roll-up** ranking subscriptions by how much their cost moved.

> DO NOT USE for rightsizing/optimization recommendations (use `azure-compliance`/azqr or
> Azure Advisor) or for deploying resources.

## What It Answers

1. **Per subscription, per month** — total cost, the delta vs the previous month ($ and %),
   and direction (UP / DOWN / FLAT).
2. **Resource contribution** — for every resource: previous cost, current cost, delta,
   % change, and its share of the subscription's total change.
3. **New resources** — resources with cost this month but none last month, plus each one's
   percentage of the current month's total spend.

## Prerequisites

- **Cost Management Reader** (or Reader + Billing Reader) on each subscription in scope —
  required for the cost query.
- **Reader** on the subscription — required for the Azure Resource Graph enrichment.

## Data Sources

| Need | Source | Why |
|------|--------|-----|
| Cost / $ amounts per resource per month | **Cost Management Query API** | Azure Resource Graph has **no** cost/billing data |
| New-resource detection, resource metadata, creation time | **Azure Resource Graph (KQL)** | Fast inventory and `properties.createdTime` |

> ⚠️ **Azure Resource Graph does not contain cost.** Use it only for resource inventory and
> metadata. All dollar amounts come from the Cost Management query below.

## Workflow

### Step 1 — Determine scope

Identify the subscription(s). For all subscriptions, enumerate them first with Resource Graph:

```kql
ResourceContainers
| where type == "microsoft.resources/subscriptions"
| project subscriptionId, name = tostring(properties.displayName), state = tostring(properties.state)
| where state == "Enabled"
```

### Step 2 — Pull monthly cost grouped by resource (Cost Management)

Issue a POST to the Cost Management query endpoint for each subscription. Use `Monthly`
granularity grouped by `ResourceId`, covering the months you want to compare.

```
POST https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.CostManagement/query?api-version=2023-11-01
```

Request body:

```json
{
  "type": "ActualCost",
  "timeframe": "Custom",
  "timePeriod": { "from": "2026-08-01T00:00:00Z", "to": "2026-10-01T23:59:59Z" },
  "dataset": {
    "granularity": "Monthly",
    "aggregation": { "totalCost": { "name": "PreTaxCost", "function": "Sum" } },
    "grouping": [ { "type": "Dimension", "name": "ResourceId" } ]
  }
}
```

See [references/cost-management-api.md](references/cost-management-api.md) for the response
shape, column handling, and gotchas.

### Step 3 — Compute the month-over-month comparison

From the returned rows (each row = one `ResourceId` + one month + `PreTaxCost`), build a
per-resource table of previous-month vs current-month cost, then calculate:

| Metric | Formula |
|--------|---------|
| Subscription delta | `currentTotal - previousTotal` |
| Subscription % change | `delta / abs(previousTotal) * 100` |
| Resource delta | `resourceCurrent - resourcePrevious` |
| Resource % change | `(cur - prev) / abs(prev) * 100` — mark `NEW` when `prev == 0` |
| Contribution to change | `resourceDelta / abs(subscriptionDelta) * 100` |
| New resource | `prev == 0 && cur > 0` |
| New resource share | `newResourceCost / currentTotal * 100` |

Rank resources by **absolute delta** to surface the biggest drivers of the change.

### Step 4 — Enrich / confirm new resources (Azure Resource Graph)

For resources flagged as new (cost this month, none last month), confirm and enrich with
Resource Graph. This also catches resources deployed this month that have not yet accrued
cost:

```kql
Resources
| where todatetime(properties.createdTime) >= startofmonth(now())
| project name, type, resourceGroup, subscriptionId,
          createdTime = todatetime(properties.createdTime), id
| order by createdTime desc
```

Join on `id` (= `ResourceId`) to attach each new resource's current-month cost and its
percentage of the subscription total.

### Step 5 — Summarize for the user

1. Lead with the **subscription-level change** ($ and %), direction first.
2. List the **top cost increases** — name, type, delta, % change, and % of the total change.
3. Note significant **decreases** (savings).
4. Call out **new resources** and their share of current spend.
5. For a tenant run, present a **ranked subscription table** first, then drill into the
   biggest mover.

> ⚠️ The **current month is partial** until month-end, so an early-month "decrease" is
> usually just incomplete data. For accurate completed-month comparisons, widen the date
> range and compare the two most recent *complete* months, or use `AmortizedCost`.

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `AuthorizationFailed` on cost query | Identity lacks cost access | Grant **Cost Management Reader** on the scope |
| Empty / one-month cost data | New subscription or no spend yet | Widen the date range; confirm the subscription has usage |
| `429 TooManyRequests` | Cost query throttling across many subs | Retry with backoff; process subscriptions sequentially |
| Current month looks low | Partial month | Compare completed months |
| New resource has no cost row | Deployed but not yet billed | Expected — surface it from Resource Graph with cost = 0 |

## Constraints

- ✅ **Always** resolve Cost Management response column indices **by name** (order is not guaranteed).
- ✅ **Always** normalize the month column to `yyyy-MM` (`BillingMonth` vs `UsageDate`).
- ✅ **Prefer** comparing two *complete* months for accurate trend claims.
- ❌ **Never** try to read cost from Azure Resource Graph — it has no billing data.
- ❌ **Never** mutate resources — this skill is read-only.
- ❌ **Never** present a partial-month drop as a real cost reduction without flagging it.
