from flask import Flask, render_template
import pandas as pd
import datetime
import os

def get_file_name():
    # Get today's date
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    # Create the filename with today's date
    today_filename = f"car_data_{today}.csv"
    yesterday_filename = f"car_data_{yesterday}.csv"
    filename_to_use = today_filename
    # Check if today's file exists
    if not os.path.exists(today_filename):
        if os.path.exists(yesterday_filename):
            filename_to_use = yesterday_filename
            print("Using yesterdays file.")
        else:
            # Yesterday's file also doesn't exist
            print(f"Yesterday's file not found: {yesterday_filename}")
            print("No file available.")
    return filename_to_use

app = Flask(__name__)

@app.route('/')
def display_table():
    # Read the CSV file
    file = get_file_name()
    print(f"Reading file: {file}")
    data = pd.read_csv(file)
    
    # Filter rows based on the "Registration Status" column
    #filtered_data = data[data['Registration Status'] == 'yes']
    
    # Convert the filtered data to HTML table
    table_html = data.to_html(index=False)
    
    # Render the template with the table data
    return render_template('table.html', table=table_html)

if __name__ == '__main__':
    app.run()
