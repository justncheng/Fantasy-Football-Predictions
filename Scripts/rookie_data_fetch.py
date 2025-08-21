from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import os
from datetime import datetime

def college_football_data(year):
    URL = f"https://www.pro-football-reference.com/years/{year}/draft.htm"
    html = urlopen(URL)
    soup = BeautifulSoup(html, features="html.parser")

    positions = ['QB', 'WR', 'RB', 'TE']

    # Extract headers dynamically from the table
    headers = [th.getText() for th in soup.find_all('tr')[1].find_all('th')]
    headers = headers[1:]  # Drop 'Rk'

    # Extract all rows that are not header rows
    rows = soup.find_all('tr', class_=lambda x: x != "thead")

    # Extract data from table rows
    player_stats = [[td.getText() for td in row.find_all('td')] for row in rows]
    player_stats = [row for row in player_stats if len(row) == len(headers)]  # Only keep valid rows

    # Create DataFrame with dynamic headers
    stats = pd.DataFrame(player_stats, columns=headers)

    # Replace empty strings with 0 (except OvRank if it exists)
    for col in stats.columns:
        if col != 'OvRank':
            stats[col] = stats[col].replace(r'^$', 0, regex=True)

    # Remove unwanted characters like * and +
    stats = stats.replace(r'[*+]', '', regex=True)

    # Add year column
    stats['Year'] = year

    # Drop empty columns
    stats = stats.drop(columns=[""], errors='ignore')

    # Keep only relevant positions
    if 'Pos' in stats.columns:
        stats = stats[stats['Pos'].isin(positions)]
        stats = stats.drop(columns=['AP1', 'PB', 'St', 'Solo', 'Int', 'Sk'], errors='ignore')

    # Final header names you want
    renamed_headers = [
        'Pick', 'Tm', 'Player', 'Pos', 'Age', 'To', 'wAV', 'DrAV', 'G',
        'Passing Cmp', 'Passing Att', 'Passing Yds', 'Passing TD',
        'Rushing Att', 'Rushing Yds', 'Rushing TD',
        'Rec', 'Receiving Yds', 'Receiving TD',
        'College/Univ', 'Year'
    ]

    # Only rename columns if the count matches
    if len(stats.columns) == len(renamed_headers):
        stats.columns = renamed_headers
    else:
        print(f"[!] Column mismatch for {year}: expected {len(renamed_headers)}, got {len(stats.columns)}")
        return pd.DataFrame()

    # If current year, only keep limited columns
    if datetime.now().year == year:
        stats = stats[['Pick', 'Tm', 'Player', 'Pos', 'Age', 'Year']]

    return stats


# Create output directory if needed
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
output_dir = os.path.join(project_root, 'NFL Rookie Stats')
os.makedirs(output_dir, exist_ok=True)

# Fetch data for each year
for year in range(2020, 2026):
    print(f"Fetching year {year}...")
    df = college_football_data(year)
    if not df.empty:
        filename = os.path.join(output_dir, f'{year} rookie stats.csv')
        df.to_csv(filename, index=False)
        print(f"Saved to {filename}")
    else:
        print(f"Skipped {year} due to column mismatch.")

print("Done")
