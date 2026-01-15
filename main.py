from pathlib import Path
import pandas as pd
from Features.feature_engineering import preprocess_data
from Features.feature_engineering import rolling_average

DATA_PATH = Path("NFL Combined Fantasy Stats") / "merged_fantasy_stats_2005_2024.csv"
OUT_PATH  = Path("data") / "processed" / "features_only.csv"

df = pd.read_csv(DATA_PATH)
df = preprocess_data(df)
df = rolling_average(df)

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(OUT_PATH, index=False)
print(f"Saved → {OUT_PATH}")