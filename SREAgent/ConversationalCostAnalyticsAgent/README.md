# Conversational Cost Analytics Agent

An Azure SRE Agent solution for investigating Azure spend in natural language, comparing month-over-month costs, identifying resource-level cost drivers, and presenting findings in an interactive Live Report.

The latest portable kit is in [V1](V1/README.md). It includes three skills, three Live Report templates, a knowledge playbook, six setup and investigation prompts, and an optional placeholder renderer. The original [Dashboard](Dashboard/README.md) and [Skills](Skills/) folders remain available as the earlier version.

## Capabilities

- Discover accessible Azure subscriptions.
- Compare current and previous-month costs by subscription and resource.
- Explore up to 12 months of cost history, select months for comparison, and drill down by service.
- Identify newly billed resources and verify creation separately using available inventory or history.
- Rank the resources driving increases and decreases.
- Surface Azure Advisor optimization and orphaned-resource findings.
- Review subscription spending, forecasts or labeled projections, and budget utilization where authorized data is available.
- Generate and periodically refresh an Azure SRE Agent Live Report.

Reports use snapshots populated during refresh, not real-time billing queries. Queries, permissions, and scheduled refresh must be validated in the target environment. See the [V1 limitations](V1/README.md#known-limitations), including the subscription picker's current label-only behavior.

## Dashboard Preview

### Month-to-Month Overview

V1 supports a 12-month trend and month selection alongside summary KPIs, projected current-month spend, and prior-month actuals. The screenshot below shows the earlier report and is retained for reference.

![Month-to-month cost overview](Screenshots/month-to-month-overview.png)

### Resource-Level Changes

New-resource detection and expandable resource-level month-over-month comparisons.

![Month-to-month resource comparison](Screenshots/month-to-month-resources.png)

### Azure Advisor Cost Optimization

Rightsizing and savings opportunities derived from Azure Advisor data.

![Azure Advisor cost optimization](Screenshots/advisor-cost-optimization.png)

### Orphaned Resources

Inventory of unattached disks, stale snapshots, orphaned public IPs and NICs, and empty App Service plans.

![Azure Advisor orphaned resources](Screenshots/advisor-orphaned-resources.png)

## Repository Structure

```text
ConversationalCostAnalyticsAgent/
|-- README.md
|-- Azure-SRE-Agent-Cost-Analytics-Use-Case.md
|-- V1/
|   |-- README.md
|   |-- knowledge/
|   |   `-- cost-analysis-playbook.md
|   |-- prompts/
|   |   |-- 01-bootstrap-environment.md
|   |   |-- 02-create-month-to-month-report.md
|   |   |-- 03-create-budget-report.md
|   |   |-- 04-create-advisor-report.md
|   |   |-- 05-scheduled-tasks.md
|   |   `-- 06-adhoc-prompts.md
|   |-- reports/
|   |   |-- month-to-month-cost.html
|   |   |-- subscription-cost-budget.html
|   |   `-- advisor-cost-optimization.html
|   |-- setup/
|   |   |-- placeholders.env.example
|   |   `-- render.py
|   `-- skills/
|       |-- cost-month-to-month/
|       |   `-- SKILL.md
|       |-- advisor-cost-optimization/
|       |   `-- SKILL.md
|       `-- budget-overview/
|           `-- SKILL.md
|-- Dashboard/
|   |-- live-report-template.html
|   |-- bootstrap-prompt.md
|   `-- README.md
|-- Skills/
|   |-- month-over-monthSKILL.md
|   `-- live-report-query-reference-SKILL.md
`-- Screenshots/
    |-- month-to-month-overview.png
    |-- month-to-month-resources.png
    |-- advisor-cost-optimization.png
    `-- advisor-orphaned-resources.png
```

## Import V1

1. Follow the [V1 setup guide](V1/README.md) and configure scoped permissions for the agent identity.
2. Add the three skills from [V1/skills](V1/skills/) and upload the [cost analysis playbook](V1/knowledge/cost-analysis-playbook.md) as knowledge.
3. Run [prompt 01](V1/prompts/01-bootstrap-environment.md) to discover subscriptions, validate access, and record environment settings.
4. Run [prompt 02](V1/prompts/02-create-month-to-month-report.md), [prompt 03](V1/prompts/03-create-budget-report.md), and [prompt 04](V1/prompts/04-create-advisor-report.md), each with its matching template from [V1/reports](V1/reports/).
5. Reconcile report totals and labels with the source data before configuring optional refresh using [prompt 05](V1/prompts/05-scheduled-tasks.md).
6. Use [prompt 06](V1/prompts/06-adhoc-prompts.md) for follow-up investigations and manual refresh.

Templates contain demonstration data and placeholders. Replace them with authorized data during setup. Do not commit populated customer reports, environment memory, credentials, or customer-specific placeholder files.

## Skills

| V1 skill | Purpose |
|---|---|
| [Month-to-month cost](V1/skills/cost-month-to-month/SKILL.md) | Cost queries, resource-level changes, projections, and a 12-month trend. |
| [Advisor optimization](V1/skills/advisor-cost-optimization/SKILL.md) | Rightsizing, commitment recommendations, and potentially orphaned resources for review. |
| [Budget overview](V1/skills/budget-overview/SKILL.md) | Month-to-date spend, previous-month actuals, forecasts, and budget utilization. |

The earlier analysis and query-reference skills are retained in [Skills](Skills/).

## Required Access

| Role | Purpose |
|---|---|
| `Cost Management Reader` | Read subscription cost and usage data. |
| `Reader` | Discover subscriptions and enrich resources through Azure Resource Graph. |

Keep the solution read-only by default. Validate recommendations and require explicit approval before resizing resources, deleting orphaned assets, or purchasing reservations or savings plans.

Reservation, savings plan, and billing-scope visibility may require additional permissions. Subscription `Reader` access does not automatically grant access to every commitment dataset. Report unavailable data explicitly rather than treating an access failure as a zero value.

## Important Data Notes

- Current-month cost is partial until month-end; projected values must be labeled.
- Azure Cost Management provides billing data. Azure Resource Graph does not contain cost.
- Cost data can lag behind current usage.
- Resolve Cost Management response columns by name because their order is not guaranteed.
- Treat optimization savings as estimates, not guaranteed realized savings.

## Example Prompts

> Which subscriptions and resources explain the largest cost increases compared with last month?

> Show newly billed resources separately from resources created this month.

> Build the cost dashboard with up to 12 months of history, let me select months to compare, and rank the top resource-level changes.

> Show Azure Advisor savings opportunities and orphaned resources that require owner review.

> Which budgets are projected to exceed their limits at the current run rate?

> Refresh the Month-to-Month Cost Analysis report using the cost analysis playbook.
