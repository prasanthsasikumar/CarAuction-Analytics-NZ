"""
CarAuction Analytics NZ - Main Application
Professional web application for analyzing damaged vehicle auction data from Manheim NZ

This application combines:
- Real-time data viewing
- Historical analytics dashboard
- REST API for data access
- Admin scraper controls
"""

from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import pandas as pd
import datetime
import os
import glob
from pathlib import Path

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for API access

# Configuration
class Config:
    DATA_RAW_DIR = Path("data/raw")
    DATA_PROCESSED_DIR = Path("data/processed")
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'

app.config.from_object(Config)

# ==================== UTILITY FUNCTIONS ====================

def get_latest_data_file():
    """Get the most recent CSV file (today or yesterday)"""
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    
    today_file = Config.DATA_RAW_DIR / f"car_data_{today}.csv"
    yesterday_file = Config.DATA_RAW_DIR / f"car_data_{yesterday}.csv"
    
    if today_file.exists():
        return today_file
    elif yesterday_file.exists():
        return yesterday_file
    else:
        # Return most recent file
        files = sorted(Config.DATA_RAW_DIR.glob("car_data_*.csv"))
        return files[-1] if files else None

def clean_price(price_str):
    """Clean price strings and convert to float"""
    if pd.isna(price_str) or str(price_str) == 'N/A':
        return None
    try:
        cleaned = str(price_str).replace('$', '').replace(',', '').strip()
        return float(cleaned)
    except:
        return None

def clean_mileage(mileage_str):
    """Clean mileage strings and convert to float"""
    if pd.isna(mileage_str) or str(mileage_str) == 'N/A':
        return None
    try:
        cleaned = str(mileage_str).replace(',', '').strip()
        return float(cleaned)
    except:
        return None

# ==================== WEB ROUTES ====================

@app.route('/')
def view_today():
    """View today's/latest vehicle listings (default landing page)"""
    try:
        file_path = get_latest_data_file()
        if not file_path:
            return render_template('error.html', 
                                 error="No data files available",
                                 message="Please run the scraper to collect data.")
        
        data = pd.read_csv(file_path)
        
        # Add some computed columns for display
        data['Price_Clean'] = data['Price'].apply(clean_price)
        data['Mileage_Clean'] = data['Mileage'].apply(clean_mileage)
        
        # Get stats
        stats = {
            'total': len(data),
            'avg_price': round(data['Price_Clean'].mean(), 2) if data['Price_Clean'].notna().any() else 0,
            'registered': len(data[data['Registration Status'] == 'Yes']),
            'file_date': file_path.stem.replace('car_data_', ''),
            'top_manufacturer': data['Manufacturer'].mode()[0] if not data.empty else 'N/A'
        }
        
        # Convert to HTML table
        table_html = data.to_html(index=False, classes='table table-striped table-hover', 
                                   escape=False, border=0)
        
        return render_template('today.html', table=table_html, stats=stats)
    
    except Exception as e:
        return render_template('error.html', 
                             error=f"Error loading data: {str(e)}",
                             message="Please check if data files exist in data/raw/")

@app.route('/home')
def home():
    """Project landing page with navigation"""
    return render_template('index_main.html')

@app.route('/analytics')
def analytics():
    """Interactive analytics dashboard"""
    return render_template('analytics.html')

@app.route('/api-docs')
def api_docs():
    """API documentation page"""
    return render_template('api_docs.html')

@app.route('/about')
def about():
    """About page with project information"""
    return render_template('about.html')

# ==================== API ENDPOINTS ====================

@app.route('/api/v1/stats/overview')
def api_overview():
    """Get overview statistics from recent data"""
    try:
        # Load recent 30 days
        recent_files = sorted(glob.glob(str(Config.DATA_RAW_DIR / "car_data_*.csv")))[-30:]
        data_frames = [pd.read_csv(f) for f in recent_files if os.path.exists(f)]
        
        if not data_frames:
            return jsonify({'error': 'No data available'}), 404
        
        df = pd.concat(data_frames, ignore_index=True)
        df['Price_Clean'] = df['Price'].apply(clean_price)
        df['Mileage_Clean'] = df['Mileage'].apply(clean_mileage)
        
        stats = {
            'total_listings': len(df),
            'unique_vehicles': df['Link'].nunique() if 'Link' in df else 0,
            'manufacturers': df['Manufacturer'].nunique(),
            'avg_price': round(df['Price_Clean'].mean(), 2),
            'median_price': round(df['Price_Clean'].median(), 2),
            'min_price': round(df['Price_Clean'].min(), 2),
            'max_price': round(df['Price_Clean'].max(), 2),
            'avg_mileage': round(df['Mileage_Clean'].mean(), 2),
            'top_manufacturers': df['Manufacturer'].value_counts().head(10).to_dict(),
            'fuel_types': df['Fuel Type'].value_counts().to_dict() if 'Fuel Type' in df else {},
            'registration_status': df['Registration Status'].value_counts().to_dict()
        }
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/stats/price-trends')
def api_price_trends():
    """Get price trends over time"""
    try:
        csv_files = sorted(glob.glob(str(Config.DATA_RAW_DIR / "car_data_*.csv")))
        
        trends = []
        # Sample every 7 days for performance
        for file in csv_files[::7]:
            date_str = Path(file).stem.replace('car_data_', '')
            df = pd.read_csv(file)
            df['Price_Clean'] = df['Price'].apply(clean_price)
            
            trends.append({
                'date': date_str,
                'avg_price': round(df['Price_Clean'].mean(), 2),
                'median_price': round(df['Price_Clean'].median(), 2),
                'count': len(df)
            })
        
        return jsonify(trends)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/manufacturers')
