# import requests
# from bs4 import BeautifulSoup
# import pandas as pd
# from datetime import datetime
# import time
# import os

# # List of months
# months = [
#     'january', 'february', 'march', 'april', 'may', 'june',
#     'july', 'august', 'september', 'october', 'november', 'december'
# ]

# # Base URL
# base_url = 'https://weatherandclimate.com/namibia/oshikoto/okaukuejo/'
# year = 2012

# # Save directory
# save_dir = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\climatedata'
# # Ensure the directory exists
# os.makedirs(save_dir, exist_ok=True)

# # Function to extract daily data from a single page
# def extract_daily_data(url):
#     response = requests.get(url)
#     if response.status_code != 200:
#         print(f"Failed to fetch {url}")
#         return []
    
#     soup = BeautifulSoup(response.content, 'html.parser')
#     tables = soup.find_all('table')
    
#     daily_data = []
#     for table in tables:
#         rows = table.find_all('tr')
#         if len(rows) < 2:
#             continue
        
#         # Check if this table has date-like entries (e.g., 2011-MM-DD)
#         has_date = False
#         for row in rows[1:3]:  # Check first couple of data rows
#             cells = row.find_all(['td', 'th'])
#             for cell in cells:
#                 text = cell.get_text(strip=True)
#                 if '-' in text and len(text) == 10 and text[:4] == str(year):
#                     has_date = True
#                     break
#             if has_date:
#                 break
#         if not has_date:
#             continue
        
#         # Parse headers - expect complex header with units
#         header_row1 = rows[0].find_all(['th', 'td'])
#         header_row2 = rows[1].find_all(['th', 'td']) if len(rows) > 1 else []
        
#         # Build full header list
#         headers = []
#         i = 0
#         while i < len(header_row1):
#             h1 = header_row1[i].get_text(strip=True)
#             if i < len(header_row2):
#                 h2 = header_row2[i].get_text(strip=True)
#                 headers.append(f"{h1} {h2}".strip())
#             else:
#                 headers.append(h1)
#             i += 1
        
#         # Parse data rows starting from row 2 (after headers)
#         for row in rows[2:]:
#             cells = row.find_all(['td', 'th'])
#             if len(cells) != len(headers):
#                 continue
#             row_data = [cell.get_text(strip=True) for cell in cells]
#             # Insert month/year if date is partial, but since it's full date, ok
#             daily_data.append(row_data)
        
#         break  # Assume first matching table is the daily one
    
#     return daily_data

# # Collect all data
# all_data = []
# for month in months:
#     url = f"{base_url}{month}-{year}"
#     print(f"Fetching {month} {year}...")
#     month_data = extract_daily_data(url)
#     if month_data:
#         # Prepend month name if needed, but date has it
#         all_data.extend(month_data)
#     else:
#         print(f"No data for {month}")
#     time.sleep(1)  # Be polite to the server

# # Create DataFrame
# if all_data:
#     # Use first row as headers if not already
#     headers = all_data[0] if all_data else []
#     df = pd.DataFrame(all_data[1:], columns=headers)
    
#     # Clean up column names if needed (from the examples)
#     # Adjust based on actual: e.g., split Temperature into °C and °F
#     # From examples, columns are already split like 'Temperature °C', etc.
    
#     # Save to specified directory
#     save_path = os.path.join(save_dir, 'okaukuejo_weather_2012.csv')
#     df.to_csv(save_path, index=False)
#     print(f"Data saved to {save_path}")
    
#     # Display summary
#     print(df.head())
# else:
#     print("No data retrieved.")

# Note: You may need to install dependencies: pip install requests beautifulsoup4 pandas

# import requests
# from bs4 import BeautifulSoup
# import pandas as pd
# from datetime import datetime
# import time
# import os
# import random
# import re  # For potential advanced splitting if needed

# # List of months
# months = [
#     'january', 'february', 'march', 'april', 'may', 'june',
#     'july', 'august', 'september', 'october', 'november', 'december'
# ]

