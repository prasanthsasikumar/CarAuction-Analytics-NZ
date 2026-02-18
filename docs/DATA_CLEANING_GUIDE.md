# Data Cleaning & Public Distribution Guide
# Car Auction Data - Manheim NZ

## 🔍 Current Data Issues

### 1. **Data Quality Problems**
- Missing values in Mileage (N/A)
- Inconsistent price formatting ($1,800 vs $1800)
- Missing keys count (0 means no keys available)
- Links contain session/tracking parameters
- Transmission field has trailing commas ("CVT,")
- Damage descriptions are unstructured text

### 2. **Privacy & Legal Considerations**
- Direct links to auction pages (may violate terms of service)
- No license information for data redistribution
- Potential PII in tracking URLs

## 🧹 Data Cleaning Steps

### Step 1: Standardize Formats
```python
import pandas as pd
import re

def clean_car_data(df):
    """Clean and standardize car auction data"""
    
    # 1. Clean Price - Remove currency and commas
    df['Price_USD'] = df['Price'].apply(lambda x: 
        float(re.sub(r'[^\d.]', '', str(x))) if pd.notna(x) and x != 'N/A' else None
    )
    
    # 2. Clean Mileage - Remove commas
    df['Mileage_Miles'] = df['Mileage'].apply(lambda x:
        float(re.sub(r'[^\d.]', '', str(x))) if pd.notna(x) and x != 'N/A' else None
    )
    
    # 3. Standardize Transmission
    df['Transmission_Type'] = df['Transmission'].str.strip().str.rstrip(',')
    
    # 4. Registration Status - Boolean
    df['Is_Registered'] = df['Registration Status'].apply(lambda x: 
        True if str(x).lower() == 'yes' else False
    )
    
    # 5. Extract Year from Model or Damage Description
    df['Year'] = df['Link'].str.extract(r'/(\d{4})-')
    
    # 6. Parse Damage Types into Categories
    df['Has_Airbag_Deployed'] = df['Damage description'].str.contains('Airbag', case=False, na=False)
    df['Has_Water_Damage'] = df['Damage description'].str.contains('Water', case=False, na=False)
    df['Has_Fire_Damage'] = df['Damage description'].str.contains('Fire', case=False, na=False)
    df['Is_Stolen_Recovered'] = df['Damage description'].str.contains('Stolen', case=False, na=False)
    df['Impact_Severity'] = df['Damage description'].apply(extract_impact_severity)
    
    # 7. Remove or hash sensitive links
    df['Vehicle_ID'] = df['Link'].str.extract(r'/(\d{18})/')
    
    return df

def extract_impact_severity(damage_text):
    """Extract highest impact severity from damage description"""
    if pd.isna(damage_text):
        return 'Unknown'
    damage_text = str(damage_text).lower()
    if 'impact heavy' in damage_text:
        return 'Heavy'
    elif 'impact medium' in damage_text:
        return 'Medium'
    elif 'impact light' in damage_text:
        return 'Light'
    return 'None'
```

### Step 2: Create Derived Features
```python
def add_derived_features(df):
    """Add computed fields for analysis"""
    
    # Price per year (depreciation proxy)
    current_year = 2026
    df['Age'] = current_year - pd.to_numeric(df['Year'], errors='coerce')
    df['Price_Per_Year'] = df['Price_USD'] / df['Age'].replace(0, 1)
    
    # Days on market (requires time series data)
    df['First_Seen'] = df.groupby('Vehicle_ID')['scrape_date'].transform('min')
    df['Last_Seen'] = df.groupby('Vehicle_ID')['scrape_date'].transform('max')
    df['Days_Listed'] = (df['Last_Seen'] - df['First_Seen']).dt.days
    
    # Price changes
    df['Initial_Price'] = df.groupby('Vehicle_ID')['Price_USD'].transform('first')
    df['Current_Price'] = df.groupby('Vehicle_ID')['Price_USD'].transform('last')
    df['Price_Change'] = df['Current_Price'] - df['Initial_Price']
    df['Price_Change_Pct'] = (df['Price_Change'] / df['Initial_Price'] * 100).round(2)
    
    # Damage severity score
    damage_weights = {
        'Airbag': 500,
        'Fire': 1000,
        'Water': 800,
        'Stolen': 300,
        'Heavy': 600,
        'Medium': 300,
        'Light': 100
    }
    
    df['Damage_Score'] = 0
    for keyword, weight in damage_weights.items():
        df['Damage_Score'] += df['Damage description'].str.contains(keyword, case=False, na=False) * weight
    
    return df
```

