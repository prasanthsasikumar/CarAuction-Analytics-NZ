# Scraper Modules

This directory contains the web scraping modules for collecting vehicle auction data from Manheim NZ.

## Files

- **main.py** - Main scraper orchestrator that runs the daily scraping job
- **ScrapeVehiclePage.py** - Module for parsing individual vehicle pages
- **CSVSaver.py** - Utility for saving scraped data to CSV files
- **PageLengthFinder.py** - Helper to determine pagination

## Usage

To run the scraper manually:

```bash
# From project root
python src/scrapers/main.py
```

The scraper will:
1. Fetch all vehicle listings from Manheim NZ
2. Parse vehicle details (make, model, price, damage, etc.)
3. Save data to `data/raw/car_data_YYYY-MM-DD.csv`

## Scheduling

For automated daily scraping, set up a cron job (Linux/Mac) or Task Scheduler (Windows):

**Linux/Mac (crontab):**
```bash
# Run at 2 AM daily
0 2 * * * cd /path/to/project && /path/to/.venv/bin/python src/scrapers/main.py
```

**Windows (Task Scheduler):**
- Create a new task
- Trigger: Daily at 2:00 AM
- Action: Run program
  - Program: `C:\path\to\.venv\Scripts\python.exe`
  - Arguments: `src\scrapers\main.py`
  - Start in: `C:\path\to\Website-Scrapper`

## Output

Each run creates a new CSV file in `data/raw/` with today's date.
