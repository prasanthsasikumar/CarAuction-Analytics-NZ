import os
import re
from datetime import datetime, timedelta

# Get all CSV files
files = [f for f in os.listdir('.') if f.startswith('car_data_') and f.endswith('.csv')]

# Extract dates
dates = []
pattern = re.compile(r'car_data_(\d{4}-\d{2}-\d{2})\.csv')

for f in files:
    match = pattern.match(f)
    if match:
        dates.append(datetime.strptime(match.group(1), '%Y-%m-%d'))

dates.sort()

print(f'Total CSV files: {len(dates)}')
print(f'Date range: {dates[0].strftime("%Y-%m-%d")} to {dates[-1].strftime("%Y-%m-%d")}')
print(f'Days covered: {len(dates)}')
print(f'Days in range: {(dates[-1] - dates[0]).days + 1}')

# Find missing days
missing = []
current = dates[0]
while current <= dates[-1]:
    if current not in dates:
        missing.append(current)
    current += timedelta(days=1)

print(f'\nMissing days: {len(missing)}')
print('\nList of missing dates:')
for d in missing:
    print(d.strftime('%Y-%m-%d'))
