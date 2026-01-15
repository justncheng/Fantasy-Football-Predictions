import os
import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

BASE_URL = "https://www.sports-reference.com"
CFB_PLAYER_URL = BASE_URL + "/cfb/players/{}.html"
HEADERS = {"User-Agent": "Mozilla/5.0"}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))  # one level up

NFL_FOLDER = os.path.join(ROOT_DIR, "NFL Rookie Stats")
CFB_FOLDER = os.path.join(ROOT_DIR, "CFB Stats")
os.makedirs(CFB_FOLDER, exist_ok=True)

def normalize_name(name):
    return re.sub(r'\b(jr|sr|ii|iii|iv|v)\b\.?', '', name, flags=re.IGNORECASE).strip()

def slugify_player_name(name):
    name = normalize_name(name)
    name = name.lower().replace('.', '').replace("'", '').replace(' ', '-')
    return name

def get_player_url(slug, expected_college):
    for i in range(5):  # 0 to 4
        suffix = f"-{i}" if i > 0 else ""
        url = f"https://www.sports-reference.com/cfb/players/{slug}{suffix}.html"

        try:
            res = requests.get(url, headers=HEADERS)
            if res.status_code != 200:
                continue

            soup = BeautifulSoup(res.text, "html.parser")

            # Sometimes team info is in the first row of the first table
            team_tag = soup.find("table")
            if not team_tag:
                # Try inside comments if table is hidden
                from bs4 import Comment
                for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                    comment_soup = BeautifulSoup(comment, "html.parser")
                    team_tag = comment_soup.find("table")
                    if team_tag:
                        break

            if not team_tag:
                continue

            first_team = None
            for row in team_tag.find_all("tr"):
                th = row.find("th")
                if th and th.get("data-stat") == "year_id":
                    td = row.find("td", {"data-stat": "school_name"})
                    if td:
                        first_team = td.text.strip()
                        break

            if not first_team:
                continue

            # Compare team from table with expected_college (case-insensitive, ignore punctuation)
            clean = lambda s: re.sub(r'[^a-zA-Z]', '', s).lower()
            if clean(first_team) == clean(expected_college):
                print(f"[✓] Matched college for {slug}{suffix} → {url}")
                return url
            else:
                print(f"[~] Tried {slug}{suffix}, but team '{first_team}' ≠ expected '{expected_college}'")

        except Exception as e:
            print(f"[!] Error while trying {url}: {e}")

        time.sleep(0.5)

    print(f"[X] No matching college found for {slug}")
    return None

def parse_table(table, prefix):
    data = {}
    headers = [th.text.strip() for th in table.thead.find_all("th")]
    for row in table.tbody.find_all("tr"):
        if row.get("class") and "thead" in row["class"]:
            continue
        season = row.find("th").text.strip()
        cells = [td.text.strip() for td in row.find_all("td")]
        if len(cells) != len(headers) - 1:
            continue
        season_data = {f"{prefix}{col}": val for col, val in zip(headers[1:], cells)}
        data[season] = season_data
    return data

from bs4 import BeautifulSoup, Comment

def scrape_combined_stats(player_name, draft_year, college):
    slug = slugify_player_name(player_name)
    url = get_player_url(slug, college)
    if not url:
        print(f"[!] Could not find stats for {player_name}")
        return []

    print(f"[+] Scraping {player_name} from {url}")
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    # Look for tables directly first
    pass_table = soup.find("table", id="passing")
    rush_recv_table = soup.find("table", id="rushing_and_receiving")

    # If not found, try extracting from HTML comments
    if not pass_table or not rush_recv_table:
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment_soup = BeautifulSoup(comment, "html.parser")
            if not pass_table:
                pass_table = comment_soup.find("table", id="passing")
            if not rush_recv_table:
                rush_recv_table = comment_soup.find("table", id="rushing_and_receiving")
            if pass_table and rush_recv_table:
                break

    # Parse both tables
    pass_data = parse_table(pass_table, "Pass_") if pass_table else {}
    rush_data = parse_table(rush_recv_table, "Rush_") if rush_recv_table else {}

    all_seasons = set(pass_data.keys()).union(rush_data.keys())
    results = []

    for season in all_seasons:
        row = {
            "Player": player_name,
            "Draft Year": draft_year,
            "Season": season,
            "College": college
        }
        if season in pass_data:
            row.update(pass_data[season])
        if season in rush_data:
            row.update(rush_data[season])
        results.append(row)

    return results


def append_to_season_csv(stats):
    for row in stats:
        season_year = row["Season"]
        path = os.path.join(CFB_FOLDER, f"{season_year}.csv")
        df = pd.DataFrame([row])
        if os.path.exists(path):
            existing_df = pd.read_csv(path)
            df = pd.concat([existing_df, df], ignore_index=True)
        df.to_csv(path, index=False)

def process_rookie_file(path):
    df = pd.read_csv(path)
    for _, row in df.iterrows():
        player_name = row["Player"]
        college = row["College/Univ"]
        draft_year = row["Year"]
        stats = scrape_combined_stats(player_name, draft_year, college)
        if stats:
            append_to_season_csv(stats)
        time.sleep(1)

def main():
    for file in os.listdir(NFL_FOLDER):
        if file.endswith(".csv"):
            print(f"Processing: {file}")
            process_rookie_file(os.path.join(NFL_FOLDER, file))

if __name__ == "__main__":
    main()
