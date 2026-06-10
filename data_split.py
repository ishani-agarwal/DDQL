import pandas as pd
import os

RAW_DIR = '/Users/stuti/DDQL/data/raw'
TRAIN_DIR = '/Users/stuti/DDQL/data/train'
TEST_DIR = '/Users/stuti/DDQL/data/test'

os.makedirs(TRAIN_DIR, exist_ok=True)
os.makedirs(TEST_DIR, exist_ok=True)

HOURS = [11, 12, 13]
TRAIN_CUTOFF = '2018-01-01'
N_PERIODS = 5

tickers = ['JNJ', 'UNH', 'LLY', 'MDT', 'NVO', 'PFE', 'ABT', 'ABBV', 'DGX']

total_train, total_test = 0, 0

for ticker in tickers:
    path = f'{RAW_DIR}/{ticker}_raw.csv'
    if not os.path.exists(path):
        print(f"✗ {ticker}: raw file not found, skipping")
        continue

    df = pd.read_csv(path, parse_dates=['timestamp'])
    df = df.rename(columns={'timestamp': 'Date', 'mid_price': 'Price'})
    df = df.sort_values('Date').reset_index(drop=True)

    df['date'] = df['Date'].dt.date
    df['hour'] = df['Date'].dt.hour

    for (date, hour), group in df.groupby(['date', 'hour']):
        if hour not in HOURS:
            continue

        episode = group[['Date', 'Price']].reset_index(drop=True)

        # Trim to nearest multiple of N_PERIODS so preprocessor can split evenly
        trim = len(episode) - (len(episode) % N_PERIODS)
        episode = episode.iloc[:trim]

        # Skip episodes that are too short after trimming
        if len(episode) < 100:
            continue

        if str(date) < TRAIN_CUTOFF:
            out_dir = TRAIN_DIR
            total_train += 1
        else:
            out_dir = TEST_DIR
            total_test += 1

        fname = f'{ticker}_{date}_h{hour}.csv'
        episode.to_csv(f'{out_dir}/{fname}', index=False)

    print(f'✓ {ticker} done', flush=True)

print(f'\nTotal train episodes: {total_train}')
print(f'Total test episodes:  {total_test}')