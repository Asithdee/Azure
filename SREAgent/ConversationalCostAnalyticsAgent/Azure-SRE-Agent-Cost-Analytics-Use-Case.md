# Azure SRE Agent: Conversational Cost Analytics and FinOps Reporting

**Use-case summary:** Help cloud operations and finance teams understand Azure spending, explain changes, and prioritize savings through natural-language questions and interactive cost reports, with Azure Portal links for investigation and approved action.

**Primary persona:** Cloud Operations / FinOps Lead  
**Supporting personas:** SRE, Azure Platform Engineer, Subscription Owner, Finance Analyst, IT Budget Owner  
**Business function:** Cloud operations, financial management, and governance  
**Applicability:** State and local government, higher education, and other organizations operating Azure subscriptions  
**Status:** Prototype reports demonstrated through supplied screenshots; additional integrations and automation proposed. No measured customer savings or production-readiness claim.

## 1. The person and the problem

A cloud operations or FinOps lead must explain where Azure money is going, why spending changed, and which actions can safely reduce costs. Today, this can require switching among Cost Management, Azure Advisor, resource inventories, reservation views, and spreadsheets.

Subscription totals alone do not explain which resources drove an increase, whether a new workload appeared, whether stable workloads are good commitment candidates, or who owns untagged spend. Rebuilding reports and writing recurring summaries adds effort and can produce inconsistent comparisons.

## 2. The agent-assisted experience

The user asks the Azure SRE Agent:

> "Show spending across my authorized subscriptions. Compare this month with previous months, explain the largest changes, identify new resources and stable workloads, and show the best cost optimization opportunities."

The agent retrieves authorized data through configured tools, presents an interactive report, and explains findings with source references and timestamps. Users drill from subscription to resource group, service, resource, and available meter-level detail, then open the relevant Azure Portal view.

The agent supports investigation and recommendations by default. Resource changes, commitment purchases, policy changes, and external report delivery require separately configured permissions and approval controls.

## 3. Scope and report capabilities

| Area | Intended experience |
|---|---|
| Subscription overview | Multi-select authorized subscriptions; show month-to-date actual cost, previous-month actual cost, forecast or labeled projection, budgets, and budget utilization. |
| Cost breakdown | Filter and group by subscription, resource group, service, resource, region, and available tags. Show each resource's contribution to total spending and to the change in spending. |
| Historical comparison | Show six-month trends, matched-period month-to-date comparisons, completed-month comparisons, and separately labeled full-month forecasts. Explain absolute and percentage increases and decreases. |
| Resource lifecycle | Separate newly created resources, newly observed billable resources, stable resources, increased/decreased spend, and resources no longer incurring observed charges. Verify creation or deletion using inventory/history where available. |
| Cost optimization | Surface Azure Advisor recommendations and candidates for rightsizing, scheduling, or cleanup. Include estimated savings, evidence, owner, operational risk, and approval requirements. Low CPU alone does not establish that shutdown is safe. |
| Reservations / RI | Show accessible reservation inventory, utilization, coverage, unused commitment, expiration, and purchase recommendations. Keep utilization distinct from coverage. |
| Savings plans and discounts | Show accessible savings plan utilization, coverage, and recommendations; explain effective pricing and identifiable negotiated or benefit-based discounts where billing data supports them. Do not assume retail prices equal the customer's prices. |
| Governance and tagging | Report spend missing required tags such as Owner, CostCenter, Application, and Environment; show budget gaps, unallocated cost, and ownership follow-up. Preserve a visible unallocated category. |
| Report delivery | Offer manual refresh, configured automatic refresh, and scheduled generation. Send approved email summaries or secure report links at configured times, subject to supported integrations and recipient access controls. |

### Report examples supplied

- **Month-to-Month Cost Analysis:** Summary cards, six-month trend, top-resource comparisons, new-resource list, and expandable resource-level changes.
- **Azure Advisor Cost Optimization:** Rightsizing recommendations, reservation purchase advice, existing reservations, and savings plan recommendations.
- **Subscription Cost & Budget Overview:** Month-to-date spend, previous-month actuals, forecast, expected change, and configured budgets.

