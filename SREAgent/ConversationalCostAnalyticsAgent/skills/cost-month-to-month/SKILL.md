---
name: cost-month-to-month
description: Month-over-month Azure cost analysis for any subscription/RG/management-group scope using the Cost Management Query API (cost) and Azure Resource Graph (metadata). Use for "why did cost go up", "compare this month vs last month", "new resources driving cost", "12-month cost trend", or refreshing the Month-to-Month Cost Live Report.
---

# Month-to-Month Cost Analysis

Cost comes from **Cost Management Query API**. Resource metadata (creation time, tags, type) comes from
**Azure Resource Graph**. Resource Graph has **no** cost table.

Scope placeholder used below: `{SCOPE}` =
- Subscription: `/subscriptions/{subscriptionId}`
- Resource group: `/subscriptions/{subscriptionId}/resourceGroups/{rg}`
- Management group: `/providers/Microsoft.Management/managementGroups/{mgId}`

---

## 0. Tool mapping (SRE Agent) — read first

| Operation | Tool | Why |
|---|---|---|
| Cost Management `query` / `forecast` (HTTP **POST**) | `RunAzCliWriteCommands` with `az rest --method post` | POST is classified as a write; the read tool rejects it even though it is read-only. Expect an approval prompt in Review mode. |
| Resource Graph (`az graph query`) | `RunAzCliReadCommands` | Read-only. |
| `az rest --method get` (budgets, reservations) | `RunAzCliReadCommands` | GET is read-only. |

**Do NOT use** (fail in the agent sandbox):
- `az costmanagement ...` — extension not installed.
- `az consumption usage list` — not available.
- `az` from the terminal (`RunInTerminal`) — the terminal is not logged in to Azure.
- Built-in tools (e.g. `RunAzCliWriteCommands`) inside a Live Report's `allowedTools` — rejected. Live Reports can
  only call *connector* tools, so reports built with this kit use **baked-in data** refreshed by a scheduled task.

Tool responses wrap CLI output: parse `cliExecutionResult.output` (a JSON **string**) before reading
`properties.columns` / `properties.rows`.

---

## 1. Per-resource cost for one month (current or previous)

```
az rest --method post \
  --url "https://management.azure.com{SCOPE}/providers/Microsoft.CostManagement/query?api-version=2023-11-01" \
  --body "{\"type\":\"ActualCost\",\"timeframe\":\"Custom\",\"timePeriod\":{\"from\":\"<YYYY-MM>-01T00:00:00Z\",\"to\":\"<YYYY-MM-DD>T23:59:59Z\"},\"dataset\":{\"granularity\":\"None\",\"aggregation\":{\"totalCost\":{\"name\":\"PreTaxCost\",\"function\":\"Sum\"}},\"grouping\":[{\"type\":\"Dimension\",\"name\":\"ResourceId\"},{\"type\":\"Dimension\",\"name\":\"ServiceName\"}]}}" \
  --subscription {subscriptionId}
```
- Current month: `from` = 1st of month, `to` = today.
- Previous month: `from` = 1st, `to` = last day of previous month.
- Run both **in parallel**.

Response columns (positional — always resolve indices from `properties.columns`):
`PreTaxCost, ResourceId, ServiceName, Currency`.

## 2. 12-month trend by service

Same endpoint, body:
```json
{"type":"ActualCost","timeframe":"Custom",
 "timePeriod":{"from":"<YYYY-MM of 11 months ago>-01T00:00:00Z","to":"<today>T23:59:59Z"},
 "dataset":{"granularity":"Monthly",
   "aggregation":{"totalCost":{"name":"PreTaxCost","function":"Sum"}},
   "grouping":[{"type":"Dimension","name":"ServiceName"}]}}
```
The month column is `BillingMonth` (`yyyyMMdd`) or `UsageDate` (`yyyy-MM-ddT00:00:00`) — normalize to `yyyy-MM`.
If the API rejects a range > 12 months or times out, split into two 6-month calls.

## 3. Compact views (MonthToDate)

Replace grouping with `ServiceName` or `ResourceGroupName` and use `"timeframe":"MonthToDate"` (no `timePeriod`).
Other grouping dimensions: `MeterCategory`, `ResourceType`, `ResourceLocation`. Max 2 groupings per query.

## 4. Resource Graph enrichment (`RunAzCliReadCommands`)

Enabled subscriptions in the tenant:
```
az graph query -q "ResourceContainers | where type == 'microsoft.resources/subscriptions' | project subscriptionId, name, state=tostring(properties.state) | where state == 'Enabled'" --first 100
```
Recently created resources:
```
az graph query -q "Resources | extend created = coalesce(todatetime(properties.createdTime), todatetime(properties.creationTime), todatetime(properties.timeCreated)) | where created >= datetime(<YYYY-MM-01>) | project name, type, resourceGroup, subscriptionId, created, id | order by created desc" --subscriptions {subscriptionId} --first 200
```
Inventory by type:
```
az graph query -q "Resources | summarize count() by type | order by count_ desc" --subscriptions {subscriptionId} --first 50
```
Notes: types/IDs are lowercase — use `=~` / `in~`. Missing `createdTime` = unknown, not old.

---

## 5. Analysis workflow

1. Query current and previous month (section 1) in parallel.
2. Parse and **aggregate by ResourceId** — a resource appears once per `ServiceName` (e.g. storage + Defender).
   Empty `ResourceId` → bucket `(subscription-level / unattributed)`. Name = last path segment; RG = segment after `resourcegroups/`.
3. Compute:

| Metric | Formula |
|---|---|
| Projected current month | `currentMTD * daysInMonth / daysElapsed` |
| Delta | `projected - previous` |
| % change | `delta / abs(previous) * 100` |
| Contribution to change | `resourceDelta / abs(totalDelta) * 100` |
| Status | `new` (prev=0, cur>0) · `stopped` (cur=0, prev>0) · `up` (>+10%) · `down` (<-10%) · `stable` |

4. Enrich new resources with Resource Graph (creation date, creator tags).
5. Present: KPI summary (MTD, projected, previous, delta %), top-N bar chart, new resources, stopped resources,
   full table sorted by cost.

## 6. Gotchas

- Current month is **partial**; early-month results always look like a drop — use the projection.
- Cost data lags usage by **8–24 h**; `daysElapsed` should be (today − 1) early in the day.
- Requires **Cost Management Reader** (or Reader + Billing Reader) on the scope. `AuthorizationFailed`/`RBACAccessDenied`
  → grant the agent's managed identity that role.
- **429 throttling** — retry with exponential backoff; when looping many subscriptions, serialize.
- `ActualCost` shows reservation/savings-plan purchases as lump sums; use `AmortizedCost` for spread cost.
- Currency comes from the `Currency` column — never assume USD.
- CSP/EA/MCA billing accounts may need the billing-account scope instead of subscription scope for some tenants.
