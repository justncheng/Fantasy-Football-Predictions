from pathlib import Path
import pandas as pd
import re

project_root = Path(__file__).resolve().parents[1]

data_dir = project_root / "NFL Fantasy Stats"   # folder containing all yearly CSVs
out_dir = project_root / "NFL Combined Fantasy Stats"
out_dir.mkdir(parents=True, exist_ok=True)   # make the folder if missing
out_path = out_dir / "NFL Fantasy Stats 2005-2024.csv"


files = sorted(data_dir.glob("*fantasy stats*.csv"))
if not files:
    raise FileNotFoundError(f"No files matched in {data_dir}")

dfs = []
for fp in files:
    # Read CSV; tweak options if you hit weird encodings
    df = pd.read_csv(fp, low_memory=False)

    dfs.append(df)

combined = pd.concat(dfs, ignore_index=True, sort=False)

# Optional: drop exact duplicates (use a subset of columns if you prefer)
combined = combined.drop_duplicates()

# Save at the project root (NOT in Scripts/)
combined.to_csv(out_path, index=False)
print(f"Combined {len(files)} files → {out_path}")