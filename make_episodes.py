import pandas as pd
import os

# Each episode = one trading hour (11-12, 12-13, 13-14) for one ticker on one day
# Train: Jan 2017 - Dec 2017, Test: Jan 2018 - Mar 2018

# Input: per-ticker 1-second mid-price CSVs from data_pull.py
# Output: per-episode CSVs with columns [Date, Price] consumed by the DDQL environment

RAW_DIR = 'data/raw'
TRAIN_DIR = 'data/train'
TEST_DIR = 'data/test'

os.makedirs(TRAIN_DIR, exist_ok=True)
os.makedirs(TEST_DIR, exist_ok=True)

# Analyze 11am-12pm, 12pm-1pm, 1pm-2pm separately, matching Ning et al. (2020)
# This avoids diurnal volatility patterns at open and close
HOURS = [11, 12, 13]

# Chronological split: train on 2017, test on Jan-Mar 2018
# No random shuffling to prevent future data leaking into training
TRAIN_CUTOFF = '2018-01-01'

# Healthcare equities universe replacing the original paper's tech stocks
tickers = ['JNJ', 'UNH', 'LLY', 'MDT', 'NVO', 'PFE', 'ABT', 'ABBV', 'DGX']

total_train, total_test = 0, 0

for ticker in tickers:
    path = f'{RAW_DIR}/{ticker}_raw.csv'
    if not os.path.exists(path):
        print(f"✗ {ticker}: raw file not found, skipping")
        continue

    # Load 1-second mid-price data and rename to match preprocessor expectations
    df = pd.read_csv(path, parse_dates=['timestamp'])
    df = df.rename(columns={'timestamp': 'Date', 'mid_price': 'Price'})
    df = df.sort_values('Date').reset_index(drop=True)

    # Extract date and hour for grouping into episodes
    df['date'] = df['Date'].dt.date
    df['hour'] = df['Date'].dt.hour

    for (date, hour), group in df.groupby(['date', 'hour']):
        if hour not in HOURS:
            continue
        if len(group) < 100:
            # Skip episodes with too few seconds (early closes, data gaps)
            continue

        # Each episode is a single hour of 1-second mid-prices for one ticker
        episode = group[['Date', 'Price']].reset_index(drop=True)

        # Assign to train or test based on date
        if str(date) < TRAIN_CUTOFF:
            out_dir = TRAIN_DIR
            total_train += 1
        else:
            out_dir = TEST_DIR
            total_test += 1

        # Filename encodes ticker, date, and hour for traceability
        fname = f'{ticker}_{date}_h{hour}.csv'
        episode.to_csv(f'{out_dir}/{fname}', index=False)

    print(f'✓ {ticker} done', flush=True)

print(f'\nTotal train episodes: {total_train}')
print(f'Total test episodes:  {total_test}')