import wrds
import pandas as pd
from datetime import datetime, timedelta
import os

os.makedirs('data/raw', exist_ok=True)

def get_trading_dates(start, end):
    dates = []
    current = datetime.strptime(start, '%Y-%m-%d')
    end_dt = datetime.strptime(end, '%Y-%m-%d')
    while current <= end_dt:
        if current.weekday() < 5:
            dates.append(current.strftime('%Y%m%d'))
        current += timedelta(days=1)
    return dates

tickers = ['JNJ', 'UNH', 'LLY', 'MDT', 'NVO', 'PFE', 'ABT', 'MRNA', 'DGX']
dates = get_trading_dates('2017-01-02', '2018-03-30')

print(f"Trading days: {len(dates)}, Total queries: {len(dates) * len(tickers)}", flush=True)

conn = wrds.Connection(wrds_username='snpatel7')

failed = []

for ticker in tickers:
    if os.path.exists(f'data/raw/{ticker}_raw.csv'):
        print(f"⏭ {ticker}: already exists, skipping", flush=True)
        continue

    ticker_dfs = []
    for i, date in enumerate(dates):
        try:
            df = conn.raw_sql(f"""
                SELECT date, time_m, best_bid, best_ask,
                       (best_bid+best_ask)/2 as mid_price
                FROM taqmsec.complete_nbbo_{date}
                WHERE sym_root = '{ticker}'
                AND time_m BETWEEN '11:00:00' AND '14:00:00'
            """)
            if len(df) > 0:
                ticker_dfs.append(df)
            if i % 25 == 0:
                print(f"  {ticker}: {i}/{len(dates)} days done", flush=True)
        except Exception as e:
            failed.append((ticker, date, str(e)))
            continue

    if ticker_dfs:
        ticker_df = pd.concat(ticker_dfs)
        ticker_df['timestamp'] = pd.to_datetime(
            ticker_df['date'].astype(str) + ' ' + ticker_df['time_m'].astype(str),
            format='mixed'
        )
        ticker_df = (ticker_df
            .set_index('timestamp')
            .resample('1S')['mid_price']
            .last()
            .dropna()
            .reset_index()
        )
        ticker_df.to_csv(f'data/raw/{ticker}_raw.csv', index=False)
        print(f"✓ {ticker}: {len(ticker_df)} seconds saved", flush=True)

print(f"\nFailed: {len(failed)}", flush=True)
conn.close()