# # Base URL
# base_url = 'https://weatherandclimate.com/namibia/oshikoto/okaukuejo/'

# # Fixed column names for the daily data table
# columns = [
#     'Date',
#     'Temp_C',
#     'Temp_F',
#     'Dew_C',
#     'Dew_F',
#     'Humidity_%',
#     'Wind_Kph',
#     'Wind_Mph',
#     'Press_Hg',
#     'Press_Mb',
#     'Precip_mm',
#     'Precip_in'
# ]

# # Save directory
# save_dir = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\climatedata'
# # Ensure the directory exists
# os.makedirs(save_dir, exist_ok=True)

# # Updated headers to better mimic a modern browser
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
#     'Accept-Language': 'en-US,en;q=0.9',
#     'Accept-Encoding': 'gzip, deflate, br',
#     'DNT': '1',
#     'Connection': 'keep-alive',
#     'Upgrade-Insecure-Requests': '1',
#     'Sec-Fetch-Dest': 'document',
#     'Sec-Fetch-Mode': 'navigate',
#     'Sec-Fetch-Site': 'none',
#     'Sec-Fetch-User': '?1',
#     'Cache-Control': 'max-age=0'
# }

# # Create a session to persist cookies and connections
# session = requests.Session()
# session.headers.update(headers)

# # Function to extract daily data from a single page (with added debugging and handling for 7-column format)
# def extract_daily_data(url, session):
#     try:
#         response = session.get(url, timeout=10)
#         print(f"    Status code for {url}: {response.status_code}")
        
#         if response.status_code != 200:
#             print(f"    Failed to fetch {url} (status: {response.status_code})")
#             if response.status_code in [403, 429]:
#                 print("    Possible rate limiting or blocking. Consider increasing delays.")
#             return []
        
#         soup = BeautifulSoup(response.content, 'html.parser')
#         tables = soup.find_all('table')
#         print(f"    Number of tables found: {len(tables)}")
        
#         raw_daily_data = []
#         found_table = False
#         for i, table in enumerate(tables):
#             rows = table.find_all('tr')
#             if len(rows) < 3:  # Need at least headers + one data row
#                 continue
            
#             # Check if this table has date-like entries (e.g., YYYY-MM-DD)
#             has_date = False
#             year_from_url = url.split('-')[-1]
#             print(f"    Checking table {i+1} for dates starting with {year_from_url}...")
#             for row in rows[2:4]:  # Check first couple of data rows (skip headers)
#                 cells = row.find_all(['td', 'th'])
#                 for cell in cells:
#                     text = cell.get_text(strip=True)
#                     if '-' in text and len(text) == 10 and text.startswith(year_from_url):
#                         has_date = True
#                         print(f"    Date found in table {i+1}: {text}")
#                         break
#                 if has_date:
#                     break
#             if not has_date:
#                 print(f"    No matching dates in table {i+1}")
#                 continue
            
#             print(f"    Processing daily data from table {i+1}...")
#             # Parse data rows starting from row 2 (after two header rows)
#             for row_idx, row in enumerate(rows[2:], start=1):
#                 cells = row.find_all(['td', 'th'])
#                 row_len = len(cells)
#                 row_texts = [cell.get_text(strip=True) for cell in cells]
                
#                 if row_len not in (7, 11, 12):
#                     print(f"    Skipping row {row_idx} (len: {row_len}), sample: {row_texts[:2]}...")  # Debug: show sample
#                     continue
                
#                 processed_row = None
#                 if row_len == 12:
#                     # Already separate columns
#                     processed_row = row_texts
#                 elif row_len == 11:
#                     # Precip combined in last cell
#                     precip_text = row_texts[10]
#                     precip_parts = precip_text.split(' | ')
#                     precip_mm = precip_parts[0].strip() if precip_parts else ''
#                     precip_in = precip_parts[1].strip() if len(precip_parts) > 1 else ''
#                     processed_row = row_texts[:10] + [precip_mm, precip_in]
#                 elif row_len == 7:
#                     # Combined format: split paired values by ' | '
#                     # Assuming order: [Date, Temp(C|F), Dew(C|F), Hum, Wind(Kph|Mph), Press(Hg|Mb), Precip(mm|in)]
#                     try:
#                         date = row_texts[0]
#                         temp_parts = row_texts[1].split(' | ')
#                         temp_c = temp_parts[0].strip() if temp_parts else ''
#                         temp_f = temp_parts[1].strip() if len(temp_parts) > 1 else ''
                        
