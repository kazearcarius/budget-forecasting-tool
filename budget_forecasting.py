"""
Automated Budget Forecasting Tool
================================

This module provides a simple command‑line workflow for producing
monthly revenue and expense forecasts from historical ledger data.
It reads transactional data exported from an accounting system,
aggregates it by month and category, fits a time‑series model and
produces a six‑month forecast.  The output can be saved as an Excel
report or fed into a BI dashboard.

Example usage::

    python budget_forecasting.py --input ledger.csv --output forecast.xlsx

Dependencies:
    pandas, numpy, statsmodels, openpyxl (optional: prophet)
"""

import argparse
from datetime import datetime
import pandas as pd
import numpy as np

try:
    from statsmodels.tsa.statespace.sarimax import SARIMAX
except ImportError:
    SARIMAX = None  # Statsmodels may not be installed in all environments


def load_ledger(path: str) -> pd.DataFrame:
    """Load the raw ledger export as a DataFrame.

    The CSV is expected to contain at least the columns:
    Date, Category, Amount (positive for revenue, negative for expense).
    """
    df = pd.read_csv(path, parse_dates=['Date'])
    df['Month'] = df['Date'].dt.to_period('M').dt.to_timestamp()
    return df


def aggregate_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate amounts by month and category."""
    return df.groupby(['Month', 'Category'])['Amount'].sum().reset_index()


def forecast_series(series: pd.Series, periods: int = 6) -> pd.Series:
    """Forecast a univariate time series using a simple ARIMA model.

    If statsmodels is not available, falls back to a naive forecast.
    """
    if SARIMAX is None or len(series) < 6:
        # Fallback: repeat last value
        last = series.iloc[-1]
        return pd.Series([last] * periods)

    model = SARIMAX(series, order=(1, 1, 1), seasonal_order=(0, 0, 0, 0))
    results = model.fit(disp=False)
    forecast = results.forecast(periods)
    return forecast


def build_forecast(df: pd.DataFrame, periods: int = 6) -> pd.DataFrame:
    """Build forecasts per category and return a long DataFrame."""
    forecasts = []
    for category, group in df.groupby('Category'):
        ts = group.set_index('Month')['Amount'].asfreq('MS').fillna(0)
        fc = forecast_series(ts, periods)
        fc_index = pd.date_range(ts.index[-1] + pd.offsets.MonthBegin(1), periods=periods, freq='MS')
        forecasts.append(pd.DataFrame({'Month': fc_index, 'Category': category, 'Forecast': fc.values}))
    return pd.concat(forecasts, ignore_index=True)


def save_to_excel(actuals: pd.DataFrame, forecast: pd.DataFrame, path: str) -> None:
    """Save the aggregated actuals and forecasts into an Excel workbook."""
    with pd.ExcelWriter(path) as writer:
        actuals.to_excel(writer, sheet_name='Actuals', index=False)
        forecast.to_excel(writer, sheet_name='Forecast', index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate budget forecasts from ledger data.")
    parser.add_argument("--input", required=True, help="Path to the ledger CSV export")
    parser.add_argument("--output", required=True, help="Path to save the Excel forecast")
    args = parser.parse_args()

    df = load_ledger(args.input)
    monthly = aggregate_by_month(df)
    forecast = build_forecast(monthly)
    save_to_excel(monthly, forecast, args.output)
    print(f"Forecast saved to {args.output}")


if __name__ == '__main__':
    main()