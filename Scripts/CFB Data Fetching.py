import os
import pandas as pd
from tqdm import tqdm
from cfbd import Configuration, ApiClient
from cfbd.api import PlayersApi, StatsApi
from cfbd.rest import ApiException
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

configuration = Configuration(access_token=os.environ["BEARER_TOKEN"])

# Get the root directory by going one level up from the script's location
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

# Input and output directories relative to the root
NFL_ROOKIE_STATS_DIR = os.path.join(ROOT_DIR, "NFL Rookie Stats")
CFB_STATS_OUTPUT_DIR = os.path.join(ROOT_DIR, "CFB Stats")

# Make sure the output folder exists
os.makedirs(CFB_STATS_OUTPUT_DIR, exist_ok=True)

with ApiClient(configuration) as api_client:
    players_api = PlayersApi(api_client)
    stats_api = StatsApi(api_client)

    # Go through each rookie year file
    for filename in sorted(os.listdir(NFL_ROOKIE_STATS_DIR)):
        if not filename.endswith(".csv"):
            continue

        rookie_year = int(filename[:4])
        df = pd.read_csv(os.path.join(NFL_ROOKIE_STATS_DIR, filename))

        print(f"\nProcessing rookies from {rookie_year}...")

        for _, row in tqdm(df.iterrows(), total=len(df), desc=f"{rookie_year} rookies"):
            name = row['Player']  # adjust this column name if needed

            try:
                players = players_api.get_players(search=name)
                if not players:
                    continue

                # Take first match (can be refined)
                player = players[0]

                if not player.seasons:
                    continue

                for season in player.seasons:
                    try:
                        stats = stats_api.get_player_season_stats(year=season, player_id=player.id)
                        if not stats:
                            continue

                        season_df = pd.DataFrame([s.to_dict() for s in stats])

                        # Append to per-year file
                        out_path = os.path.join(CFB_STATS_OUTPUT_DIR, f"{season} stats.csv")

                        if os.path.exists(out_path):
                            season_df.to_csv(out_path, mode='a', index=False, header=False)
                        else:
                            season_df.to_csv(out_path, index=False)

                    except ApiException as e:
                        print(f"Failed to fetch stats for {name} in {season}: {e}")

            except ApiException as e:
                print(f"API error searching for {name}: {e}")