#                         dew_parts = row_texts[2].split(' | ')
#                         dew_c = dew_parts[0].strip() if dew_parts else ''
#                         dew_f = dew_parts[1].strip() if len(dew_parts) > 1 else ''
                        
#                         hum = row_texts[3]
                        
#                         wind_parts = row_texts[4].split(' | ')
#                         wind_kph = wind_parts[0].strip() if wind_parts else ''
#                         wind_mph = wind_parts[1].strip() if len(wind_parts) > 1 else ''
                        
#                         press_parts = row_texts[5].split(' | ')
#                         press_hg = press_parts[0].strip() if press_parts else ''  # Assuming first is Hg (smaller number)
#                         press_mb = press_parts[1].strip() if len(press_parts) > 1 else ''
                        
#                         precip_parts = row_texts[6].split(' | ')
#                         precip_mm = precip_parts[0].strip() if precip_parts else ''
#                         precip_in = precip_parts[1].strip() if len(precip_parts) > 1 else ''
                        
#                         processed_row = [
#                             date, temp_c, temp_f, dew_c, dew_f, hum,
#                             wind_kph, wind_mph, press_hg, press_mb, precip_mm, precip_in
#                         ]
                        
#                         # Debug: print first few processed for verification
#                         if len(raw_daily_data) < 2:
#                             print(f"    Sample processed row {len(raw_daily_data)+1}: {processed_row[:3]}...")
#                     except Exception as e:
#                         print(f"    Error processing 7-col row {row_idx}: {e}, raw: {row_texts}")
#                         continue
                
#                 if processed_row:
#                     raw_daily_data.append(processed_row)
#                     if len(raw_daily_data) <= 2:  # Print first couple for verification
#                         print(f"    Sample row {len(raw_daily_data)}: {processed_row[:2]}...")  # Truncated for brevity
            
#             found_table = True
#             break  # Assume first matching table is the daily one
        
#         if not found_table:
#             print("    No suitable daily data table found.")
        
#         print(f"    Retrieved {len(raw_daily_data)} rows total")
#         return raw_daily_data
    
#     except requests.exceptions.RequestException as e:
#         print(f"    Request error for {url}: {e}")
#         return []
#     except Exception as e:
#         print(f"    Unexpected error for {url}: {e}")
#         return []

# # Years to fetch
# years = [2010, 2011, 2012, 2013]

# for year in years:
#     print(f"\nFetching data for {year}...")
#     all_data = []
#     for month in months:
#         url = f"{base_url}{month}-{year}"
#         print(f"  Fetching {month} {year}...")
#         month_data = extract_daily_data(url, session)
#         if month_data:
#             all_data.extend(month_data)
#             print(f"    Retrieved {len(month_data)} days")
#         else:
#             print(f"    No data for {month}")
        
#         # Random delay between 3-7 seconds to avoid rate limiting
#         delay = random.uniform(3, 7)
#         print(f"    Sleeping for {delay:.1f} seconds...")
#         time.sleep(delay)
    
#     # Create DataFrame for this year
#     if all_data:
#         df = pd.DataFrame(all_data, columns=columns)
        
#         # Save to specified directory
#         save_path = os.path.join(save_dir, f'okaukuejo_weather_{year}.csv')
#         df.to_csv(save_path, index=False)
#         print(f"Data for {year} ({len(df)} rows) saved to {save_path}")
        
#         # Display summary
#         print(df.head())
#     else:
#         print(f"No data retrieved for {year}.")

# print("\nAll data fetching completed.")

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import os
import random
import re  # For potential advanced splitting if needed

