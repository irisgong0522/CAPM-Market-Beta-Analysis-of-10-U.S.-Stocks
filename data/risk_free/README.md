# FRED Risk-Free Rate Source

- Series: DTB3, 3-Month Treasury Bill Secondary Market Rate, Discount Basis.
- Source: https://fred.stlouisfed.org/series/DTB3
- Requested period: 2014-12-01 through 2025-12-31. The extra history supports alignment at the start of the stock sample.
- Frequency: daily observations.
- Units: annualized percent, discount basis; not a daily holding-period return.
- CSV columns: date, DTB3. Missing source observations are retained as blank values.
- No rate conversion or forward filling has been applied.
- During analysis, align to stock trading dates using only available prior observations and document the quote-to-return conversion. Do not subtract the raw rate directly from stock returns.
