# DDQL Optimal Execution

Replication and extension of Ning et al. (2020) using healthcare stocks and a risk-averse reward modification.

## Quickstart

### 1. Clone the repo
git clone https://github.com/ishani-agarwal/DDQL.git
cd DDQL

### 2. Install dependencies
pip install -r requirements.txt
pip install wrds

### 3. Get the data
Download from Google Drive: https://drive.google.com/drive/folders/1Qphnfm6AKNq-kAaIWUEfIi85BUnOcN1G?usp=drive_link
unzip data_split.zip INTO THE REPO ROOT

### 4. Run the notebook
Open `notebooks/draft.ipynb` and run all cells.

## Data
- `data/train/` — 6761 training episodes (Jan 2017 - Dec 2017)
- `data/test/` — 1647 test episodes (Jan 2018 - Mar 2018)
- 9 healthcare stocks: JNJ, UNH, LLY, MDT, NVO, PFE, ABT, ABBV, DGX
- Source: NYSE TAQ millisecond data via WRDS
