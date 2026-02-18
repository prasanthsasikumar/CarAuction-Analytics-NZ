<<<<<<< HEAD
# 🚗 CarAuction Analytics NZ

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive data platform tracking vehicle auction listings from Manheim New Zealand. This project provides historical trends, price analytics, and insights into the used vehicle market with 991 days of data covering **460K+ auction records**.

🔗 **Live Demo:** [findcars.prasanthsasikumar.com](https://findcars.prasanthsasikumar.com)

## ✨ Features

- **📊 Interactive Analytics Dashboard** - Visualize price trends, manufacturer statistics, and damage patterns
- **📈 Real-Time Listings** - View latest vehicle auction data with interactive filtering
- **🔌 RESTful API** - Programmatic access to all data with multiple endpoints
- **🧹 Data Cleaning Pipeline** - Automated processing of raw scraper data
- **📥 Multiple Export Formats** - CSV, Parquet, and SQLite database exports
- **🤖 Daily Automated Scraping** - Fresh data collected every day

## 📊 Dataset Overview

| Metric | Value |
|--------|-------|
| **Time Period** | May 27, 2023 - February 18, 2026 |
| **Total Days** | 991 days |
| **Missing Days** | 8 (99.2% coverage) |
| **Total Records** | 460,000+ (cleaned) |
| **Manufacturers** | 500+ |
| **Data Fields** | 20+ attributes per vehicle |

### Missing Dates
- 2023-05-30
- 2023-07-19
- 2024-02-28 through 2024-03-04 (6 consecutive days)

## 🚀 Quick Start

### Prerequisites

- Python 3.13 or higher
- pip package manager
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/CarAuction-Analytics-NZ.git
cd CarAuction-Analytics-NZ
```

2. **Create and activate virtual environment**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
# Development server
python app_main.py

# Production server with Gunicorn (Linux/Mac)
gunicorn -c gunicorn_config.py app_main:app
```

5. **Access the application**
```
http://localhost:8000
```

## 📁 Project Structure

```
CarAuction-Analytics-NZ/
├── app_main.py                 # Main Flask application
├── clean_data.py               # Data cleaning pipeline
├── main.py                     # Web scraper (daily job)
├── requirements.txt            # Python dependencies
├── gunicorn_config.py          # Production server config
├── data/
│   ├── raw/                    # 991 daily CSV files
│   ├── processed/              # Cleaned datasets
│   │   ├── car_auction_public.csv
│   │   ├── car_auction_public.parquet
│   │   └── car_auction_data.db
│   └── *.csv                   # Additional data files
├── templates/                  # HTML templates
│   ├── index_main.html         # Landing page
│   ├── today.html              # Listings view
│   ├── analytics.html          # Analytics dashboard
│   ├── api_docs.html           # API documentation
│   └── about.html              # About page
├── src/
│   ├── scrapers/               # Scraper modules
│   └── utils/                  # Utility functions
└── docs/                       # Documentation

```

## 🔌 API Documentation

### Base URL
```
https://findcars.prasanthsasikumar.com/api/v1
```

### Endpoints

#### Get Overview Statistics
```http
GET /api/v1/stats/overview
```

Returns aggregated statistics from the most recent 30 days.

**Response:**
```json
{
  "total_listings": 45000,
  "unique_vehicles": 12000,
  "manufacturers": 500,
  "avg_price": 2500.50,
  "median_price": 1800.00,
  "top_manufacturers": {
    "Toyota": 8500,
    "Mazda": 6200
  }
}
```

#### Get Price Trends
```http
GET /api/v1/stats/price-trends
```

Returns historical price trends (sampled every 7 days).

#### Search Vehicles
```http
GET /api/v1/search?manufacturer=Toyota&max_price=5000
```

**Parameters:**
- `manufacturer` - Filter by manufacturer
- `model` - Filter by model
- `max_price` - Maximum price
- `min_price` - Minimum price

#### Download Data
```http
GET /api/v1/download/latest      # Latest raw CSV
GET /api/v1/download/processed   # Cleaned dataset
```

For complete API documentation, visit: [/api-docs](https://findcars.prasanthsasikumar.com/api-docs)

## 🧹 Data Cleaning

The project includes a comprehensive data cleaning pipeline that:

1. Loads all 991 daily CSV files
2. Removes duplicates based on vehicle attributes
3. Cleans price and mileage data
4. Standardizes manufacturer and model names
5. Adds derived features (vehicle age, price changes)
6. Exports to multiple formats

**Run the cleaning pipeline:**
```bash
python clean_data.py
```

**Output files:**
- `data/processed/car_auction_public.csv` - Cleaned CSV (460K records)
- `data/processed/car_auction_public.parquet` - Parquet format
- `data/processed/car_auction_data.db` - SQLite database
- `data/processed/DATA_SUMMARY.txt` - Summary statistics

## 🕷️ Web Scraper

The scraper runs daily to collect fresh auction data.

**Manual scraping:**
```bash
python main.py
```

**Schedule with cron (Linux/Mac):**
```bash
# Add to crontab -e
0 2 * * * cd /path/to/CarAuction-Analytics-NZ && /path/to/.venv/bin/python main.py
```

## 📊 Use Cases

- **Market Research** - Analyze pricing trends and market dynamics
- **Price Prediction** - Train ML models for vehicle valuation
- **Academic Research** - Study depreciation patterns and damage types
- **Business Intelligence** - Inform inventory decisions for dealerships
- **Personal Use** - Track specific vehicles and get price alerts

## 🛠️ Technology Stack

**Backend:**
- Python 3.13
- Flask (Web framework)
- Pandas (Data processing)
- BeautifulSoup4 (Web scraping)
- Gunicorn (Production server)

**Frontend:**
- Bootstrap 5
- Chart.js (Visualizations)
- DataTables (Interactive tables)
- Font Awesome (Icons)

**Data Storage:**
- SQLite
- Parquet (PyArrow)
- CSV

## 🚀 Deployment

### Production Setup

1. **Configure Gunicorn**
```python
# gunicorn_config.py
bind = '0.0.0.0:8000'
workers = 4
module = 'app_main:app'
```

2. **Start Gunicorn**
```bash
gunicorn -c gunicorn_config.py app_main:app
```

3. **Setup Nginx (optional)**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⚠️ Disclaimer

This data is for informational and research purposes only. Prices and availability should be verified directly with Manheim NZ. This project follows ethical web scraping practices and respects robots.txt.

## 🔮 Future Plans

- [ ] Implement XGBoost price prediction model
- [ ] Add email price alerts for tracked vehicles
- [ ] Expand to other auction platforms
- [ ] Build recommendation engine
- [ ] Mobile app for iOS/Android
- [ ] Export to Excel/Google Sheets

## 📧 Contact

Prasanth Sasikumar - [prasanthsasikumar.com](https://prasanthsasikumar.com)

Project Link: [https://github.com/yourusername/CarAuction-Analytics-NZ](https://github.com/yourusername/CarAuction-Analytics-NZ)

---

⭐ If you find this project useful, please consider giving it a star!
