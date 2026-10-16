---
name: Cost Month to Month
description: Proven queries, tool mappings, response shapes, and failed approaches for Azure month-over-month cost analysis. Read this FIRST before running any cost investigation. Works with any subscription.
---

# Cost & Resource Query Reference — Proven Playbook

This skill combines two data sources. **Cost comes from Cost Management (POST via RunAzCliWriteCommands); resource metadata comes from Azure Resource Graph (GET via RunAzCliReadCommands).**

> **Usage:** Replace `{SUB_ID}` with the target subscription ID in every query.
> To operate on multiple subscriptions, loop through each one.

---

## 0. PROVEN: Discover All Subscriptions

**Tool:** `RunAzCliReadCommands`

```
az account list --query "[?state=='Enabled'].{name:name, id:id}" -o json
```

**Verified response shape:**
```json
{
  "cliExecutionResult": {
    "output": "[\n  { \"id\": \"aaaa-bbbb-cccc\", \"name\": \"My-Subscription-Name\" }\n]"
  }
}
```

Alternative via Resource Graph (if `az account list` is scoped):
```
az graph query -q "ResourceContainers | where type == 'microsoft.resources/subscriptions' | project subscriptionId, displayName=name, state=tostring(properties.state) | where state == 'Enabled'" --first 50
```

---

## 1. PROVEN: Cost by Resource + Service (per subscription)

**Tool:** `RunAzCliWriteCommands` (MUST use write tool — POST is rejected by `RunAzCliReadCommands`)

```
az rest --method post --url "https://management.azure.com/subscriptions/{SUB_ID}/providers/Microsoft.CostManagement/query?api-version=2023-11-01" --body "{\"type\":\"ActualCost\",\"timeframe\":\"Custom\",\"timePeriod\":{\"from\":\"{FROM_DATE}T00:00:00Z\",\"to\":\"{TO_DATE}T23:59:59Z\"},\"dataset\":{\"granularity\":\"None\",\"aggregation\":{\"totalCost\":{\"name\":\"PreTaxCost\",\"function\":\"Sum\"}},\"grouping\":[{\"type\":\"Dimension\",\"name\":\"ResourceId\"},{\"type\":\"Dimension\",\"name\":\"ServiceName\"}]}}" --subscription {SUB_ID}
```

**Placeholders:**
- `{SUB_ID}` — subscription GUID
- `{FROM_DATE}` — start date `YYYY-MM-DD` (e.g. `2026-10-01`)
- `{TO_DATE}` — end date `YYYY-MM-DD` (e.g. `2026-10-15`)

**Verified response shape:**
```json
{
  "cliExecutionResult": {
    "output": "<JSON string — parse this>",
    "errorType": "None",
    "errorOccurred": false
  }
}
```

Parsed `output`:
```json
{
  "properties": {
    "columns": [
      { "name": "PreTaxCost", "type": "Number" },
      { "name": "ResourceId", "type": "String" },
      { "name": "ServiceName", "type": "String" },
      { "name": "Currency", "type": "String" }
    ],
    "rows": [
      [ 38.30, "/subscriptions/.../agents/myagent", "Foundry Tools", "USD" ]
    ]
  }
}
```

**Critical parsing notes:**
- Columns are **positional** — resolve indices from `properties.columns`.
- One resource → **multiple rows** with different ServiceName. **Aggregate by ResourceId.**
- `ResourceId` can be empty → bucket as `(subscription-level / untagged)`.
- All ResourceIds are lowercase.

---

## 2. PROVEN: 6-Month Cost Trend by Service (per subscription)

**Tool:** `RunAzCliWriteCommands`

```
az rest --method post --url "https://management.azure.com/subscriptions/{SUB_ID}/providers/Microsoft.CostManagement/query?api-version=2023-11-01" --body "{\"type\":\"ActualCost\",\"timeframe\":\"Custom\",\"timePeriod\":{\"from\":\"{6MO_AGO_DATE}T00:00:00Z\",\"to\":\"{TODAY}T23:59:59Z\"},\"dataset\":{\"granularity\":\"Monthly\",\"aggregation\":{\"totalCost\":{\"name\":\"PreTaxCost\",\"function\":\"Sum\"}},\"grouping\":[{\"type\":\"Dimension\",\"name\":\"ServiceName\"}]}}" --subscription {SUB_ID}
```

Response columns: `PreTaxCost`, `BillingMonth` (datetime string like `2026-05-01T00:00:00`), `ServiceName`, `Currency`.

---

## 3. PROVEN: Cost by Service Name (summary)

**Tool:** `RunAzCliWriteCommands`

