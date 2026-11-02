---
name: budget-overview
description: Subscription cost summary (actual month-to-date, last month, end-of-month forecast) and Azure budget utilization for one or many subscriptions. Use for "am I over budget", "forecast this month", "list budgets", or refreshing the Subscription Cost & Budget Overview Live Report.
---

# Subscription Cost & Budget Overview

## 1. List subscriptions in scope (`RunAzCliReadCommands`)
```
az graph query -q "ResourceContainers | where type == 'microsoft.resources/subscriptions' | project subscriptionId, name, state=tostring(properties.state) | where state == 'Enabled'" --first 100
```

## 2. Actual MTD and last month (`RunAzCliWriteCommands` — POST)
```
az rest --method post --url "https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.CostManagement/query?api-version=2023-11-01" --body "{\"type\":\"ActualCost\",\"timeframe\":\"MonthToDate\",\"dataset\":{\"granularity\":\"None\",\"aggregation\":{\"totalCost\":{\"name\":\"PreTaxCost\",\"function\":\"Sum\"}}}}" --subscription {subscriptionId}
```
Last month: `"timeframe":"TheLastMonth"`.

## 3. Forecast to month end (`RunAzCliWriteCommands` — POST)
```
az rest --method post --url "https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.CostManagement/forecast?api-version=2023-11-01" --body "{\"type\":\"ActualCost\",\"timeframe\":\"Custom\",\"timePeriod\":{\"from\":\"<YYYY-MM>-01T00:00:00Z\",\"to\":\"<YYYY-MM-LASTDAY>T23:59:59Z\"},\"dataset\":{\"granularity\":\"Daily\",\"aggregation\":{\"totalCost\":{\"name\":\"Cost\",\"function\":\"Sum\"}}},\"includeActualCost\":true,\"includeFreshPartialCost\":false}" --subscription {subscriptionId}
```
Sum all rows (actual + forecast) for the month total. If forecast fails (new subscription, < ~7 days of data),
fall back to linear projection `MTD * daysInMonth / daysElapsed` and label it "projected".

## 4. Budgets (`RunAzCliReadCommands` — GET)
```
az rest --method get --url "https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.Consumption/budgets?api-version=2023-05-01"
```
Per budget use: `name`, `properties.amount`, `properties.timeGrain`, `properties.timePeriod.startDate/endDate`,
`properties.currentSpend.amount`, `properties.forecastSpend.amount` (may be absent → null).
Resource-group budgets: same path under `/resourceGroups/{rg}`.

Utilization thresholds: `< 60%` ok · `60–99%` warn · `>= 100%` danger (apply to both actual and forecast).

## 5. Output contract (used by the Live Report template)
```
{ currency, curMonthLabel:'Mon YYYY', prevMonthLabel:'Mon YYYY', daysElapsed, snapshotUtc,
  subscriptions:[{ name, id, actualMtd, lastMonth, forecast }],
  budgets:[{ subscription, name, amount, currentSpend, forecastSpend|null, period:'Mon YYYY – Mon YYYY' }] }
```

## Gotchas
- Budget `currentSpend` is refreshed by Azure a few times a day and can differ slightly from the Query API.
- Requires Cost Management Reader (query/forecast) and Reader on budgets.