# List of months
months = [
    'january', 'february', 'march', 'april', 'may', 'june',
    'july', 'august', 'september', 'october', 'november', 'december'
]

# Base URL
# base_url = 'https://weatherandclimate.com/namibia/oshikoto/okaukuejo/'
base_url = 'https://weatherandclimate.com/namibia/oshikoto/halali/'

# Fixed column names for the daily data table (with Year added)
columns = [
    'Year',
    'Date',
    'Temp_C',
    'Temp_F',
    'Dew_C',
    'Dew_F',
    'Humidity_%',
    'Wind_Kph',
    'Wind_Mph',
    'Press_Hg',
    'Press_Mb',
    'Precip_mm',
    'Precip_in'
]

# Save directory
save_dir = r'G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\climatedata\Halali'
# Ensure the directory exists
os.makedirs(save_dir, exist_ok=True)

# Updated headers to better mimic a modern browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0'
}

# Create a session to persist cookies and connections
session = requests.Session()
session.headers.update(headers)

# Function to extract daily data from a single page (with added debugging and handling for 7-column format)
def extract_daily_data(url, session, year):
    try:
        response = session.get(url, timeout=10)
        print(f"    Status code for {url}: {response.status_code}")
        
        if response.status_code != 200:
            print(f"    Failed to fetch {url} (status: {response.status_code})")
            if response.status_code in [403, 429]:
                print("    Possible rate limiting or blocking. Consider increasing delays.")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        tables = soup.find_all('table')
        print(f"    Number of tables found: {len(tables)}")
        
        raw_daily_data = []
        found_table = False
        for i, table in enumerate(tables):
            rows = table.find_all('tr')
            if len(rows) < 3:  # Need at least headers + one data row
                continue
            
            # Check if this table has date-like entries (e.g., YYYY-MM-DD)
            has_date = False
            year_from_url = url.split('-')[-1]
            print(f"    Checking table {i+1} for dates starting with {year_from_url}...")
            for row in rows[2:4]:  # Check first couple of data rows (skip headers)
                cells = row.find_all(['td', 'th'])
                for cell in cells:
                    text = cell.get_text(strip=True)
                    if '-' in text and len(text) == 10 and text.startswith(year_from_url):
                        has_date = True
                        print(f"    Date found in table {i+1}: {text}")
                        break
                if has_date:
                    break
            if not has_date:
                print(f"    No matching dates in table {i+1}")
                continue
            
            print(f"    Processing daily data from table {i+1}...")
            # Parse data rows starting from row 2 (after two header rows)
            for row_idx, row in enumerate(rows[2:], start=1):
                cells = row.find_all(['td', 'th'])
                row_len = len(cells)
                row_texts = [cell.get_text(strip=True) for cell in cells]
                
                if row_len not in (7, 11, 12):
                    print(f"    Skipping row {row_idx} (len: {row_len}), sample: {row_texts[:2]}...")  # Debug: show sample
                    continue
                
                processed_row = None
                if row_len == 12:
                    # Already separate columns
                    processed_row = [str(year)] + row_texts
                elif row_len == 11:
                    # Precip combined in last cell
                    precip_text = row_texts[10]
                    precip_parts = precip_text.split(' | ')
                    precip_mm = precip_parts[0].strip() if precip_parts else ''
                    precip_in = precip_parts[1].strip() if len(precip_parts) > 1 else ''
                    processed_row = [str(year)] + row_texts[:10] + [precip_mm, precip_in]
                elif row_len == 7:
                    # Combined format: split paired values by ' | '
                    # Assuming order: [Date, Temp(C|F), Dew(C|F), Hum, Wind(Kph|Mph), Press(Hg|Mb), Precip(mm|in)]
                    try:
                        date = row_texts[0]
                        temp_parts = row_texts[1].split(' | ')
                        temp_c = temp_parts[0].strip() if temp_parts else ''
                        temp_f = temp_parts[1].strip() if len(temp_parts) > 1 else ''
                        
                        dew_parts = row_texts[2].split(' | ')
                        dew_c = dew_parts[0].strip() if dew_parts else ''
                        dew_f = dew_parts[1].strip() if len(dew_parts) > 1 else ''
                        
                        hum = row_texts[3]
                        
                        wind_parts = row_texts[4].split(' | ')
                        wind_kph = wind_parts[0].strip() if wind_parts else ''
                        wind_mph = wind_parts[1].strip() if len(wind_parts) > 1 else ''
                        
                        press_parts = row_texts[5].split(' | ')
                        press_hg = press_parts[0].strip() if press_parts else ''  # Assuming first is Hg (smaller number)
                        press_mb = press_parts[1].strip() if len(press_parts) > 1 else ''
                        
                        precip_parts = row_texts[6].split(' | ')
                        precip_mm = precip_parts[0].strip() if precip_parts else ''
                        precip_in = precip_parts[1].strip() if len(precip_parts) > 1 else ''
                        
                        processed_row = [
                            str(year), date, temp_c, temp_f, dew_c, dew_f, hum,
                            wind_kph, wind_mph, press_hg, press_mb, precip_mm, precip_in
                        ]
                        
                        # Debug: print first few processed for verification
                        if len(raw_daily_data) < 2:
                            print(f"    Sample processed row {len(raw_daily_data)+1}: {processed_row[:3]}...")
                    except Exception as e:
                        print(f"    Error processing 7-col row {row_idx}: {e}, raw: {row_texts}")
                        continue
                
                if processed_row:
                    raw_daily_data.append(processed_row)
                    if len(raw_daily_data) <= 2:  # Print first couple for verification
                        print(f"    Sample row {len(raw_daily_data)}: {processed_row[:2]}...")  # Truncated for brevity
            
            found_table = True
            break  # Assume first matching table is the daily one
        
        if not found_table:
            print("    No suitable daily data table found.")
        
        print(f"    Retrieved {len(raw_daily_data)} rows total")
        return raw_daily_data
    
    except requests.exceptions.RequestException as e:
        print(f"    Request error for {url}: {e}")
        return []
    except Exception as e:
        print(f"    Unexpected error for {url}: {e}")
        return []

