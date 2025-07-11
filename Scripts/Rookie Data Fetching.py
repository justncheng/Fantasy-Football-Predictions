from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import os
from datetime import datetime

def college_football_data(year):
    URL = "https://www.pro-football-reference.com/years/{}/draft.htm".format(year)
    html = urlopen(URL)
    soup = BeautifulSoup(html, features="html.parser")

    positions = ['QB', 'WR', 'RB', 'TE']

    headers = [th.getText() for th in soup.find_all('tr')[1].find_all('th')]  # Selecting the table headers
    headers = headers[1:]  # We don't want 'Rk' as a table header

    rows = soup.find_all('tr', class_=lambda
        table_rows: table_rows != "thead")  # Finding all table rows that are not 'thead'

    player_stats = [[td.getText() for td in rows[i].find_all('td')]  # Get the table data from each table data cell
                    for i in range(len(rows))]  # For each row
    player_stats = player_stats[2:]

    stats = pd.DataFrame(player_stats, columns=headers)

    for col in stats.columns:
        if col != 'OvRank':
            stats[col] = stats[col].replace(r'', 0, regex=True)  # Replace all empty stats with 0 except overall rank

    stats = stats.replace(r'[*+]', '', regex=True)  # Remove unwanted characters

    stats['Year'] = year  # Add a year column

    stats = stats.drop(columns=[""], errors='ignore')

    if 'Pos' in stats.columns:
        stats = stats[stats['Pos'].isin(positions)] # Removing all non-QB, WR, RB, TE from the rookie stats lists
        stats = stats.drop(columns=['AP1', 'PB', 'St', 'Solo', 'Int', 'Sk'], errors='ignore') # Dropping unnecessary columns

    if datetime.now().year == year:
        stats = stats[['Pick', 'Tm', 'Player', 'Pos', 'Age', 'Year']] # Keep only the players' pick #, team, name, position, age and year

    return stats


# Create directory if necessary
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
output_dir = os.path.join(project_root, 'NFL Rookie Stats')
os.makedirs(output_dir, exist_ok=True)

for year in range(2016, 2026):
    print(f"Fetching year {year}...")
    df = college_football_data(year)
    filename = os.path.join(output_dir, f'{year} rookie stats.csv')
    df.to_csv(filename, index=False)
    print(f"Saved to {filename}")

print("Done")