### Step 3: Remove Duplicates & Handle Missing Data
```python
def deduplicate_and_clean(df):
    """Remove duplicates and handle missing values"""
    
    # Remove exact duplicates
    df = df.drop_duplicates(subset=['Vehicle_ID', 'scrape_date'])
    
    # For time series analysis, keep one record per car per day
    df = df.sort_values(['Vehicle_ID', 'scrape_date'])
    
    # Fill missing mileage with group median (by manufacturer/model/year)
    df['Mileage_Miles'] = df.groupby(['Manufacturer', 'Model', 'Year'])['Mileage_Miles'].transform(
        lambda x: x.fillna(x.median())
    )
    
    # Drop rows with missing critical fields
    df = df.dropna(subset=['Price_USD', 'Manufacturer', 'Model'])
    
    return df
```

## 📊 Creating Public Dataset

### Option 1: Anonymized Daily Snapshots
```python
def create_public_dataset(df):
    """Create anonymized public version"""
    
    public_df = df[[
        'scrape_date',
        'Manufacturer',
        'Model',
        'Year',
        'Price_USD',
        'Mileage_Miles',
        'Transmission_Type',
        'Fuel Type',
        'Seats',
        'Is_Registered',
        'Keys',
        'Impact_Severity',
        'Has_Airbag_Deployed',
        'Has_Water_Damage',
        'Has_Fire_Damage',
        'Is_Stolen_Recovered',
        'Damage_Score',
        'Days_Listed',
        'Price_Change_Pct'
    ]].copy()
    
    # Remove original links and IDs
    # Add general categorical bins instead of exact values
    public_df['Price_Range'] = pd.cut(public_df['Price_USD'], 
        bins=[0, 1000, 3000, 5000, 10000, 50000],
        labels=['<1k', '1-3k', '3-5k', '5-10k', '10k+']
    )
    
    return public_df
```

### Option 2: Aggregated Statistics
```python
def create_aggregated_dataset(df):
    """Create aggregated dataset (no individual cars)"""
    
    daily_stats = df.groupby('scrape_date').agg({
        'Price_USD': ['mean', 'median', 'std', 'min', 'max', 'count'],
        'Mileage_Miles': ['mean', 'median'],
        'Days_Listed': ['mean', 'median'],
        'Damage_Score': 'mean',
        'Is_Registered': lambda x: (x == True).sum(),
        'Manufacturer': 'nunique'
    }).reset_index()
    
    # Manufacturer trends
    mfg_trends = df.groupby(['scrape_date', 'Manufacturer']).agg({
        'Price_USD': 'mean',
        'Vehicle_ID': 'count'
    }).reset_index()
    
    return daily_stats, mfg_trends
```

## 🚀 Distribution Formats

### 1. **CSV/Parquet Files**
Best for: Data scientists, researchers
```python
# Save cleaned data
public_df.to_csv('manheim_nz_cleaned.csv', index=False)
public_df.to_parquet('manheim_nz_cleaned.parquet', index=False)
```

### 2. **SQLite Database**
Best for: Analysts, app developers
```python
import sqlite3

conn = sqlite3.connect('car_auction_data.db')
public_df.to_sql('daily_listings', conn, if_exists='replace', index=False)
daily_stats.to_sql('daily_aggregates', conn, if_exists='replace', index=False)
conn.close()
```

### 3. **JSON API**
Best for: Web applications
```python
# Already implemented in dashboard.py
# Add data export endpoint
@app.route('/api/export', methods=['GET'])
def export_data():
    format_type = request.args.get('format', 'json')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Filter and export
    if format_type == 'json':
        return jsonify(filtered_df.to_dict('records'))
    elif format_type == 'csv':
        return send_file(csv_buffer, mimetype='text/csv')
```

