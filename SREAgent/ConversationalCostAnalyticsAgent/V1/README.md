# Azure SRE Agent — Portable Cost Analysis Kit

Reusable skills, Live Report templates, and prompts for Azure cost analysis. The kit is designed for reuse across environments, using `{{PLACEHOLDERS}}`, demonstration data, and agent-discovered settings. Validate access, queries, currency, and report calculations before relying on populated reports.

## Contents

| Folder | What | How to use |
|---|---|---|
| `skills/cost-month-to-month/SKILL.md` | Cost Management queries, MoM math, 12-month trend with month selection, tool mapping | Agent → Capabilities → **Skills** → New skill → paste |
| `skills/advisor-cost-optimization/SKILL.md` | Advisor right-sizing, reservations, savings plans, orphaned resources | same |
| `skills/budget-overview/SKILL.md` | MTD / last month / forecast + budget utilization | same |
| `knowledge/cost-analysis-playbook.md` | Do/don't rules, refresh workflow | Upload as a knowledge document (Knowledge settings or ask the agent to upload it) |
| `reports/*.html` | 3 Live Report templates with sample data | Attach to chat with prompts 02–04 |
| `prompts/01..06` | Bootstrap, report creation, scheduled tasks, ad-hoc | Paste into chat in order |
| `setup/render.py` | Optional: pre-fill placeholders per environment | Copy `setup/placeholders.env.example` to a private `setup/placeholders.env`, then run `python3 setup/render.py setup/placeholders.env out/<customer>` |

## Import into a new environment (about 15 minutes)

1. **Create the agent** in the customer tenant and give it access to the target subscription(s).
2. **Grant RBAC** to the agent's managed identity on each subscription (or management group):
   - `Cost Management Reader` (cost query, forecast, budgets)
  - `Reader` (resource inventory and Advisor, where supported)

  Reservation, savings plan, and billing-scope datasets can require additional permissions. Verify access separately; missing access must not be reported as zero commitments or spend.
   ```
   az role assignment create --assignee <agent-managed-identity-client-id> --role "Cost Management Reader" --scope /subscriptions/<subId>
   az role assignment create --assignee <agent-managed-identity-client-id> --role "Reader" --scope /subscriptions/<subId>
   ```
3. **Add the 3 skills** and **upload the knowledge doc**.
4. Paste **prompt 01** (bootstrap). The agent discovers subscriptions and currency, checks access, and writes `cost-environment.md` to memory.
5. Paste **prompts 02, 03, 04**, each with its report template attached. The agent fills the data blocks and saves the Live Reports.
6. Paste **prompt 05** to create the weekly refresh scheduled tasks.
7. Keep **prompt 06** as a cheat sheet.

## How the report templates work

- Each template renders on its own with **SAMPLE** data. Preview it in a browser before importing.
- Real data goes only between the `// >>> DATA:<name>` and `// <<< DATA:<name>` markers. The rest of the HTML/JS is generic.
- Month labels, KPIs, and counts are computed from the data, so no month names or totals are hard-coded.
- `{REPORT_NONCE}` (single braces) is the Live Report runtime nonce. Leave it as is.
- Data is **baked in** (`allowedTools: []`) because Live Reports can't call built-in Azure CLI tools. The weekly scheduled tasks keep the data fresh.
  If the target agent has a Cost Management/ARG **connector**, you can switch to live fetching with `window.sreagent.callTool`.

## Known limitations

- The subscription picker in the Month-to-Month report only updates the label. Data shows whatever was baked in. For per-subscription filtering, add `sub` to each `resources` entry and filter in `render`.
- Cost queries use `az rest --method post`, which the agent classifies as a write. In Review mode each run asks for approval; scheduled tasks need Autonomous mode or pre-approved permissions.
- Month-to-Month report formats money with `$`. For non-USD currencies, follow step 5 of prompt 02.
- Advisor `extendedProperties` field names differ by recommendation type. Prompt 04 has the agent sample rows first.
- Cost queries and the tool mapping were verified in the source environment. Advisor, budget, and forecast queries follow standard API shapes and should be checked on first run (prompt 06, last item).

## Publishing and environment data

Keep the `knowledge/`, `prompts/`, `reports/`, `setup/`, and `skills/` directories together when copying or publishing this kit. Their relative paths are used throughout the instructions.

Publish only generic templates, prompts, skills, and the example placeholder file. Do not commit populated reports, private placeholder files, generated customer output, credentials, or `cost-environment.md`. Reporting is the intended workflow, not an enforcement boundary: verify effective permissions and enabled tools, and require explicit approval before resource changes or commitment purchases. Savings are estimates until measured after approved actions.
