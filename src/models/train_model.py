from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score


INPUT_PATH = Path("data") / "2330_TW_features.csv"
MODEL_PATH = Path("models") / "stock_up_5d_model.pkl"

FEATURE_COLUMNS = [
    "daily_return",
    "ma_5",
    "ma_20",
    "ma_60",
    "volume_ma_5",
    "volume_ma_20",
    "volatility_20",
]
TARGET_COLUMN = "target_up_5d"


def train_model() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Feature file not found: {INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH)

    required_columns = set(FEATURE_COLUMNS + [TARGET_COLUMN])
    missing = required_columns.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    # Keep only required columns and drop NaN rows to ensure clean model input.
    model_df = df[FEATURE_COLUMNS + [TARGET_COLUMN]].dropna().copy()

    if model_df.empty:
        raise ValueError("No training rows left after dropping NaN values.")

    X = model_df[FEATURE_COLUMNS]
    y = model_df[TARGET_COLUMN].astype(int)

    # Time-series split: first 80% for training, last 20% for testing.
    split_idx = int(len(model_df) * 0.8)
    if split_idx <= 0 or split_idx >= len(model_df):
        raise ValueError("Not enough data points for 80/20 time-series split.")

    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print("=== Training Summary ===")
    print(f"Input file: {INPUT_PATH}")
    print(f"Total rows (before dropna): {len(df)}")
    print(f"Total rows (after dropna): {len(model_df)}")
    print(f"Train rows: {len(X_train)}")
    print(f"Test rows: {len(X_test)}")
    print(f"Model saved to: {MODEL_PATH}")

    print("\n=== Evaluation Metrics (Test Set) ===")
    print(f"accuracy: {acc:.4f}")
    print(f"precision: {prec:.4f}")
    print(f"recall: {rec:.4f}")
    print(f"F1 score: {f1:.4f}")
    print("confusion matrix:")
    print(cm)


if __name__ == "__main__":
    train_model()
