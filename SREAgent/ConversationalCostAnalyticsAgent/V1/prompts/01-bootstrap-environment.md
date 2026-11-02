# Prompt 01 — Bootstrap a new environment

Paste into the new agent's chat **after** importing the skills and uploading the knowledge doc (see README).

---

You are being set up with the portable Azure cost-analysis kit. Do the following, in order, and stop to ask me only if a step is blocked.

1. Discover the environment: list enabled subscriptions I can access (Resource Graph `ResourceContainers`). If more than one, ask me which subscription(s) are in scope.
2. Verify cost access: run a `MonthToDate` Cost Management query grouped by `ServiceName` for each in-scope subscription using the `cost-month-to-month` skill (POST via the write CLI tool). If it returns `AuthorizationFailed`/`RBACAccessDenied`, give me the exact `az role assignment create` command to grant **Cost Management Reader** to your managed identity on that scope, and wait.
3. Record the billing currency from the `Currency` column.
4. Save a memory file `memories/synthesizedKnowledge/cost-environment.md` with: in-scope subscription IDs and names, currency, which query patterns worked/failed here, and placeholders for the three Live Report IDs and two scheduled task IDs (to fill in after prompts 02–05). Link it from `overview.md`.
5. Reply with a 5-line summary: subscriptions, currency, MTD total, top 3 services, and anything that failed.
