# Month-to-Month Cost Analysis - Dashboard Kit

Drop-in cost analysis dashboard for any Azure SRE Agent. Auto-discovers subscriptions, queries 6 months of cost history, and builds an interactive Live Report with expandable service breakdowns.

## What You Get

| Component | Description |
|---|---|
| **Live Report** | Interactive HTML dashboard with 6-month trend chart, top 15 resource chart, expandable monthly/resource tables, multi-select subscription picker |
| **Skill Files** | Analysis workflow and proven queries with exact tool mappings, response shapes, and failed approaches to avoid |
| **Scheduled Refresh** | Weekly auto-refresh of cost data (Monday 7am UTC) |
| **Bootstrap Prompt** | Copy-paste agent prompts for first-run setup and scheduled task |

## Files

```text
Dashboard/
|-- live-report-template.html   # Generic report template with no customer data
|-- bootstrap-prompt.md         # Agent prompts for setup and refresh
`-- README.md                   # This deployment guide

Skills/
|-- month-over-monthSKILL.md
`-- live-report-query-reference-SKILL.md
```

## Quick Start (5 minutes)

### Step 1: Add the Skill Files

Add both files from the repository's `Skills/` folder to the agent's knowledge base:

- `month-over-monthSKILL.md` - analytical workflow and reporting rules.
- `live-report-query-reference-SKILL.md` - SRE Agent query and tool reference.

Use one of these methods:

- **Agent UI:** Go to Capabilities → Skills → Upload, or use the Knowledge page
- **Agent Chat:** Drag and drop the skill files into the chat, or say: _"Upload these as knowledge documents"_
- **Memory folder:** Place the query reference in `memories/synthesizedKnowledge/cost-analysis-queries.md`

This ensures the agent reads proven query patterns before any cost investigation.

### Step 2: Assign Permissions

The agent's managed identity needs these roles on each target subscription:

```bash
# Find the agent's managed identity client ID from the agent settings page

# Assign Cost Management Reader (required for cost queries)
az role assignment create \
  --assignee {AGENT_MANAGED_IDENTITY_CLIENT_ID} \
  --role "Cost Management Reader" \
  --scope /subscriptions/{SUBSCRIPTION_ID}

# Assign Reader (required for Resource Graph queries)
az role assignment create \
  --assignee {AGENT_MANAGED_IDENTITY_CLIENT_ID} \
  --role "Reader" \
  --scope /subscriptions/{SUBSCRIPTION_ID}
```

Repeat for each subscription the agent should monitor.

### Step 3: Bootstrap the Report

Open the agent thread and paste the **First-Run Bootstrap Prompt** from `bootstrap-prompt.md`.

Provide `live-report-template.html` as the importable dashboard template when creating the Live Report.

The agent will:
1. Discover all accessible subscriptions
2. Query 6 months of cost data for each
3. Build and save the Live Report with all data populated
4. Share the report link

### Step 4: Set Up Weekly Refresh (Optional)

Tell the agent:

> "Create a scheduled task to refresh the cost report every Monday at 7am UTC. It should run automatically without asking for approval."

Or use the **Weekly Refresh Scheduled Task Prompt** from `bootstrap-prompt.md` with `CreateScheduledMonitoringTask`:
- **Task Name:** `Weekly Cost Report Refresh`
- **Cron:** `0 7 * * 1`
- **Agent Prompt:** Copy from `bootstrap-prompt.md` section 2

## How It Works

### Data Flow
```
az account list          → Discover subscriptions (RunAzCliReadCommands)
         ↓
Cost Management API      → 6-month trend + current/prev month detail (RunAzCliWriteCommands)
         ↓
Parse & Aggregate        → Group by resource, compute projections, classify changes
         ↓
Live Report HTML         → Bake data into template, save via SaveReport
```

### Why Baked-In Data?

Live Reports can only call **connector tools** (from `ListConnectorTools`) at view time. Built-in tools like `RunAzCliWriteCommands` are blocked in `allowedTools`. Without a dedicated cost data connector, the report uses data baked in at refresh time.

**To get truly live data:** Configure an MCP connector that exposes cost queries, then update the template to use `window.sreagent.callTool()` instead of the baked-in arrays.

### Report Sections

| Section | Description |
|---|---|
| **Subscription Picker** | Multi-select checkboxes with Select All, shows subscription names |
| **KPI Cards** | Current month projected, previous month actual, MoM change %, new resource count |
| **6-Month Trend** | Bar chart + expandable table — click any month to see per-service breakdown |
| **Top 15 Resources** | Horizontal bar chart comparing current (projected) vs previous month |
| **New Resources** | Table of resources that appeared this month but weren't in the previous month |
| **All Resources** | Full comparison table — click any row to expand per-service cost breakdown |

## Customization

### Change the trend window
Edit the `timePeriod.from` date in the 6-month trend query to go further back (e.g., 12 months).

### Switch to amortized costs
Change `"type":"ActualCost"` to `"type":"AmortizedCost"` in query bodies. This spreads reservation/savings plan costs.

### Scope to specific resource groups
Change the query URL from:
```
/subscriptions/{id}/providers/Microsoft.CostManagement/query
```
to:
```
/subscriptions/{id}/resourceGroups/{rg}/providers/Microsoft.CostManagement/query
```

### Add more grouping dimensions
Supported: `ResourceId`, `ResourceGroupName`, `ServiceName`, `MeterCategory`, `ResourceType`, `ResourceLocation`. Max 2 per query.

### Change refresh frequency
Update the cron expression in the scheduled task:
- `0 7 * * 1` — Monday 7am (weekly)
- `0 7 * * 1-5` — Weekdays 7am
- `0 7 1 * *` — 1st of each month 7am
- `0 */6 * * *` — Every 6 hours

## Troubleshooting

| Issue | Cause | Fix |
|---|---|---|
| `AuthorizationFailed` | Missing RBAC role | Assign `Cost Management Reader` to the agent identity |
| `This method only supports read operations` | Used `RunAzCliReadCommands` for POST | Use `RunAzCliWriteCommands` instead |
| `'costmanagement' is not recognized` | Extension missing | Use `az rest --method post` pattern, not `az costmanagement` |
| `Please run 'az login'` | Used `RunInTerminal` | Use `RunAzCliWriteCommands` / `RunAzCliReadCommands` tools |
| `allowedTools contains unknown tool name(s)` | Tried to use built-in tools in Live Report | Use baked-in data (no connectors configured) |
| Chart panel is empty | `Chart.register(ChartDataLabels)` called after chart creation | Ensure registration happens BEFORE any `new Chart()` call |
| Cost data looks too low | Current month is partial | Projections improve as more days elapse; compare full months only for accuracy |
| 429 throttling | Cost Management API rate limit | Add backoff/retry; avoid querying too many subscriptions in tight loops |

## Architecture Decision Record

| Decision | Rationale |
|---|---|
| POST via `RunAzCliWriteCommands` | Cost Management Query API requires POST; read-only CLI tool rejects it |
| Baked-in data (not live) | No data connectors configured; built-in tools blocked in Live Report `allowedTools` |
| Aggregate by ResourceId | One resource spans multiple ServiceName rows — must sum to get total |
| 6-month Monthly granularity | Good balance of trend visibility without too much data; adjustable |
| Chart.js + datalabels | Lightweight, CDN-served with SRI, works in CSP-sandboxed iframe |
| `textContent` only | CSP security rule — `innerHTML` with untrusted data could allow injection |
