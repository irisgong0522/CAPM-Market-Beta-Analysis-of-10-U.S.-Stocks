"""Download CAPM prices. Run from a terminal with TIINGO_API_TOKEN set."""
import argparse
import os
from pathlib import Path
import sys
import pandas as pd
import requests

STOCKS = ['MSFT', 'GOOGL', 'AMZN', 'JPM', 'JNJ', 'PG', 'XOM', 'CAT', 'NEE', 'APD']
START, END = '2014-12-31', '2025-12-31'
ROOT = Path(__file__).resolve().parents[1]


def validate(frame, column):
    if frame.empty or frame.index.has_duplicates:
        raise ValueError('Empty data or duplicate dates')
    if frame[column].isna().any() or (frame[column] <= 0).any():
        raise ValueError('Missing or non-positive prices')
    if str(frame.index.min().date()) != START or str(frame.index.max().date()) != END:
        raise ValueError('Requested full date range was not returned')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--include-spy', action='store_true', help='Explicitly use SPY ETF as the S&P 500 proxy')
    args = parser.parse_args()
    token = os.environ.get('TIINGO_API_TOKEN', '').strip()
    if not token:
        sys.exit('TIINGO_API_TOKEN is missing. Run this from the terminal used for the successful API test.')
    target = ROOT / 'data' / 'capm_prices'
    target.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers['Authorization'] = 'Token ' + token
    tickers = STOCKS + (['SPY'] if args.include_spy else [])
    frames = []
    for ticker in tickers:
        dest = target / (ticker + '.csv')
        if dest.exists():
            frame = pd.read_csv(dest, index_col='date', parse_dates=True)
            validate(frame, 'adj_close')
            print(ticker + ': using existing CSV')
        else:
            response = session.get('https://api.tiingo.com/tiingo/daily/' + ticker + '/prices',
                params={'startDate': START, 'endDate': END, 'resampleFreq': 'daily'}, timeout=60)
            if response.status_code != 200:
                raise RuntimeError(ticker + ': HTTP ' + str(response.status_code) + '. Check token, account access, or request limits.')
            records = response.json()
            if not isinstance(records, list) or not records:
                raise ValueError(ticker + ': no price data returned')
            raw = pd.DataFrame(records)
            frame = pd.DataFrame({'date': pd.to_datetime(raw['date'], utc=True).dt.tz_localize(None),
                                  'adj_close': pd.to_numeric(raw['adjClose'], errors='raise')})
            frame = frame.set_index('date').sort_index()
            validate(frame, 'adj_close')
            temporary = dest.with_suffix('.tmp')
            frame.to_csv(temporary, date_format='%Y-%m-%d')
            temporary.replace(dest)
            print(ticker + ': saved ' + str(len(frame)) + ' rows', flush=True)
        frames.append(frame.rename(columns={'adj_close': ticker}))
    combined = pd.concat(frames, axis=1).sort_index()
    if combined.isna().any().any():
        raise ValueError('Trading dates differ across securities. Individual CSVs saved; inspect gaps before combining.')
    filename = 'stocks_and_spy_adj_close.csv' if args.include_spy else 'stocks_adj_close.csv'
    combined.to_csv(target / filename, date_format='%Y-%m-%d')
    print('Complete: ' + str(target / filename))


if __name__ == '__main__':
    try:
        main()
    except (requests.RequestException, ValueError, KeyError, RuntimeError) as exc:
        sys.exit('Download stopped: ' + str(exc))
