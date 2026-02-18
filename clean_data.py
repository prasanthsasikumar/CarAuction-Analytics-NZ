import pandas as pd
import glob
import re
from datetime import datetime
import sqlite3
import os

def clean_price(price_str):
    """Clean price strings and convert to float"""
    if pd.isna(price_str) or price_str == 'N/A':
        return None
    try:
        cleaned = str(price_str).replace('$', '').replace(',', '').strip()
        return float(cleaned)
    except:
        return None

def clean_mileage(mileage_str):
    """Clean mileage strings and convert to float"""
    if pd.isna(mileage_str) or mileage_str == 'N/A':
        return None
    try:
        cleaned = str(mileage_str).replace(',', '').strip()
        return float(cleaned)
    except:
        return None

def extract_year(link_str):
    """Extract year from vehicle link"""
    if pd.isna(link_str):
        return None
    match = re.search(r'/(\d{4})-', str(link_str))
    return int(match.group(1)) if match else None

def extract_vehicle_id(link_str):
    """Extract vehicle ID from link"""
    if pd.isna(link_str):
        return None
    match = re.search(r'/(\d{18})/', str(link_str))
    return match.group(1) if match else None

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

def calculate_damage_score(damage_text):
    """Calculate numerical damage score based on keywords"""
    if pd.isna(damage_text):
        return 0
    
    damage_text = str(damage_text).lower()
    score = 0
    
    damage_weights = {
        'airbag': 500,
        'fire': 1000,
        'water': 800,
        'stolen': 300,
        'vandalised': 400,
        'heavy': 600,
        'medium': 300,
        'light': 100
    }
    
    for keyword, weight in damage_weights.items():
        if keyword in damage_text:
            score += weight
    
    return score

def load_all_data():
    """Load all CSV files with date information"""
    print("Loading CSV files...")
    all_data = []
    csv_files = sorted(glob.glob('data/raw/car_data_*.csv'))
    
    total_files = len(csv_files)
    for idx, file in enumerate(csv_files, 1):
        if idx % 50 == 0:
            print(f"  Loaded {idx}/{total_files} files...")
        
        # Extract date from filename, handle both Windows and Unix path separators
        basename = os.path.basename(file)
        date_str = basename.replace('car_data_', '').replace('.csv', '')
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            df = pd.read_csv(file)
            df['scrape_date'] = date
            df['source_file'] = file
            all_data.append(df)
        except Exception as e:
            print(f"  Error loading {file}: {e}")
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        print(f"✓ Loaded {len(combined_df)} total records from {len(csv_files)} files")
        return combined_df
    return pd.DataFrame()

def clean_car_data(df):
    """Clean and standardize car auction data"""
    print("\nCleaning data...")
    
    # Basic cleaning
    df['Price_USD'] = df['Price'].apply(clean_price)
    df['Mileage_Miles'] = df['Mileage'].apply(clean_mileage)
    df['Transmission_Type'] = df['Transmission'].str.strip().str.rstrip(',')
    df['Is_Registered'] = df['Registration Status'].apply(
        lambda x: True if str(x).strip().lower() == 'yes' else False
    )
    
    # Extract structured data
    df['Year'] = df['Link'].apply(extract_year)
    df['Vehicle_ID'] = df['Link'].apply(extract_vehicle_id)
    
    # Parse damage information
    df['Has_Airbag_Deployed'] = df['Damage description'].str.contains(
        'Airbag', case=False, na=False
    )
    df['Has_Water_Damage'] = df['Damage description'].str.contains(
        'Water', case=False, na=False
    )
    df['Has_Fire_Damage'] = df['Damage description'].str.contains(
        'Fire', case=False, na=False
    )
    df['Is_Stolen_Recovered'] = df['Damage description'].str.contains(
        'Stolen', case=False, na=False
    )
    df['Is_Vandalized'] = df['Damage description'].str.contains(
        'Vandal', case=False, na=False
    )
    df['Impact_Severity'] = df['Damage description'].apply(extract_impact_severity)
    df['Damage_Score'] = df['Damage description'].apply(calculate_damage_score)
    
    # Convert numeric columns to proper types
    df['Seats'] = pd.to_numeric(df['Seats'], errors='coerce')
    df['Keys'] = pd.to_numeric(df['Keys'], errors='coerce').fillna(0).astype(int)
    
    print(f"✓ Cleaned {len(df)} records")
    return df

