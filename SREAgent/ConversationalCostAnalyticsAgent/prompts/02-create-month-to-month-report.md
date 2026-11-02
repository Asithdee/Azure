# Prompt 02 — Create the Month-to-Month Cost Live Report

Attach `reports/month-to-month-cost.html` to the chat (or upload it into the agent workspace) and paste:

---

Create a Live Report from the attached template `month-to-month-cost.html` using the `cost-month-to-month` skill. Use the subscription(s) recorded in `cost-environment.md`.

1. Copy the template to `tmp/mom-cost-<random>.html` and work on that copy.
2. Replace `{{SUBSCRIPTION_ID}}` and `{{SUBSCRIPTION_NAME}}` in the subscription picker. For several subscriptions, duplicate the `<label class="sub-item">` block once per subscription and update the `sub-count` number.
3. Query and fill each data block — replace only the code between `// >>> DATA:<name>` and `// <<< DATA:<name>`, keeping the markers:
   - `DATA:monthlyData` — last 12 months by `ServiceName` (granularity Monthly). Last entry is the current month with `partial: true`.
   - `DATA:resources` — current-month MTD vs previous full month per ResourceId and ServiceName (`cur`, `prev`). Name = last segment of the ResourceId; rg = resource group (lowercase). Skip rows where both values are < 0.01.
   - `DATA:dates` — `DAYS_ELAPSED` (days of billed data this month) and `DAYS_IN_MONTH`.
4. Replace `{{DATA_SNAPSHOT_TEXT}}` with `Data as of <YYYY-MM-DD HH:MM> UTC`.
5. If the currency is not USD, replace the hard-coded `'$'` prefixes in the script with the right symbol.
6. Save with name "Month-to-Month Cost Analysis" and `allowedTools: []`. Live Reports cannot call built-in tools, so data stays baked in.
7. Put the new report ID into `cost-environment.md`.