```
az rest --method post --url "https://management.azure.com/subscriptions/{SUB_ID}/providers/Microsoft.CostManagement/query?api-version=2023-11-01" --body "{\"type\":\"ActualCost\",\"timeframe\":\"MonthToDate\",\"dataset\":{\"granularity\":\"None\",\"aggregation\":{\"totalCost\":{\"name\":\"PreTaxCost\",\"function\":\"Sum\"}},\"grouping\":[{\"type\":\"Dimension\",\"name\":\"ServiceName\"}]}}" --subscription {SUB_ID}
```

---

## 4. PROVEN: Cost by Resource Group

**Tool:** `RunAzCliWriteCommands`

```
az rest --method post --url "https://management.azure.com/subscriptions/{SUB_ID}/providers/Microsoft.CostManagement/query?api-version=2023-11-01" --body "{\"type\":\"ActualCost\",\"timeframe\":\"MonthToDate\",\"dataset\":{\"granularity\":\"None\",\"aggregation\":{\"totalCost\":{\"name\":\"PreTaxCost\",\"function\":\"Sum\"}},\"grouping\":[{\"type\":\"Dimension\",\"name\":\"ResourceGroupName\"}]}}" --subscription {SUB_ID}
```

---

## 5. PROVEN: Resource Inventory by Type

**Tool:** `RunAzCliReadCommands`

```
az graph query -q "Resources | summarize count() by type | order by count_ desc" --subscriptions {SUB_ID} --first 50
```

---

## 6. PROVEN: Recently Created Resources

**Tool:** `RunAzCliReadCommands`

```
az graph query -q "Resources | where isnotempty(properties.creationTime) or isnotempty(properties.createdTime) | extend created = coalesce(todatetime(properties.createdTime), todatetime(properties.creationTime)) | where created >= datetime({SINCE_DATE}) | project name, type, resourceGroup, created, id | order by created desc" --subscriptions {SUB_ID} --first 100
```

**Note:** `properties.createdTime` is NOT on all resource types. Missing = unknown, not old.

---

## Useful Grouping Dimensions

| Dimension | Use case |
|---|---|
| `ResourceId` | Per-resource breakdown (most detailed) |
| `ResourceGroupName` | Cost by resource group |
| `ServiceName` | Cost by Azure service |
| `MeterCategory` | Cost by meter category |
| `ResourceType` | Cost by ARM resource type |
| `ResourceLocation` | Cost by region |

Max 2 dimensions per query.

---

## FAILED APPROACHES — DO NOT RETRY

| What was tried | Tool | Error | Why |
|---|---|---|---|
| `az consumption usage list` | `RunAzCliReadCommands` | `ValidationError` | Not available in SRE Agent sandbox |
| `az costmanagement query` | `RunAzCliReadCommands` | `not recognized` | Extension not installed |
| `az rest --method post` | `RunAzCliReadCommands` | `only supports read operations` | POST = write; must use `RunAzCliWriteCommands` |
| `az rest --method post` | `RunInTerminal` | `Please run 'az login'` | Terminal not authenticated |
| Built-in tools in Live Report `allowedTools` | `SaveReport` | `unknown connector tool name(s)` | Only connector tools allowed; no connectors = baked-in data only |

---

## Analysis Workflow

### Step 1: Discover subscriptions
`az account list` → get all enabled subscriptions with names and IDs.

### Step 2: Query costs (parallel per subscription)
For each subscription, run current month + previous month cost queries via `RunAzCliWriteCommands`.
For 6-month trend, use Monthly granularity grouped by ServiceName.

### Step 3: Parse and aggregate
- Parse `cliExecutionResult.output` as JSON.
- Resolve column indices from `properties.columns`.
- Aggregate rows by ResourceId (sum across ServiceName).
- Extract short name (last path segment) and resource group from ResourceId.

### Step 4: Compare months
- **New:** in current but not previous. **Stopped:** in previous but not current.
- **Projected:** `currentMTD × (daysInMonth / daysElapsed)`.
- **% change:** `(projected − previous) / |previous| × 100`.
- **Status:** new / up (>+10%) / down (>−10%) / stable.

### Step 5: Present
- KPI cards: total MTD, projected, previous, delta
- 6-month trend bar chart + expandable monthly table
- Top 15 resources chart
- New resources table
- Full comparison table with expandable service breakdown

---

## Live Report Notes

- Live Reports **cannot call built-in tools** — only connector tools. Without connectors, use baked-in data.
- To refresh: re-query → `GetReport` → edit data arrays in HTML → `SaveReport` with same reportId.
- Subscription picker is built from `az account list` results at refresh time.

---

## Gotchas

- **Current month is partial** — early-month looks like a drop.
- **Cost data lags 8–24h.**
- **Permissions:** Needs `Cost Management Reader` (or `Reader` + `Billing Reader`).
- **Throttling:** Retry 429s with backoff.
- **Reservations:** `ActualCost` = lump; `AmortizedCost` = spread.
- **One resource = multiple rows** — always aggregate by ResourceId.
