from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd


FEATURES_PATH = Path("data") / "2330_TW_features.csv"
MODEL_PATH = Path("models") / "stock_up_5d_model.pkl"
REPORT_PATH = Path("reports") / "backtest_2330_TW.csv"

FEATURE_COLUMNS = [
    "daily_return",
    "ma_5",
    "ma_20",
    "ma_60",
    "volume_ma_5",
    "volume_ma_20",
    "volatility_20",
]
TARGET_RETURN_COLUMN = "target_5d_return"


def _max_drawdown(returns: pd.Series) -> float:
    if returns.empty:
        return 0.0

    equity_curve = (1 + returns).cumprod()
    running_max = equity_curve.cummax()
    drawdown = (equity_curve - running_max) / running_max
    return float(drawdown.min())


def run_backtest() -> None:
    if not FEATURES_PATH.exists():
        raise FileNotFoundError(f"Feature file not found: {FEATURES_PATH}")
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

    df = pd.read_csv(FEATURES_PATH)

    required_columns = set(FEATURE_COLUMNS + [TARGET_RETURN_COLUMN])
    missing = required_columns.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    # Build a clean dataframe for backtesting (features + 5D forward return target).
    bt_df = df[FEATURE_COLUMNS + [TARGET_RETURN_COLUMN]].dropna().copy()
    if bt_df.empty:
        raise ValueError("No rows left for backtest after dropping NaN values.")

    # Time-series split: first 80% as training range, last 20% as backtest range.
    split_idx = int(len(bt_df) * 0.8)
    if split_idx <= 0 or split_idx >= len(bt_df):
        raise ValueError("Not enough data points for 80/20 time-series split.")

    backtest_df = bt_df.iloc[split_idx:].copy()

    model = joblib.load(MODEL_PATH)
    predictions = model.predict(backtest_df[FEATURE_COLUMNS])

    backtest_df["prediction"] = predictions.astype(int)
    backtest_df["trade_return"] = np.where(
        backtest_df["prediction"] == 1,
        backtest_df[TARGET_RETURN_COLUMN],
        0.0,
    )

    trades = backtest_df[backtest_df["prediction"] == 1]
    num_trades = int(len(trades))

    if num_trades == 0:
        avg_return = 0.0
        win_rate = 0.0
        strategy_cum_return = 0.0
        strategy_mdd = 0.0
        print("No trades generated in the backtest window.")
    else:
        avg_return = float(trades[TARGET_RETURN_COLUMN].mean())
        win_rate = float((trades[TARGET_RETURN_COLUMN] > 0).mean())
        strategy_cum_return = float((1 + trades[TARGET_RETURN_COLUMN]).prod() - 1)
        strategy_mdd = _max_drawdown(trades[TARGET_RETURN_COLUMN])

    # Buy & hold baseline on the same backtest period (5-day horizon compatible view).
    bh_returns = backtest_df[TARGET_RETURN_COLUMN]
    bh_cum_return = float((1 + bh_returns).prod() - 1)
    bh_mdd = _max_drawdown(bh_returns)
    bh_avg_return = float(bh_returns.mean())

    result = pd.DataFrame(
        [
            {
                "rows_in_backtest": len(backtest_df),
                "num_trades": num_trades,
                "avg_return": avg_return,
                "win_rate": win_rate,
                "cum_return": strategy_cum_return,
                "mdd": strategy_mdd,
                "buy_hold_avg_return": bh_avg_return,
                "buy_hold_cum_return": bh_cum_return,
                "buy_hold_mdd": bh_mdd,
            }
        ]
    )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(REPORT_PATH, index=False)

    print("=== Backtest Summary (2330.TW) ===")
    print(f"Backtest rows: {len(backtest_df)}")
    print(f"Number of trades: {num_trades}")
    print(f"Average return per trade: {avg_return:.4f}")
    print(f"Win rate: {win_rate:.2%}")
    print(f"Cumulative return: {strategy_cum_return:.2%}")
    print(f"Max drawdown (MDD): {strategy_mdd:.2%}")

    print("\n=== Buy & Hold (same backtest window) ===")
    print(f"Average 5D return: {bh_avg_return:.4f}")
    print(f"Cumulative return: {bh_cum_return:.2%}")
    print(f"Max drawdown (MDD): {bh_mdd:.2%}")

    print(f"\nSaved backtest report to: {REPORT_PATH}")


if __name__ == "__main__":
    run_backtest()
