import pandas as pd
import numpy as np
import os

RAW_DIR = 'data/raw'
tickers = ['JNJ', 'UNH', 'LLY', 'MDT', 'NVO', 'PFE', 'ABT', 'ABBV', 'DGX']

rows = []

for ticker in tickers:
    path = f'{RAW_DIR}/{ticker}_raw.csv'
    if not os.path.exists(path):
        print(f"✗ {ticker}: not found")
        continue

    df = pd.read_csv(path, parse_dates=['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)

    price = df['mid_price']

    # Realized quadratic variation: sum of squared 1-second returns
    log_returns = np.log(price / price.shift(1)).dropna()
    qv = (log_returns ** 2).sum()

    # Average daily QV (normalize by number of trading days)
    n_days = df['timestamp'].dt.date.nunique()

    rows.append({
        'Ticker': ticker,
        'Obs (M)': round(len(df) / 1e6, 2),
        'Mean Price ($)': round(price.mean(), 2),
        'Std Price ($)': round(price.std(), 2),
        'Min Price ($)': round(price.min(), 2),
        'Max Price ($)': round(price.max(), 2),
        'Trading Days': n_days,
        'Avg Daily QV (x1e-4)': round(qv / n_days * 1e4, 3),
    })

    print(f'✓ {ticker} done', flush=True)

stats = pd.DataFrame(rows).set_index('Ticker')
print('\n')
print(stats.to_string())

# Save to CSV for easy copy into paper
stats.to_csv('summary_stats.csv')
print('\nSaved to summary_stats.csv')