def add_derived_features(df):
    """Add computed fields for analysis"""
    print("\nAdding derived features...")
    
    # Age calculation
    current_year = datetime.now().year
    df['Age'] = current_year - df['Year']
    df['Age'] = df['Age'].clip(lower=0)  # No negative ages
    
    # Price per year (rough value metric)
    df['Price_Per_Year'] = df['Price_USD'] / df['Age'].replace(0, 1)
    
    # Sort for time-based calculations
    df = df.sort_values(['Vehicle_ID', 'scrape_date'])
    
    # Days on market
    df['First_Seen'] = df.groupby('Vehicle_ID')['scrape_date'].transform('min')
    df['Last_Seen'] = df.groupby('Vehicle_ID')['scrape_date'].transform('max')
    df['Days_Listed'] = (df['Last_Seen'] - df['First_Seen']).dt.days
    
    # Price changes
    df['Initial_Price'] = df.groupby('Vehicle_ID')['Price_USD'].transform('first')
    df['Final_Price'] = df.groupby('Vehicle_ID')['Price_USD'].transform('last')
    df['Price_Change'] = df['Final_Price'] - df['Initial_Price']
    df['Price_Change_Pct'] = (df['Price_Change'] / df['Initial_Price'] * 100).round(2)
    
    # Is this the latest record for this vehicle?
    df['Is_Latest'] = df.groupby('Vehicle_ID')['scrape_date'].transform('max') == df['scrape_date']
    
    # Price bins
    df['Price_Range'] = pd.cut(
        df['Price_USD'],
        bins=[0, 500, 1000, 2000, 3000, 5000, 10000, 20000, 50000, 999999],
        labels=['<500', '500-1k', '1-2k', '2-3k', '3-5k', '5-10k', '10-20k', '20-50k', '50k+']
    )
    
    print(f"✓ Added derived features")
    return df

def deduplicate_and_clean(df):
    """Remove duplicates and handle missing values"""
    print("\nDeduplicating and final cleaning...")
    
    initial_count = len(df)
    
    # Remove exact duplicates
    df = df.drop_duplicates(subset=['Vehicle_ID', 'scrape_date'])
    print(f"  Removed {initial_count - len(df)} duplicate records")
    
    # Fill missing mileage with group median
    df['Mileage_Miles'] = df.groupby(['Manufacturer', 'Model', 'Year'])['Mileage_Miles'].transform(
        lambda x: x.fillna(x.median())
    )
    
    # Drop rows with missing critical fields
    before_drop = len(df)
    df = df.dropna(subset=['Price_USD', 'Manufacturer', 'Model', 'Vehicle_ID'])
    print(f"  Removed {before_drop - len(df)} records with missing critical data")
    
    print(f"✓ Final dataset: {len(df)} records")
    return df

def create_public_dataset(df):
    """Create anonymized public version"""
    print("\nCreating public dataset...")
    
    public_columns = [
        'scrape_date',
        'Manufacturer',
        'Model',
        'Year',
        'Age',
        'Price_USD',
        'Price_Range',
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
        'Is_Vandalized',
        'Damage_Score',
        'Days_Listed',
        'Price_Change_Pct',
        'Is_Latest'
    ]
    
    # Keep only public columns that exist
    available_columns = [col for col in public_columns if col in df.columns]
    public_df = df[available_columns].copy()
    
    print(f"✓ Public dataset ready: {len(public_df)} records with {len(available_columns)} columns")
    return public_df

