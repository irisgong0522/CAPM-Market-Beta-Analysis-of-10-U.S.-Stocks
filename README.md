# CAPM: Market Beta Analysis of 10 U.S. Stocks

## Overview

This project estimates the Capital Asset Pricing Model (CAPM) for 10 U.S. stocks using daily returns from **2 January 2015 to 31 December 2025**. SPY is the market proxy. The analysis compares full-sample alpha, beta, explanatory power, and statistical significance, and examines beta stability using **252-day and 126-day rolling windows**.

The main analysis is in [CAPM_analysis.ipynb](notebooks/CAPM_analysis.ipynb). It includes a regression table, a beta comparison bar chart, scatter plots with regression lines, residual plots, and two rolling-beta charts. The submission checklist below distinguishes implemented analysis from remaining corrections and written interpretation.

## Data and Sample

| Item                  | Current implementation                                                                         |
| --------------------- | ---------------------------------------------------------------------------------------------- |
| Stock universe        | MSFT, GOOGL, AMZN, JPM, JNJ, PG, XOM, CAT, NEE, APD                                            |
| Market benchmark      | SPY ETF, used as a proxy for the S&P 500                                                       |
| Price source          | Tiingo; downloader retains the`adjClose` field as `adj_close`                              |
| Price coverage        | 31 December 2014 to 31 December 2025; the initial price supports the first 2015 return         |
| Return sample         | 2 January 2015 to 31 December 2025; 2,766 daily observations per security                      |
| Return definition     | Simple adjusted-price returns, expressed as decimals:`P_t / P_(t-1) - 1`                     |
| Risk-free input       | FRED DTB3, 3-month Treasury bill secondary-market rate, annualized percent on a discount basis |
| Risk-free source file | `data/risk_free/fred_dtb3.csv`; source notes in [risk-free README](data/risk_free/README.md)  |
| Rolling windows       | 252 trading observations (approximately one year) and 126 (approximately six months)           |

The selected companies span several business areas, but are not ten distinct sectors:

| Ticker | Company                    | Broad business area                       |
| ------ | -------------------------- | ----------------------------------------- |
| MSFT   | Microsoft                  | Software and cloud services               |
| GOOGL  | Alphabet                   | Internet services and digital advertising |
| AMZN   | Amazon                     | E-commerce and cloud services             |
| JPM    | JPMorgan Chase             | Banking                                   |
| JNJ    | Johnson & Johnson          | Healthcare                                |
| PG     | Procter & Gamble           | Household and personal-care products      |
| XOM    | Exxon Mobil                | Oil and gas                               |
| CAT    | Caterpillar                | Construction and mining equipment         |
| NEE    | NextEra Energy             | Utilities and power generation            |
| APD    | Air Products and Chemicals | Industrial gases                          |

These are descriptive business areas, not a historical sector-classification dataset. This is a selected-stock study, not a representative or survivorship-free sample of the market.

### Data processing and missing observations

`data/data_process.py` validates the individual price files, checks date alignment and positive prices, and calculates returns with `pct_change(fill_method=None)`. It does not fill missing stock prices to manufacture returns.

The notebook merges returns and the risk-free series by date, sorts dates in ascending order, and forward-fills **only the converted risk-free rate**. In the current sample, 20 trading dates lack a matched risk-free observation before filling. After this step, the analysis data have no missing values and each full-sample regression uses 2,766 observations.

Forward filling assumes that the most recent rate available in the merged trading-date table remains applicable on a missing date. It does not use later observations. Exact publication-time availability is not modeled.

### Risk-free conversion: current approximation

The notebook currently applies:

```python
rf["Risk_Free_Rate"] = (1 + rf["DTB3"] / 100) ** (1 / 252) - 1
```

This treats the annual quote as if it were an effective annual yield and converts it to a daily decimal return. **DTB3 is actually a bank-discount quote, so this is a simplifying approximation, not an exact Treasury-bill holding-period return.** The results below reflect this implementation. A more precise treatment would require a documented conversion from the discount quote or a differently specified risk-free return series, followed by rerunning the analysis.

## Model and Estimation

For each stock, estimate an OLS regression with an intercept:

```text
R_stock,t - R_f,t = alpha + beta * (R_SPY,t - R_f,t) + epsilon_t
```