# Years to fetch
years = [2010, 2011, 2012, 2013, 2014]

all_years_data = []  # Collect all data across years

for year in years:
    print(f"\nFetching data for {year}...")
    year_data = []
    for month in months:
        url = f"{base_url}{month}-{year}"
        print(f"  Fetching {month} {year}...")
        month_data = extract_daily_data(url, session, year)  # Pass year for column
        if month_data:
            year_data.extend(month_data)
            print(f"    Retrieved {len(month_data)} days")
        else:
            print(f"    No data for {month}")
        
        # Random delay between 3-7 seconds to avoid rate limiting
        delay = random.uniform(3, 7)
        print(f"    Sleeping for {delay:.1f} seconds...")
        time.sleep(delay)
    
    # Optional: Save yearly CSV as before
    if year_data:
        yearly_df = pd.DataFrame(year_data, columns=columns)
        save_path_yearly = os.path.join(save_dir, f'halali_weather_{year}.csv')
        yearly_df.to_csv(save_path_yearly, index=False)
        print(f"Yearly data for {year} ({len(yearly_df)} rows) saved to {save_path_yearly}")
        print(yearly_df.head())
        
        # Add to all years
        all_years_data.extend(year_data)
    else:
        print(f"No data retrieved for {year}.")

# Combine all years into one CSV with Year column
if all_years_data:
    combined_df = pd.DataFrame(all_years_data, columns=columns)
    
    # Save to specified directory
    combined_save_path = os.path.join(save_dir, 'halali_weather_all_years.csv')
    combined_df.to_csv(combined_save_path, index=False)
    print(f"\nCombined data for all years ({len(combined_df)} rows) saved to {combined_save_path}")
    
    # Display summary of combined
    print(combined_df.head())
    print(f"\nRows per year in combined file:")
    print(combined_df['Year'].value_counts().sort_index())
else:
    print("No data retrieved overall.")

print("\nAll data fetching completed.")