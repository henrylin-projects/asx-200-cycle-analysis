# ASX 200 Peak-to-Recovery Cycle Analysis

A Python-based market cycle analysis project that studies **ASX 200 recovery cycles** using historical price data from Yahoo Finance. The project measures how long it takes the index to recover from different drawdown levels back to a new all-time high (ATH), and visualizes the distribution of those recovery periods.

This project is designed as a **portfolio piece for equity research, market analysis, and data analytics**, showing practical use of Python for financial time-series analysis, data transformation, and visualization.

#Skills Demonstrated
Python scripting
pandas data wrangling
time-series analysis
CSV export automation
data visualization

financial market analytics
---

## Project Overview

The core idea is simple:

- Start from a **new closing all-time high (ATH)**
- Check whether the market falls by at least a chosen percentage (for example, **-10%**)
- If that drop happens before the next recovery to a new ATH, count it as a **complete cycle**
- Measure the number of calendar days from the starting ATH to the next new ATH

This allows the project to answer questions such as:

- How many complete recovery cycles has the ASX 200 had since 2010?
- How does the number of cycles change as the required drawdown gets deeper?
- Are shallow corrections much more common than deep drawdowns?
- How long do recovery cycles usually last?

---

## Key Features

### 1. Single-threshold cycle analysis
Analyze one drawdown threshold at a time, such as:

- `-7%`
- `-10%`
- `-15%`

Outputs include:

- Number of complete cycles
- Average cycle length
- Minimum cycle length
- Maximum cycle length
- Median cycle length
- Detailed list of cycle start/end dates

### 2. Multi-threshold batch analysis
Run the same logic across **46 drawdown thresholds**, from:

- `-5%`
- `-6%`
- `-7%`
- ...
- `-50%`

Outputs include:

- Summary table across all thresholds
- CSV export of summary statistics
- CSV export of detailed cycle-level data
- 46-panel scatter chart
- Summary scatter chart of threshold vs number of cycles

### 3. Visualization
The project creates:

- **Cycle frequency scatter panels**
  - X-axis = cycle day periods
  - Y-axis = frequency
- **Threshold summary scatter**
  - X-axis = percentage drawdown
  - Y-axis = number of complete cycles

---

## Why This Project Matters

This project demonstrates several useful skills for finance, investment, and analytics roles:

- Financial market data retrieval with Python
- Time-series preprocessing
- Rule-based cycle detection
- Statistical summary generation
- Data visualization with matplotlib
- Reproducible research workflow
- Translating market concepts into code logic

It is especially relevant for roles in:

- Equity research
- Investment analysis
- Quantitative analysis
- Data analytics / BI
- Financial modelling

---

## Methodology

### Cycle Definition
A **complete cycle** is defined as:

> **Starting ATH → drawdown threshold reached → recovery to next new ATH**

Example:

- Index reaches a new ATH
- Falls by at least `10%`
- Later climbs back to a new ATH
- Time between the two ATH dates is the cycle length

### Drawdown Thresholds
The batch version evaluates thresholds from:

- `-5%` to `-50%`
- in `1%` increments

### Data Source
- Yahoo Finance
- Ticker used: `^AXJO` (ASX 200)

### Time Range
- Start date: `2010-01-01`
- End date: current system date when script runs

---

## Repository Structure

```text
asx-200-cycle-analysis/
│
├── single_run_asx_historical_peak_analysis.py
├── multiple_run_and_visualisation.py
├── output_asx_cycles/
│   ├── asx_cycle_threshold_summary.csv
│   ├── asx_cycle_details.csv
│   ├── asx_cycle_frequency_panels.png
│   └── asx_cycle_count_vs_drop.png
├── requirements.txt
└── README.md