### 4. **Kaggle Dataset**
Steps:
1. Clean data using above scripts
2. Create comprehensive README with:
   - Data dictionary
   - Collection methodology
   - Use cases
   - Citation requirements
3. Upload to Kaggle Datasets
4. Add license (CC BY 4.0 or similar)

## 📝 Data Dictionary

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| scrape_date | date | Date data was collected | 2023-05-27 |
| Manufacturer | string | Car manufacturer | Toyota |
| Model | string | Car model | Corolla |
| Year | int | Manufacturing year | 2015 |
| Price_USD | float | Asking price | 2500.00 |
| Mileage_Miles | float | Odometer reading | 125000 |
| Transmission_Type | string | Transmission | Automatic |
| Fuel Type | string | Fuel type | Petrol |
| Seats | int | Number of seats | 5 |
| Is_Registered | boolean | Currently registered | True |
| Keys | int | Number of keys | 1 |
| Impact_Severity | string | Damage severity | Heavy/Medium/Light |
| Has_Airbag_Deployed | boolean | Airbags deployed | False |
| Damage_Score | int | Calculated damage score | 800 |
| Days_Listed | int | Days on market | 14 |
| Price_Change_Pct | float | Price change % | -10.5 |

## ⚖️ Legal Considerations

### Before Publishing:
1. **Check Terms of Service**: Verify Manheim NZ ToS allows data scraping
2. **Remove Personal Data**: No VINs, seller names, exact locations
3. **Add Attribution**: Credit original source appropriately
4. **Choose License**: Recommend CC BY 4.0 for open use
5. **Disclaimer**: Add "for educational/research purposes only"

### Recommended License Text:
```
This dataset is derived from publicly available auction listings.
It is provided for educational and research purposes only.

License: Creative Commons Attribution 4.0 International (CC BY 4.0)
Attribution: Please cite this dataset in any publications or projects.

Disclaimer: This data is provided "as is" without warranty of any kind.
Users are responsible for compliance with all applicable laws and regulations.
```

## 🔄 Automated Cleaning Pipeline

```python
# Complete pipeline script
def full_cleaning_pipeline():
    """Execute complete data cleaning pipeline"""
    
    print("Loading raw data...")
    df = load_all_data()  # From dashboard.py
    
    print("Cleaning data...")
    df = clean_car_data(df)
    
    print("Adding derived features...")
    df = add_derived_features(df)
    
    print("Deduplicating...")
    df = deduplicate_and_clean(df)
    
    print("Creating public dataset...")
    public_df = create_public_dataset(df)
    
    print("Exporting...")
    public_df.to_csv('car_auction_public.csv', index=False)
    public_df.to_parquet('car_auction_public.parquet', index=False)
    
    # Create aggregated version
    daily_stats, mfg_trends = create_aggregated_dataset(df)
    daily_stats.to_csv('car_auction_daily_stats.csv', index=False)
    
    print(f"✅ Cleaned dataset: {len(public_df)} records")
    print(f"✅ Date range: {public_df['scrape_date'].min()} to {public_df['scrape_date'].max()}")
    print(f"✅ Unique vehicles: {public_df['Vehicle_ID'].nunique()}")
    
    return public_df, daily_stats

if __name__ == '__main__':
    cleaned_df, stats_df = full_cleaning_pipeline()
```

## 📦 Distribution Checklist

- [ ] Remove all direct links to auction pages
- [ ] Hash or remove vehicle IDs
- [ ] Clean and standardize all fields
- [ ] Add comprehensive data dictionary
- [ ] Create sample analysis notebooks
- [ ] Write clear README with use cases
- [ ] Add license file
- [ ] Test data loading in common tools (Python, R, Excel)
- [ ] Create validation tests
- [ ] Document any known limitations or biases

## 🎯 Suggested Public Use Cases

1. **Academic Research**: Market dynamics, pricing models
2. **ML Competitions**: Price prediction challenges
3. **Educational**: Data science tutorials, visualization examples
4. **Industry Analysis**: Used car market trends in NZ
5. **Tool Development**: Testing data analysis libraries
