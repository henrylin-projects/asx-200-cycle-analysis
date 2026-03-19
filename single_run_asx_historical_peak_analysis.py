# Python for ASX historical peak analysis

import yfinance as yf
import pandas as pd
from datetime import datetime

# Fetch daily data for ASX 200 from 2010 to now
ticker = "^AXJO"
end_date = datetime.today().strftime("%Y-%m-%d")

data = yf.download(ticker, start="2010-01-01", end=end_date, progress=False)

# Keep only Close column and rename it
df = data[["Close"]].copy()
df.columns = ["close"]

# Compute running all-time high (ATH)
df["ath"] = df["close"].cummax()
df["is_new_ath"] = df["close"] == df["ath"]  # True on new closing ATHs

# Extract dates of new ATHs
ath_df = df[df["is_new_ath"]].copy().reset_index()  # so we have Date column

print(f"Total new ATHs since 2010: {len(ath_df)}")

# Identify cycles:
# start at one ATH -> >=10% drop somewhere in between -> next new ATH
cycles_days = []
cycle_starts = []
cycle_ends = []

for i in range(1, len(ath_df)):
    start_date = ath_df["Date"].iloc[i - 1]
    end_date = ath_df["Date"].iloc[i]
    start_peak = ath_df["close"].iloc[i - 1]

    # Slice the period between these two ATHs (inclusive)
    period = df.loc[start_date:end_date].copy()
    min_price_in_period = period["close"].min()

    # Check for minimum 10% drop from the starting peak
    if min_price_in_period <= start_peak * 0.90:
        days = (end_date - start_date).days
        cycles_days.append(days)
        cycle_starts.append(start_date.strftime("%Y-%m-%d"))
        cycle_ends.append(end_date.strftime("%Y-%m-%d"))

# Results
if cycles_days:
    num_cycles = len(cycles_days)
    avg_days = sum(cycles_days) / num_cycles
    min_days = min(cycles_days)
    max_days = max(cycles_days)

    sorted_days = sorted(cycles_days)
    if num_cycles % 2 == 1:
        median_days = sorted_days[num_cycles // 2]
    else:
        median_days = (sorted_days[num_cycles // 2 - 1] + sorted_days[num_cycles // 2]) / 2

    print(f"\nNumber of complete cycles since 2010 (with >=10% drop): {num_cycles}")
    print(f"Average cycle length: {avg_days:.0f} days")
    print(f"Min cycle length: {min_days} days")
    print(f"Max cycle length: {max_days} days")
    print(f"Median cycle length: {median_days:.1f} days")

    # Optional: list each cycle
    print("\nIndividual cycles (start ATH -> end ATH, days):")
    for s, e, d in zip(cycle_starts, cycle_ends, cycles_days):
        print(f"  {s} -> {e} ({d} days)")
else:
    print("No qualifying cycles found.")