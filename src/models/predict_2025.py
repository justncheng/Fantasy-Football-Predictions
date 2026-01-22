from pathlib import Path
import pandas as pd
from joblib import load

def main():
    project_root = Path(__file__).resolve().parents[2]
    data_path = project_root / "data" / "processed" / "modeling_table.csv"
    model_path = project_root / "data" / "models" / "best_model.joblib"
    out_path = project_root / "data" / "processed" / "predicted_2025_rankings.csv"

    df = pd.read_csv(data_path, low_memory=False)
    model = load(model_path)

    TARGET = "y_next_hPPR"
    CAT_COLS = ["FantPos", "Tm"]
    EXCLUDE = {"Player", "player_id", "split", TARGET, "Year"}  # must match training!

    # Use 2024 rows (split == predict) to predict 2025
    pred_df = df[df["split"] == "predict"].copy()

    # Build feature columns exactly like training did
    feature_cols = [c for c in df.columns if c not in EXCLUDE]

    # Predict 2025 points
    pred_df["predicted_2025_hPPR"] = model.predict(pred_df[feature_cols])

    # Overall rank (all positions)
    pred_df = pred_df.sort_values("predicted_2025_hPPR", ascending=False)
    pred_df["pred_ov_rank"] = range(1, len(pred_df) + 1)

    # Position rank (QB/RB/WR/TE separately)
    pred_df["pred_pos_rank"] = (
        pred_df.groupby("FantPos")["predicted_2025_hPPR"]
               .rank(ascending=False, method="first")
               .astype(int)
    )

    # Keep useful columns
    cols = [
        "pred_ov_rank", "pred_pos_rank",
        "Player", "FantPos", "Tm", "Age", "Year",
        "predicted_2025_hPPR"
    ]
    cols = [c for c in cols if c in pred_df.columns]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    pred_df[cols].to_csv(out_path, index=False)

    print(f"Saved 2025 rankings → {out_path}")

    # Optional: print top 20 overall
    print("\nTop 20 Overall (Predicted 2025):")
    print(pred_df[cols].head(20).to_string(index=False))

if __name__ == "__main__":
    main()