# GitHub Actions Workflows

## Daily Scraper Workflow

**File**: `daily-scrape.yml`

### What it does:
- Runs automatically every day at 12:00 PM UTC
- Scrapes auction data from Manheim NZ
- Saves new CSV file to `data/raw/`
- Commits and pushes the data back to the repository

### Manual Trigger:
1. Go to the **Actions** tab in your GitHub repo
2. Select "Daily Auction Data Scraper"
3. Click "Run workflow"

### Monitoring:
- Check the Actions tab to see run history
- Green checkmark = successful scrape
- Red X = scraping failed (likely blocked or site down)
- View logs for detailed output

### Timezone:
Currently set to **12:00 PM UTC**. To change:
- Edit the cron expression: `0 12 * * *`
  - Format: `minute hour day month day-of-week`
  - Example: `0 2 * * *` = 2:00 AM UTC daily

### Permissions:
Uses default `GITHUB_TOKEN` - no setup required!

### Troubleshooting:
If scraping fails with 403 errors, GitHub Actions IPs might be blocked too. In that case:
1. Use Windows Task Scheduler on your local machine
2. Manually commit and push daily scrapes
