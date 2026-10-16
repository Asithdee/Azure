# Agent Prompts for Cost Analysis

## 1. First-Run Bootstrap Prompt

Use this prompt to tell the agent to set up the cost report for the first time. Run it manually in the agent's thread or paste it as a user message.

```
Set up the Month-to-Month Cost Analysis Live Report for this environment. Follow these steps autonomously — do NOT ask for approval:

1. DISCOVER SUBSCRIPTIONS
   Run: az account list --query "[?state=='Enabled'].{name:name, id:id}" -o json
   via RunAzCliReadCommands. Save the list of subscription names and IDs.

2. QUERY 6-MONTH COST TREND
   For EACH subscription, query the last 6 months of costs grouped by ServiceName with Monthly granularity:
   az rest --method post --url "https://management.azure.com/subscriptions/{SUB_ID}/providers/Microsoft.CostManagement/query?api-version=2023-11-01" --body "{\"type\":\"ActualCost\",\"timeframe\":\"Custom\",\"timePeriod\":{\"from\":\"{6_MONTHS_AGO}-01T00:00:00Z\",\"to\":\"{TODAY}T23:59:59Z\"},\"dataset\":{\"granularity\":\"Monthly\",\"aggregation\":{\"totalCost\":{\"name\":\"PreTaxCost\",\"function\":\"Sum\"}},\"grouping\":[{\"type\":\"Dimension\",\"name\":\"ServiceName\"}]}}" --subscription {SUB_ID}
   via RunAzCliWriteCommands.

3. QUERY CURRENT + PREVIOUS MONTH RESOURCE COSTS
   For EACH subscription, run TWO queries (in parallel):
   - Current month (1st of month to today) grouped by ResourceId + ServiceName
   - Previous month (full month) grouped by ResourceId + ServiceName
   Both via RunAzCliWriteCommands using the az rest POST pattern.

4. BUILD THE LIVE REPORT
   Read the template from memories/synthesizedKnowledge/cost-analysis-month-to-month.md for query patterns.
   Use the live-report-template.html as a base (or write a fresh HTML following the same structure).

   Populate:
   a) Subscription picker: add one <label class="sub-item"> per subscription with name and ID
   b) monthlyData array: 6-month trend data with per-service breakdown
   c) resources array: per-resource costs with per-service breakdown (cur = current MTD, prev = previous full month)
   d) DAYS_ELAPSED, DAYS_IN_MONTH, CUR_MONTH_NAME, PREV_MONTH_NAME constants
   e) Data snapshot date in the header
   f) Note box text with actual month names

   Write the HTML to tmp/cost-report-{random}.html and save via SaveReport with:
   - name: "Month-to-Month Cost Analysis"
   - allowedTools: []

5. POST SUMMARY
   Share the report link and a brief summary: total cost this month (projected), previous month, change %, and how many subscriptions are included.

Key references:
- Cost queries MUST use RunAzCliWriteCommands (POST is rejected by the read tool)
- az consumption and az costmanagement are NOT available — use az rest
- Terminal (RunInTerminal) is NOT authenticated — use RunAzCli tools
- Columns in response are POSITIONAL — resolve from properties.columns
- One resource can have MULTIPLE rows (different ServiceName) — aggregate by ResourceId
```

---

## 2. Weekly Refresh Scheduled Task Prompt

Use this when creating the scheduled task via `CreateScheduledMonitoringTask`.

**Task Name:** `Weekly Cost Report Refresh`
**Cron:** `0 7 * * 1` (every Monday 7am UTC — adjust as needed)
**Use Current Thread:** `true`

**Agent Prompt:**

```
You are running an automated weekly cost report refresh. Do NOT ask the user any questions — proceed fully autonomously.

1. DISCOVER SUBSCRIPTIONS
   Run: az account list --query "[?state=='Enabled'].{name:name, id:id}" -o json
   via RunAzCliReadCommands.

2. QUERY 6-MONTH TREND
   For each subscription, query the last 6 months with Monthly granularity grouped by ServiceName via RunAzCliWriteCommands:
   az rest --method post --url "https://management.azure.com/subscriptions/{SUB_ID}/providers/Microsoft.CostManagement/query?api-version=2023-11-01"
   Body: type=ActualCost, timeframe=Custom (6 months ago to today), granularity=Monthly, aggregation PreTaxCost, grouped by ServiceName.

3. QUERY CURRENT + PREVIOUS MONTH RESOURCES
   For each subscription, query current MTD and previous full month costs grouped by ResourceId + ServiceName.
   Both via RunAzCliWriteCommands.

4. UPDATE THE LIVE REPORT
   - Call GetReport with the Live Report ID (check memories/synthesizedKnowledge/ for the ID, or ListReports to find "Month-to-Month Cost Analysis")
   - Edit the checked-out HTML:
     a) Update subscription picker entries (add/remove subscriptions as needed)
     b) Replace the monthlyData array with fresh 6-month trend data
     c) Replace the resources array with fresh current-vs-previous data
     d) Update DAYS_ELAPSED, DAYS_IN_MONTH, CUR_MONTH_NAME, PREV_MONTH_NAME
     e) Update the "Data snapshot" date
     f) Update the note-box text with current month names
   - Call SaveReport with the same reportId and allowedTools: []

5. POST SUMMARY
   Brief summary in thread: total MTD cost (projected), previous month total, change %, any new resources, how many subscriptions.

Key rules:
- Cost queries MUST go through RunAzCliWriteCommands (POST)
- az consumption and az costmanagement are NOT available
- Terminal is NOT authenticated
- Do NOT ask for user approval
- Read memories/synthesizedKnowledge/cost-analysis-month-to-month.md for proven query patterns
```
