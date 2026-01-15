import numpy as np
import pandas as pd

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    # IMPORTANT: avoid SettingWithCopyWarning
    df = df.copy()

    # Safe denominator (avoid divide by zero)
    g = df["G"].replace(0, np.nan)

    # Per-game fantasy
    df["hPPR_per_g"] = df["hPPR"] / g
    df["total_td_per_g"] = df["Total TD"] / g

    # Passing
    df["pass_yds_per_g"] = df["Passing Yds"] / g
    df["pass_att_per_g"] = df["Passing Att"] / g
    df["pass_td_per_g"]  = df["Passing TD"] / g

    # Rushing
    df["rush_yds_per_g"] = df["Rushing Yds"] / g
    df["rush_att_per_g"] = df["Rushing Att"] / g
    df["rush_td_per_g"]  = df["Rushing TD"] / g

    # Receiving
    df["rec_yds_per_g"] = df["Receiving Yds"] / g
    df["rec_per_g"]     = df["Rec"] / g
    df["tgt_per_g"]     = df["Tgt"] / g
    df["rec_td_per_g"]  = df["Receiving TD"] / g

    # Replace inf from division by zero
    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    return df


def rolling_average(df: pd.DataFrame, windows=(2, 3)) -> pd.DataFrame:
    df = df.copy()
    df = df.sort_values(["Player", "Year"])

    rolling_features = [
        "hPPR_per_g",
        "pass_yds_per_g", "pass_att_per_g", "pass_td_per_g",
        "rush_yds_per_g", "rush_att_per_g", "rush_td_per_g",
        "rec_yds_per_g", "rec_per_g", "tgt_per_g", "rec_td_per_g",
    ]

    for feature in rolling_features:
        for w in windows:
            df[f"{feature}_roll{w}"] = (
                df.groupby("Player")[feature]
                  .transform(lambda x: x.shift(1).rolling(w, min_periods=1).mean())
            )

    return df