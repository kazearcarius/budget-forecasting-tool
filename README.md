# Automated Budget Forecasting Tool

This project helps small businesses forecast monthly revenue and expense using historical ledger data. It loads exports from Xero or QuickBooks, aggregates by month and category, applies simple time-series models (e.g. ARIMA) to predict future cash needs, and outputs forecasts for budgeting.

## Features

- Load and normalize ledger data in CSV format.
- Aggregate amounts by month and category.
- Fit an ARIMA model to produce a six-month forecast.
- Output Excel reports with actuals and forecasts for each category.
- Optional scenario analysis (growth assumptions) and integration with Power BI.
