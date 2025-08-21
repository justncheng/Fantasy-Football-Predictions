from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import os

def fantasy_player_csv(year):

    URL = "https://www.pro-football-reference.com/years/{}/fantasy.htm".format(year)
    html = urlopen(URL)
    soup = BeautifulSoup(html, features="html.parser")

    headers = [th.getText() for th in soup.find_all('tr')[1].find_all('th')]  # Selecting the table headers
    headers = headers[1:]  # We don't want 'Rk' as a table header

    rows = soup.find_all('tr', class_=lambda
        table_rows: table_rows != "thead")  # Finding all table rows that are not 'thead'
    player_stats = [[td.getText() for td in rows[i].find_all('td')]  # Get the table data from each table data cell
                    for i in range(len(rows))]  # For each row
    player_stats = player_stats[2:]

    # Define expected headers in order (based on actual site structure as of 2024)
    renamed_headers = [
        'Player', 'Tm', 'FantPos', 'Age', 'G', 'GS',
        'Passing Cmp', 'Passing Att', 'Passing Yds', 'Passing TD', 'Passing Int',
        'Rushing Att', 'Rushing Yds', 'Yards per Rushing Attempt', 'Rushing TD',
        'Tgt', 'Rec', 'Receiving Yds', 'Yards per Reception', 'Receiving TD',
        'Fmb', 'FL',
        'Total TD', '2PM', '2PP', 'FantPt', 'PPR', 'DKPt', 'FDPt', 'VBD', 'PosRank', 'OvRank'
    ]

    stats = pd.DataFrame(player_stats, columns=renamed_headers)

    for col in stats.columns:
        if col != 'OvRank':
            stats[col] = stats[col].replace(r'', 0, regex=True)  # Replace all empty stats with 0 except overall rank

    stats = stats.replace(r'[*+]', '', regex=True)  # Remove unwanted characters
    stats['Year'] = year  # Add a year column

    return stats

# Create directory if necessary
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
output_dir = os.path.join(project_root, 'NFL Fantasy Stats')
os.makedirs(output_dir, exist_ok=True)

for year in range(2005,2025):
    print(f"Fetching year {year}...")
    df = fantasy_player_csv(year)
    filename = os.path.join(output_dir, f'{year} fantasy stats.csv')
    df.to_csv(filename, index=False)
    print(f"Saved to {filename}")

print("Done")
