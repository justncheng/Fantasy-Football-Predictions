from pathlib import Path
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error
from sklearn.linear_model import Ridge
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from joblib import dump

"""
OUTPUT:

 model   val_MAE  test_MAE
        ridge 36.860573 38.773008
          hgb 36.886776 38.172230
baseline_hPPR 38.000321 39.340308
          mlp 45.712029 48.158688

Best model: ridge
Test Spearman (overall): 0.7364009670299284

Baseline: Current hPPR is the same as last year's hPPR
Ridge: Linear model with regularization (Linear Model)
Hist Gradient Boosting Regressor: Decision trees to sequentially correct errors (Tree)
MLP Regressor: MLP to sequentially correct errors (Neural Network)

"""


def spearman_rank_corr(a, b):
    # simple Spearman without scipy
    a = pd.Series(a).rank(method="average")
    b = pd.Series(b).rank(method="average")
    return a.corr(b)

def make_preprocessor(num_cols, cat_cols):
    return ColumnTransformer([
        ("num", Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("sc", StandardScaler()),
        ]), num_cols),
        ("cat", Pipeline([
            ("imp", SimpleImputer(strategy="most_frequent")),
            ("oh", OneHotEncoder(handle_unknown="ignore")),
        ]), cat_cols),
    ])

def main():
    project_root = Path(__file__).resolve().parents[2]
    data_path = project_root / "data" / "processed" / "modeling_table.csv"
    model_dir = project_root / "data" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(data_path, low_memory=False)

    TARGET = "y_next_hPPR"
    CAT_COLS = ["FantPos", "Tm"]
    EXCLUDE = {"Player", "player_id", "split", TARGET, "Year"}  # keep Year excluded for now

    # Keep only rows with labels for training/eval
    labeled = df[df[TARGET].notna()].copy()

    train = labeled[labeled["split"] == "train"]
    val   = labeled[labeled["split"] == "val"]
    test  = labeled[labeled["split"] == "test"]

    feature_cols = [c for c in df.columns if c not in EXCLUDE]
    num_cols = [c for c in feature_cols if c not in CAT_COLS]

    X_train, y_train = train[feature_cols], train[TARGET].values
    X_val, y_val     = val[feature_cols],   val[TARGET].values
    X_test, y_test   = test[feature_cols],  test[TARGET].values

    pre = make_preprocessor(num_cols, CAT_COLS)

    candidates = {
        "ridge": Ridge(alpha=5.0, random_state=0),
        "hgb": HistGradientBoostingRegressor(random_state=0),
        "mlp": MLPRegressor(
            hidden_layer_sizes=(128, 64),
            activation="relu",
            alpha=1e-4,
            learning_rate_init=1e-3,
            max_iter=250,
            random_state=0,
        ),
    }

    results = []

    # Baseline: predict next year = current year hPPR (if available as a feature column)
    if "hPPR" in X_val.columns:
        val_pred_base = X_val["hPPR"].values
        test_pred_base = X_test["hPPR"].values
        results.append(("baseline_hPPR", mean_absolute_error(y_val, val_pred_base),
                        mean_absolute_error(y_test, test_pred_base)))

    best_name, best_val_mae, best_pipe = None, float("inf"), None

    for name, model in candidates.items():
        pipe = Pipeline([("pre", pre), ("model", model)])
        pipe.fit(X_train, y_train)

        val_pred = pipe.predict(X_val)
        test_pred = pipe.predict(X_test)

        val_mae = mean_absolute_error(y_val, val_pred)
        test_mae = mean_absolute_error(y_test, test_pred)

        results.append((name, val_mae, test_mae))

        if val_mae < best_val_mae:
            best_val_mae = val_mae
            best_name = name
            best_pipe = pipe

    results_df = pd.DataFrame(results, columns=["model", "val_MAE", "test_MAE"]).sort_values("val_MAE")
    print(results_df.to_string(index=False))

    # Optional ranking evaluation (overall)
    # (Use best_pipe on test set)
    test_pred = best_pipe.predict(X_test)
    print("\nBest model:", best_name)
    print("Test Spearman (overall):", spearman_rank_corr(test_pred, y_test))

    # Retrain best on train+val, then save
    trainval = labeled[labeled["split"].isin(["train", "val"])]
    X_trainval = trainval[feature_cols]
    y_trainval = trainval[TARGET].values

    best_pipe.fit(X_trainval, y_trainval)

    out_path = model_dir / "best_model.joblib"
    dump(best_pipe, out_path)
    print(f"\nSaved best model → {out_path}")

if __name__ == "__main__":
    main()