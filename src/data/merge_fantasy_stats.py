from pathlib import Path
import pandas as pd
import re

# Resolve project root correctly
project_root = Path(__file__).resolve().parents[2]

# Raw fantasy stats
data_dir = project_root / "NFL Fantasy Stats"

# Merged output
out_dir = project_root / "data" / "processed"
out_dir.mkdir(parents=True, exist_ok=True)

out_path = out_dir / "merged_fantasy_stats_2005_2024.csv"

# Find all relevant CSVs
files = sorted(data_dir.glob("*fantasy stats*.csv"))
if not files:
    raise FileNotFoundError(f"No files matched in {data_dir}")
dfs = []
for fp in files:
    # Read CSV; tweak options if you hit weird encodings
    df = pd.read_csv(fp, low_memory=False)

    dfs.append(df)

combined = pd.concat(dfs, ignore_index=True, sort=False)

combined = combined.drop_duplicates()

# Removed DKPt column
combined = combined.drop(columns=['DKPt'], errors='ignore')

combined.to_csv(out_path, index=False)
print(f"Combined {len(files)} files → {out_path}")