def api_manufacturers():
    """Get manufacturer analysis"""
    try:
        recent_files = sorted(glob.glob(str(Config.DATA_RAW_DIR / "car_data_*.csv")))[-30:]
        data_frames = [pd.read_csv(f) for f in recent_files]
        df = pd.concat(data_frames, ignore_index=True)
        
        df['Price_Clean'] = df['Price'].apply(clean_price)
        
        manufacturer_stats = df.groupby('Manufacturer').agg({
            'Price_Clean': ['mean', 'median', 'count'],
            'Model': 'nunique'
        }).round(2)
        
        result = []
        for mfg in manufacturer_stats.index:
            result.append({
                'manufacturer': mfg,
                'avg_price': float(manufacturer_stats.loc[mfg, ('Price_Clean', 'mean')]),
                'median_price': float(manufacturer_stats.loc[mfg, ('Price_Clean', 'median')]),
                'count': int(manufacturer_stats.loc[mfg, ('Price_Clean', 'count')]),
                'unique_models': int(manufacturer_stats.loc[mfg, ('Model', 'nunique')])
            })
        
        # Sort by count
        result.sort(key=lambda x: x['count'], reverse=True)
        
        return jsonify(result[:50])  # Top 50
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/damage-analysis')
def api_damage_analysis():
    """Analyze damage types and frequency"""
    try:
        recent_files = sorted(glob.glob(str(Config.DATA_RAW_DIR / "car_data_*.csv")))[-30:]
        data_frames = [pd.read_csv(f) for f in recent_files]
        df = pd.concat(data_frames, ignore_index=True)
        
        damage_keywords = [
            'Front Damage', 'Rear Damage', 'Left', 'Right',
            'Airbags Deployed', 'Water Damage', 'Fire Damage',
            'Vandalised', 'Stolen', 'Impact Heavy', 'Impact Medium', 'Impact Light'
        ]
        
        damage_counts = {}
        for keyword in damage_keywords:
            count = df['Damage description'].str.contains(keyword, case=False, na=False).sum()
            if count > 0:
                damage_counts[keyword] = int(count)
        
        return jsonify(damage_counts)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/search')
def api_search():
    """Search for vehicles"""
    manufacturer = request.args.get('manufacturer', '').strip()
    model = request.args.get('model', '').strip()
    max_price = request.args.get('max_price', type=float)
    min_price = request.args.get('min_price', type=float)
    
    try:
        # Load latest file
        file_path = get_latest_data_file()
        if not file_path:
            return jsonify({'error': 'No data available'}), 404
        
        df = pd.read_csv(file_path)
        
        # Apply filters
        if manufacturer:
            df = df[df['Manufacturer'].str.contains(manufacturer, case=False, na=False)]
        if model:
            df = df[df['Model'].str.contains(model, case=False, na=False)]
        
        df['Price_Clean'] = df['Price'].apply(clean_price)
        
        if max_price:
            df = df[df['Price_Clean'] <= max_price]
        if min_price:
            df = df[df['Price_Clean'] >= min_price]
        
        # Convert to dict
        results = df.head(100).to_dict('records')
        
        return jsonify({
            'count': len(results),
            'results': results
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/download/latest')
def api_download_latest():
    """Download latest CSV file"""
    try:
        file_path = get_latest_data_file()
        if not file_path:
            return jsonify({'error': 'No data available'}), 404
        
        return send_file(file_path, as_attachment=True)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/download/processed')
def api_download_processed():
    """Download processed/cleaned data"""
    try:
        file_path = Config.DATA_PROCESSED_DIR / "car_auction_public.csv"
        if not file_path.exists():
            return jsonify({'error': 'Processed data not available'}), 404
        
        return send_file(file_path, as_attachment=True)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', 
                         error="Page Not Found",
                         message="The requested page does not exist."), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', 
                         error="Internal Server Error",
                         message="Something went wrong. Please try again later."), 500

# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    # Development server (matches production Gunicorn port)
    app.run(host='0.0.0.0', port=8000, debug=True)
