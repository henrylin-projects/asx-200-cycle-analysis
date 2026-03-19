# ASX 200 historical peak cycle analysis
# Runs drawdown thresholds from -5% to -50% in 1% steps
# Creates:
# 1) 46-panel scatter chart: X = cycle day periods, Y = frequency
# 2) Summary scatter chart: X = percentage decrease, Y = number of complete cycles
# 3) CSV exports for summary stats and detailed cycles

import os
from math import ceil
from datetime import datetime

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt


# =========================
# Settings
# =========================
TICKER = "^AXJO"
START_DATE = "2010-01-01"
END_DATE = datetime.today().strftime("%Y-%m-%d")
OUTPUT_DIR = "output_asx_cycles"

# Thresholds: -5%, -6%, ..., -50%
THRESHOLDS = list(range(5, 51))


# =========================
# Helpers
# =========================
def download_close_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Download price data and return a DataFrame with one column: 'close'
    Handles normal and MultiIndex yfinance outputs.
    """
    data = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        progress=False,
        auto_adjust=False
    )

    if data.empty:
        raise ValueError("No data downloaded from yfinance.")

    # Case 1: MultiIndex columns
    if isinstance(data.columns, pd.MultiIndex):
        if "Close" in data.columns.get_level_values(0):
            close_block = data.xs("Close", axis=1, level=0)
            if isinstance(close_block, pd.Series):
                close_series = close_block
            else:
                close_series = close_block.iloc[:, 0]
        else:
            raise ValueError("Could not find 'Close' in MultiIndex columns.")

    # Case 2: Standard columns
    else:
        if "Close" not in data.columns:
            raise ValueError("Could not find 'Close' column in downloaded data.")
        close_block = data["Close"]
        if isinstance(close_block, pd.DataFrame):
            close_series = close_block.iloc[:, 0]
        else:
            close_series = close_block

    close_series = pd.to_numeric(close_series, errors="coerce").dropna()

    df = pd.DataFrame({"close": close_series})
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    return df


def build_ath_table(df: pd.DataFrame):
    """
    Add ATH columns and return df plus ath_df (all new ATH dates).
    """
    df = df.copy()
    df["ath"] = df["close"].cummax()
    df["is_new_ath"] = df["close"] == df["ath"]

    ath_df = df[df["is_new_ath"]].copy().reset_index()
    date_col = ath_df.columns[0]  # usually 'Date', but robust if unnamed

    return df, ath_df, date_col


def analyze_threshold(df: pd.DataFrame, ath_df: pd.DataFrame, date_col: str, threshold_pct: int):
    """
    For a given threshold like 5, 10, 15...
    define a qualifying cycle as:
    start ATH -> at least threshold drawdown -> next new ATH
    """
    drop_decimal = threshold_pct / 100.0

    cycles_days = []
    cycle_starts = []
    cycle_ends = []
    detailed_rows = []

    for i in range(1, len(ath_df)):
        start_date = ath_df[date_col].iloc[i - 1]
        end_date = ath_df[date_col].iloc[i]
        start_peak = float(ath_df["close"].iloc[i - 1])

        period = df.loc[start_date:end_date].copy()
        min_price_in_period = float(period["close"].min())

        # Example:
        # threshold_pct = 7 means min price <= 93% of peak
        if min_price_in_period <= start_peak * (1 - drop_decimal):
            days = (end_date - start_date).days
            drawdown_pct = (min_price_in_period / start_peak - 1) * 100

            cycles_days.append(days)
            cycle_starts.append(start_date.strftime("%Y-%m-%d"))
            cycle_ends.append(end_date.strftime("%Y-%m-%d"))

            detailed_rows.append({
                "threshold_pct": -threshold_pct,
                "cycle_start_ath": start_date.strftime("%Y-%m-%d"),
                "cycle_end_ath": end_date.strftime("%Y-%m-%d"),
                "cycle_days": days,
                "start_peak_close": start_peak,
                "min_close_in_period": min_price_in_period,
                "actual_min_drawdown_pct": round(drawdown_pct, 2),
            })

    if cycles_days:
        summary = {
            "threshold_pct": -threshold_pct,
            "num_cycles": len(cycles_days),
            "average_cycle_days": round(sum(cycles_days) / len(cycles_days), 2),
            "min_cycle_days": min(cycles_days),
            "max_cycle_days": max(cycles_days),
            "median_cycle_days": round(pd.Series(cycles_days).median(), 2),
        }
    else:
        summary = {
            "threshold_pct": -threshold_pct,
            "num_cycles": 0,
            "average_cycle_days": None,
            "min_cycle_days": None,
            "max_cycle_days": None,
            "median_cycle_days": None,
        }

    return {
        "threshold_pct": threshold_pct,
        "threshold_label": f"-{threshold_pct}%",
        "cycles_days": cycles_days,
        "cycle_starts": cycle_starts,
        "cycle_ends": cycle_ends,
        "detailed_rows": detailed_rows,
        "summary": summary,
    }


def create_panel_scatter(results, output_path):
    """
    Create one multi-panel figure with 46 scatter plots.
    X axis = day periods
    Y axis = frequency
    """
    n = len(results)
    ncols = 6
    nrows = ceil(n / ncols)

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(24, 30))
    axes = axes.flatten()

    for idx, result in enumerate(results):
        ax = axes[idx]
        cycles_days = result["cycles_days"]
        threshold_label = result["threshold_label"]

        if cycles_days:
            freq = pd.Series(cycles_days).value_counts().sort_index()
            ax.scatter(freq.index, freq.values, s=25)
            ax.text(
                0.98, 0.95,
                f"n={len(cycles_days)}",
                transform=ax.transAxes,
                ha="right", va="top", fontsize=8
            )
        else:
            ax.text(
                0.5, 0.5,
                "No cycles",
                transform=ax.transAxes,
                ha="center", va="center", fontsize=9
            )

        ax.set_title(threshold_label, fontsize=10)
        ax.set_xlabel("Day periods", fontsize=8)
        ax.set_ylabel("Frequency", fontsize=8)
        ax.tick_params(axis="both", labelsize=8)
        ax.grid(True, alpha=0.3)

    # Hide unused axes
    for j in range(n, len(axes)):
        axes[j].axis("off")

    fig.suptitle(
        "ASX 200 Cycle Length Frequency by Drawdown Threshold (-5% to -50%)",
        fontsize=16
    )
    plt.tight_layout(rect=[0, 0, 1, 0.98])
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.show()


def create_summary_scatter(summary_df, output_path):
    """
    Create summary scatter:
    X axis = percentage decrease
    Y axis = number of complete cycles
    """
    plot_df = summary_df.sort_values("threshold_pct")

    plt.figure(figsize=(10, 6))
    plt.scatter(plot_df["threshold_pct"], plot_df["num_cycles"], s=60)

    for _, row in plot_df.iterrows():
        plt.annotate(
            str(int(row["num_cycles"])),
            (row["threshold_pct"], row["num_cycles"]),
            textcoords="offset points",
            xytext=(0, 6),
            ha="center",
            fontsize=8
        )

    plt.xlabel("Percentage of decrease from ATH (%)")
    plt.ylabel("Number of complete cycles")
    plt.title("ASX 200: Complete Cycles vs Drawdown Threshold")
    plt.xticks(range(-50, -4, 5))
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.show()


# =========================
# Main
# =========================
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Download and prepare data
    df = download_close_data(TICKER, START_DATE, END_DATE)
    df, ath_df, date_col = build_ath_table(df)

    print(f"Ticker: {TICKER}")
    print(f"Date range: {START_DATE} to {END_DATE}")
    print(f"Total new ATHs since 2010: {len(ath_df)}")

    all_results = []
    summary_rows = []
    detailed_cycle_rows = []

    for threshold in THRESHOLDS:
        result = analyze_threshold(df, ath_df, date_col, threshold)
        all_results.append(result)
        summary_rows.append(result["summary"])
        detailed_cycle_rows.extend(result["detailed_rows"])

    # Build output tables
    summary_df = pd.DataFrame(summary_rows)
    detailed_df = pd.DataFrame(detailed_cycle_rows)

    # Save CSV files
    summary_csv = os.path.join(OUTPUT_DIR, "asx_cycle_threshold_summary.csv")
    details_csv = os.path.join(OUTPUT_DIR, "asx_cycle_details.csv")

    summary_df.to_csv(summary_csv, index=False)
    detailed_df.to_csv(details_csv, index=False)

    # Print summary table
    print("\nSummary by threshold:")
    print(summary_df.to_string(index=False))

    # Optional: print detailed cycles for each threshold
    print("\nDetailed cycle counts by threshold:")
    for result in all_results:
        print(f"{result['threshold_label']}: {len(result['cycles_days'])} complete cycles")

    # Create plots
    panel_plot_path = os.path.join(OUTPUT_DIR, "asx_cycle_frequency_panels.png")
    summary_plot_path = os.path.join(OUTPUT_DIR, "asx_cycle_count_vs_drop.png")

    create_panel_scatter(all_results, panel_plot_path)
    create_summary_scatter(summary_df, summary_plot_path)

    print("\nFiles saved:")
    print(f"- {summary_csv}")
    print(f"- {details_csv}")
    print(f"- {panel_plot_path}")
    print(f"- {summary_plot_path}")


if __name__ == "__main__":
    main()