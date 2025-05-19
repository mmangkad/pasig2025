# Pasig 2025 Election Scraper & Visualizer

This project includes two Python scripts:

- `pasig_scraper.py`: Downloads precinct-level election results from the COMELEC 2025 portal and compiles them into `pasig_results.csv`.
- `pasig_visualizer.py`: Reads the CSV and generates bar charts of the top 5 candidates per key race (Mayor, Vice Mayor, House Rep, Senators).

## How to Run

1. Run the scraper to generate the dataset:

```bash
python pasig_scraper.py
```

2. Run the visualizer to generate charts:

```bash
python pasig_visualizer.py
```

Charts are saved as PNGs in the current folder.

## Requirements

- Python 3.7+
- pandas, matplotlib, requests, tqdm, python-dateutil

Install with:

```bash
pip install -r requirements.txt
```

## Data Source

Official COMELEC 2025 results portal: https://2025electionresults.comelec.gov.ph/

---
```
