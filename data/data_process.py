"""Calculate daily simple returns from the downloaded adjusted prices."""
from pathlib import Path
import pandas as pd

TICKERS = ['MSFT', 'GOOGL', 'AMZN', 'JPM', 'JNJ', 'PG', 'XOM', 'CAT', 'NEE', 'APD', 'SPY']
DATA_DIR = Path(__file__).resolve().parent


def main():
    prices = []
    for ticker in TICKERS:
        path = DATA_DIR / 'capm_prices' / f'{ticker}.csv'
        if not path.exists():
            raise FileNotFoundError(f'Missing price file: {path}')
        df = pd.read_csv(path)
        if not {'date', 'adj_close'}.issubset(df.columns):
            raise ValueError(f'{path.name}: expected date and adj_close columns')
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='raise')
        df['adj_close'] = pd.to_numeric(df['adj_close'], errors='raise')
        df = df.set_index('date').sort_index()
        if df.empty or df.index.has_duplicates:
            raise ValueError(f'{ticker}: empty data or duplicate dates')
        if df['adj_close'].isna().any() or (df['adj_close'] <= 0).any():
            raise ValueError(f'{ticker}: missing or non-positive prices')
        prices.append(df['adj_close'].rename(ticker))

    combined = pd.concat(prices, axis=1).sort_index()
    if combined.isna().any().any():
        raise ValueError('Price dates do not match. Inspect missing observations before calculating returns.')
    if combined.index.min() >= pd.Timestamp('2015-01-01'):
        raise ValueError('A price before 2015 is required to calculate the first 2015 return.')
    returns = combined.pct_change(fill_method=None).loc['2015-01-01':'2025-12-31']
    if returns.empty or returns.isna().any().any():
        raise ValueError('Empty or incomplete return data')
    output_dir = DATA_DIR / 'processed'
    output_dir.mkdir(exist_ok=True)
    output = output_dir / 'daily_returns.csv'
    returns.to_csv(output, date_format='%Y-%m-%d')
    print(f'Saved {len(returns)} trading days and {len(returns.columns)} securities to {output}')
    print('Returns are decimals: 0.01 means 1%. Risk-free rates have not been subtracted.')


if __name__ == '__main__':
    main()
