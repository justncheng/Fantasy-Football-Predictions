from pathlib import Path
import numpy as np
import pandas as pd

from Features.feature_engineering import preprocess_data, rolling_average


def add_player_id(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["player_id"] = (
        df["Player"].astype(str).str.strip() + "|" +
        df["FantPos"].astype(str).str.strip()
    )
    return df


def add_lag_features(df: pd.DataFrame, lags=(1, 2)) -> pd.DataFrame:
    df = df.sort_values(["player_id", "Year"]).copy()

    lag_cols = [
        "hPPR",
        "G",
        "Tgt",
        "Rec",
        "Rushing Att",
        "Receiving Yds",
        "Rushing Yds",
        "Passing Yds",
        "Total TD",
    ]

    for col in lag_cols:
        if col not in df.columns:
            continue
        for k in lags:
            df[f"{col}_lag{k}"] = df.groupby("player_id")[col].shift(k)

    return df


def add_label_and_split(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["player_id", "Year"]).copy()

    # Label: predict next season
    df["y_next_hPPR"] = df.groupby("player_id")["hPPR"].shift(-1)

    # Fixed splits
    df["split"] = "ignore"
    df.loc[df["Year"].between(2005, 2018), "split"] = "train"
    df.loc[df["Year"].between(2019, 2021), "split"] = "val"
    df.loc[df["Year"].between(2022, 2023), "split"] = "test"
    df.loc[df["Year"] == 2024, "split"] = "predict"

    return df


def build_modeling_table(input_csv: Path) -> pd.DataFrame:
    df = pd.read_csv(input_csv, low_memory=False)

    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")

    # Core features
    df = preprocess_data(df)
    df = rolling_average(df)

    # IDs + lags + label + split
    df = add_player_id(df)
    df = add_lag_features(df)
    df = add_label_and_split(df)

    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    return df


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]

    input_path = (
        project_root
        / "data"
        / "processed"
        / "merged_fantasy_stats_2005_2024.csv"
    )

    out_path = project_root / "data" / "processed" / "modeling_table.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    df = build_modeling_table(input_path)
    df.to_csv(out_path, index=False)

    print(f"Saved modeling table → {out_path}")
    print("Rows:", len(df))
    print("Split counts:")
    print(df["split"].value_counts(dropna=False))