- **Alpha:** daily intercept in decimal-return units; multiply by 100 for percent per day. It is not annualized in the results table.
- **Beta:** sensitivity of stock excess returns to market excess returns; it is not a measure of total stock volatility.
- **R-squared:** fraction of in-sample stock excess-return variation explained by the market factor.
- **P-values:** the main regression uses `fit(cov_type="HC3")`, providing heteroskedasticity-robust standard errors. HC3 does not adjust for serial correlation.

The coefficient p-values test a coefficient against **zero**. In particular, `Beta_pvalue` does not test whether beta differs from one. The dashed beta = 1 lines in the charts are visual references, not significance tests.

The analysis is in-sample: it uses the same observations to estimate and describe model fit. No train/test split, out-of-sample forecast, or trading backtest is implemented.

### Rolling beta

Each rolling estimate is calculated as:

```text
beta_t = Cov(stock excess return, market excess return)
         / Var(market excess return)
```

Both quantities use the same trailing window, including the observation at date `t`. A new day enters and the oldest day leaves as the window moves forward. The chart date is the end of the estimation window.

The 252-day window produces 2,515 valid estimates per stock, starting on 31 December 2015. The 126-day window produces 2,641, starting on 2 July 2015. The first `window - 1` values are unavailable by construction. Shorter windows can respond faster but tend to yield less stable estimates.

The two charts are implemented in separate cells. At present, both write to the same `*_Rolling_Beta` column names, so running the 126-day cell replaces the stored 252-day values. The earlier displayed plot remains, but the final dataframe contains the 126-day estimates.

## Current Full-Sample Results

Recomputed from the saved notebook and local data on 13 September 2026, including forward-filled risk-free observations. Alpha is a **daily decimal return**; figures below are rounded.

| Stock |     Alpha |   Beta | R-squared | Alpha p-value |
| ----- | --------: | -----: | --------: | ------------: |
| MSFT  |  0.000393 | 1.1877 |    0.6177 |        0.0487 |
| GOOGL |  0.000424 | 1.1476 |    0.5013 |        0.0827 |
| AMZN  |  0.000537 | 1.1838 |    0.4092 |        0.0791 |
| JPM   |  0.000234 | 1.0992 |    0.5192 |        0.2979 |
| JNJ   |  0.000107 | 0.4913 |    0.2307 |        0.5781 |
| PG    |  0.000017 | 0.5112 |    0.2414 |        0.9296 |
| XOM   | -0.000065 | 0.8286 |    0.2892 |        0.8137 |
| CAT   |  0.000340 | 1.0810 |    0.4120 |        0.2200 |
| NEE   |  0.000235 | 0.6402 |    0.2132 |        0.3715 |
| APD   | -0.000097 | 0.9006 |    0.3942 |        0.6847 |

## Project Structure

```text
CAPM/
├── data/
│   ├── capm_prices/                    # Individual and combined adjusted-price CSVs
│   ├── risk_free/                      # DTB3 CSV and source notes
│   ├── processed/daily_returns.csv     # Daily simple returns
│   └── data_process.py                 # Price validation and return calculation
├── notebooks/CAPM_analysis.ipynb       # Main analysis and figures
├── src/download_capm_data.py           # Tiingo downloader
├── outputs/                           # Saved figures, including earlier runs
├── reports/                           # written report
├── README.md
└── requirements.txt
```

## Run the Project

### Existing local environment

```bash
cd ~/Desktop/CAPM
source .venv/bin/activate
```

In VS Code, open `notebooks/CAPM_analysis.ipynb`, select the project's Python 3.12 `.venv` kernel, restart the kernel, and run all cells in order. The notebook uses paths such as `../data/...`, so its working directory must be `CAPM/notebooks`.

### Rebuild returns from saved prices

From the project root:

```bash
python data/data_process.py
```

This regenerates `data/processed/daily_returns.csv`. Rerun the notebook afterward to refresh estimates and charts.

### Retrieve prices if needed

The downloader requires `TIINGO_API_TOKEN` in the environment and access to the requested Tiingo data. Do not put the token in source files or the README.

```bash
python src/download_capm_data.py --include-spy
```

The script reuses existing validated price CSVs rather than refreshing them automatically. The FRED CSV is supplied locally; an automated risk-free download step is not included in the current project. Consult the risk-free source notes for its series and requested date range. Actual retrieval timestamps are not recorded in the current data files.