def create_aggregated_dataset(df):
    """Create aggregated statistics"""
    print("\nCreating aggregated statistics...")
    
    # Daily aggregates
    daily_stats = df.groupby('scrape_date').agg({
        'Price_USD': ['mean', 'median', 'std', 'min', 'max', 'count'],
        'Mileage_Miles': ['mean', 'median'],
        'Days_Listed': ['mean', 'median', 'max'],
        'Damage_Score': 'mean',
        'Is_Registered': 'sum',
        'Manufacturer': 'nunique',
        'Vehicle_ID': 'nunique'
    }).reset_index()
    
    daily_stats.columns = ['_'.join(col).strip('_') for col in daily_stats.columns.values]
    
    # Manufacturer trends
    mfg_trends = df.groupby(['scrape_date', 'Manufacturer']).agg({
        'Price_USD': ['mean', 'count'],
        'Vehicle_ID': 'nunique'
    }).reset_index()
    
    mfg_trends.columns = ['_'.join(col).strip('_') for col in mfg_trends.columns.values]
    
    print(f"✓ Daily stats: {len(daily_stats)} days")
    print(f"✓ Manufacturer trends: {len(mfg_trends)} records")
    
    return daily_stats, mfg_trends

def export_data(public_df, daily_stats, mfg_trends):
    """Export cleaned data in multiple formats"""
    print("\nExporting data...")
    
    # Create output directory
    os.makedirs('data/processed', exist_ok=True)
    
    # CSV exports
    public_df.to_csv('data/processed/car_auction_public.csv', index=False)
    daily_stats.to_csv('data/processed/daily_statistics.csv', index=False)
    mfg_trends.to_csv('data/processed/manufacturer_trends.csv', index=False)
    print("✓ Exported CSV files")
    
    # Parquet exports (compressed)
    public_df.to_parquet('data/processed/car_auction_public.parquet', index=False, compression='snappy')
    print("✓ Exported Parquet files")
    
    # SQLite database
    conn = sqlite3.connect('data/processed/car_auction_data.db')
    public_df.to_sql('listings', conn, if_exists='replace', index=False)
    daily_stats.to_sql('daily_stats', conn, if_exists='replace', index=False)
    mfg_trends.to_sql('manufacturer_trends', conn, if_exists='replace', index=False)
    conn.close()
    print("✓ Exported SQLite database")
    
    # Summary report
    with open('data/processed/DATA_SUMMARY.txt', 'w') as f:
        f.write("Car Auction Data - Cleaning Summary\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total Records: {len(public_df):,}\n")
        f.write(f"Unique Vehicles: {public_df['Vehicle_ID'].nunique() if 'Vehicle_ID' in public_df else 'N/A'}\n")
        f.write(f"Date Range: {public_df['scrape_date'].min()} to {public_df['scrape_date'].max()}\n")
        f.write(f"Manufacturers: {public_df['Manufacturer'].nunique()}\n")
        f.write(f"Average Price: ${public_df['Price_USD'].mean():.2f}\n")
        f.write(f"Median Price: ${public_df['Price_USD'].median():.2f}\n")
        f.write(f"\nTop 10 Manufacturers:\n")
        for mfg, count in public_df['Manufacturer'].value_counts().head(10).items():
            f.write(f"  {mfg}: {count:,}\n")
    
    print("✓ Created summary report")
    print(f"\n📁 All files saved to: data/processed/")

def main():
    """Execute complete data cleaning pipeline"""
    print("=" * 60)
    print("Car Auction Data Cleaning Pipeline")
    print("=" * 60)
    
    # Load raw data
    df = load_all_data()
    
    if df.empty:
        print("❌ No data loaded. Exiting.")
        return
    
    # Clean data
    df = clean_car_data(df)
    
    # Add features
    df = add_derived_features(df)
    
    # Deduplicate
    df = deduplicate_and_clean(df)
    
    # Create public version
    public_df = create_public_dataset(df)
    
    # Create aggregates
    daily_stats, mfg_trends = create_aggregated_dataset(df)
    
    # Export everything
    export_data(public_df, daily_stats, mfg_trends)
    
    print("\n" + "=" * 60)
    print("✅ Data cleaning pipeline completed successfully!")
    print("=" * 60)
    
    return public_df, daily_stats, mfg_trends

if __name__ == '__main__':
    cleaned_data, stats, trends = main()
