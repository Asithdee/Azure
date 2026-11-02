---
name: advisor-cost-optimization
description: Collect Azure cost-saving opportunities for any subscription - Advisor VM right-sizing/shutdown, reservation and savings plan recommendations, existing reservations, and orphaned resources (unattached disks, old snapshots, unused public IPs/NICs, empty App Service plans). Use for "how can I save money", "orphaned resources", "reservation recommendations", or refreshing the Advisor Cost Optimization Live Report.
---

# Advisor Cost Optimization

All queries are read-only. Run Resource Graph via `RunAzCliReadCommands`; `az rest --method get` also via `RunAzCliReadCommands`.
Replace `{subscriptionId}` (repeat `--subscriptions` with space-separated IDs for several subscriptions).

> Verification status: the Resource Graph shapes below are standard but `extendedProperties` keys differ by
> recommendation type. On first run in a new environment, take 3 rows, look at `ext`, and adjust field names.
> Record what you learn in memory.

## 1. Advisor cost recommendations (all types)

```
az graph query -q "advisorresources | where type == 'microsoft.advisor/recommendations' | where properties.category == 'Cost' | extend problem=tostring(properties.shortDescription.problem), solution=tostring(properties.shortDescription.solution), impacted=tostring(properties.impactedValue), impactedType=tostring(properties.impactedField), ext=properties.extendedProperties, annualSavings=todouble(properties.extendedProperties.annualSavingsAmount), currency=tostring(properties.extendedProperties.savingsCurrency) | project subscriptionId, resourceGroup, impacted, impactedType, problem, solution, annualSavings, currency, ext | order by annualSavings desc" --subscriptions {subscriptionId} --first 500
```

Classify rows:
| Bucket | Rule (case-insensitive) | Useful `ext` keys |
|---|---|---|
| VM right-size / shutdown | `impactedType =~ 'microsoft.compute/virtualmachines'` and solution mentions resize/shut down | `currentSku`, `targetSku`, `MaxCpuP95`, `regionId`, `recommendationType` |
| Reservation purchase | solution contains `reserved instance` / `reservation` | `displaySKU`/`vmSize`, `displayQty`, `term` (P1Y/P3Y), `lookbackPeriod`, `scope`, `reservationType` |
| Savings plan | solution contains `savings plan` | `term`, `lookbackPeriod`, `scope`, `commitmentAmount` |
| Other | everything else | — |

If `annualSavings` is empty, use `savingsAmount * 12` (monthly) — confirm which one is present.
Lookback variants (7/30/60 days) show up as separate rows; keep them but label the lookback.

## 2. Existing reservations

```
az rest --method get --url "https://management.azure.com/providers/Microsoft.Capacity/reservations?api-version=2022-11-01"
```
Project: `properties.displayName`, `sku.name`, `properties.quantity`, `properties.utilization.aggregates[?grain==30].value`,
`properties.expiryDate`, `properties.appliedScopes`. Empty list or 403 = none visible to the identity (say which).

## 3. Orphaned / idle resources (Resource Graph)

```
az graph query -q "Resources | where type =~ 'microsoft.compute/disks' and tostring(properties.diskState) =~ 'Unattached' | project category='Unattached Disk', name, issue='Not attached to any VM', resourceGroup, sku=tostring(sku.name), sizeGb=toint(properties.diskSizeGB)" --subscriptions {subscriptionId} --first 500
```
```
az graph query -q "Resources | where type =~ 'microsoft.compute/snapshots' and todatetime(properties.timeCreated) < ago(30d) | project category='Stale Snapshot', name, issue='Older than 30 days', resourceGroup, created=todatetime(properties.timeCreated)" --subscriptions {subscriptionId} --first 500
```
```
az graph query -q "Resources | where type =~ 'microsoft.network/publicipaddresses' and isnull(properties.ipConfiguration) and isnull(properties.natGateway) | project category='Orphaned Public IP', name, issue='Not associated with any resource', resourceGroup, sku=tostring(sku.name)" --subscriptions {subscriptionId} --first 500
```
```
az graph query -q "Resources | where type =~ 'microsoft.network/networkinterfaces' and isnull(properties.virtualMachine) and isnull(properties.privateEndpoint) and isnull(properties.privateLinkService) | project category='Orphaned NIC', name, issue='Not attached to VM or PE', resourceGroup" --subscriptions {subscriptionId} --first 500
```
```
az graph query -q "Resources | where type =~ 'microsoft.web/serverfarms' and toint(properties.numberOfSites) == 0 | project category='Empty App Svc Plan', name, issue='No apps on plan', resourceGroup, sku=tostring(sku.name)" --subscriptions {subscriptionId} --first 500
```

Notes:
- Disks named `*-ASRReplica` / attached to Site Recovery, or in `MC_*` (AKS) RGs, may be intentionally unattached — flag, don't recommend deletion blindly.
- Basic SKU public IPs are free when unassociated only if dynamic; Standard static IPs bill.
- Never delete; recommend, and offer a write command for the user to approve.

## 4. Output contract (used by the Live Report template)

```
vmRightSizing:        [vmName, currentSku, action, cpuP95, annualSavings(number), region]
reservations:         [resourceType, sku, qty, term('1-Year'|'3-Year'), annualSavings, lookback, scope]
existingReservations: [displayName, sku, qty, utilizationPct, expiryDate]
savingsPlans:         [type, term, annualSavings, lookback, scope]
orphans:              [category, name, issue, resourceGroup]
```