These screenshots demonstrate report layouts and example snapshots, not verified live connections, automatic refresh, scheduled email delivery, realized savings, or complete billing coverage.

## 4. Data, trust, and operating model

**Data sources:** Azure Cost Management queries or exports, Azure Advisor, Azure Resource Graph/inventory, resource history where available, budget configuration, and authorized reservation, savings plan, and billing datasets.

**Access:** Use least-privilege managed identity and scope-specific read permissions. Subscription resource access does not automatically grant billing or commitment visibility. Display unavailable or unauthorized datasets explicitly; never report an access failure as zero spend or no reservations.

**Financial accuracy:** State scope, currency, billing period, cost basis, data-through date, retrieval time, and comparison method. Distinguish actual from amortized cost, month-to-date from full-month values, and service forecasts from simple run-rate projections. Do not combine currencies without an explicit conversion method.

For a zero prior-period baseline, display "New spend" or "Not comparable" rather than an infinite percentage increase. Classify "stable" using a configurable, documented threshold on comparable periods. A newly billed resource is not necessarily newly created.

**Savings integrity:** Treat recommendations as estimates, not guarantees. Deduplicate alternative lookback/term recommendations and account for overlap among rightsizing, reservations, and savings plans before presenting a combined savings opportunity. Evaluate rightsizing before recommending new commitments.

**Freshness and delivery:** "Live" means refreshed from the latest available source data, not real-time billing. Report source latency and stale data clearly. Configure schedules with a timezone and daylight-saving behavior. Log refresh/delivery failures, retry transient errors with bounds, and prevent duplicate emails.

**Safety:** Keep reporting read-only by default. Require explicit approval and workload validation before changing resources or purchasing commitments. Restrict report access and avoid exposing resource identifiers or financial detail to unauthorized email recipients.

## 5. Token-efficient design

Separate data refresh, report rendering, and AI interpretation so routine dashboard viewing does not require a new model call.

- Aggregate, filter, rank, and calculate in APIs or deterministic code before passing results to the model.
- Cache authorized snapshots and summaries by scope, period, currency, cost basis, and data version; invalidate them when relevant data or permissions change.
- Send only top cost drivers, material changes, anomalies, and compact structured evidence to the model. Retrieve detailed rows only when users drill down.
- Reuse report templates and versioned calculations instead of asking the model to rebuild charts or recalculate totals.
- Refresh data on a source-appropriate schedule; regenerate narratives only when material changes occur.
- Use deterministic email templates when commentary is unnecessary. Where supported, route simple summaries to a lower-cost model and reserve deeper reasoning for investigations.
- Track model calls, input/output tokens, tool/API costs, and total cost per successful report. Apply configurable context and output limits without silently dropping material findings.

## 6. Business outcomes and proof

**Expected value:** Faster cost investigations, more consistent budget conversations, better ownership of spending, and a prioritized list of evidence-backed optimization opportunities.

**Pilot success measures:** Compare report-preparation time and investigation time against a baseline; reconcile totals to matching Azure Cost Management views; measure spend allocated to owners/cost centers, tagging completeness, refresh and delivery success, data age, and token cost per report. Track approved actions and realized savings separately from estimated opportunities.

**Proof status:** Prototype / illustrative evidence. The supplied screenshots support the reporting concept; measured productivity improvements, realized savings, production integration, and scheduled delivery remain to be validated.

### Example prompts

> "Which subscriptions and resources explain the largest cost increases? Compare matched month-to-date periods."

> "Show newly created resources separately from resources that only started generating charges this month."

> "Which workloads have stable spending over the last three completed months, and which might qualify for a reservation or savings plan after rightsizing?"

> "Show reservation utilization and coverage, upcoming expirations, and unused commitments."

> "Which spending is missing an owner or cost center, and which budgets are forecast to be exceeded?"

> "Prepare a weekday 8:00 a.m. cost digest in my configured timezone. Reuse cached data when current, include its data-through date, and generate AI commentary only for material changes."

## Reference and template limitation

The SLED Use Case Library was located at https://microsoft.sharepoint.com/sites/sleducl?web=1. Organizational policy restricted access to its detailed card template. This document uses an original persona-led six-section structure; it does not claim to reproduce the library's exact headings or SharePoint schema.
