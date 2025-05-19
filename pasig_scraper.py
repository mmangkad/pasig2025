"""Script to download and compile 2025 Pasig City election results
from the COMELEC website into a structured CSV file.

Author: Mohammad Miadh Angkad
Date: 19 May 2025
"""

import os
import json
import time
from urllib.parse import urljoin
from dateutil.parser import parse

import pandas as pd
import requests
from tqdm import tqdm
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://2025electionresults.comelec.gov.ph/"
PRECINCT_BASE = "data/regions/precinct"
PASIG_CODE = "7403000"

session = requests.Session()
retries = Retry(
    total=5,
    backoff_factor=1.0,
    status_forcelist=[502, 503, 504],
    allowed_methods=["GET"]
)
adapter = HTTPAdapter(max_retries=retries)
session.mount("http://", adapter)
session.mount("https://", adapter)


def load_or_download(file_path, url, delay=0.5):
    """Download a file from URL or load it locally if already saved."""
    if os.path.exists(file_path):
        with open(file_path) as f:
            return json.load(f)

    resp = session.get(url, timeout=10)
    data = resp.json()

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(data, f)

    if "Last-Modified" in resp.headers:
        ts = parse(resp.headers["Last-Modified"]).astimezone().timestamp()
        os.utime(file_path, (ts, ts))

    time.sleep(delay)
    return data


def get_pasig_barangays():
    """Fetch all barangays under Pasig City."""
    pasig_url = urljoin(BASE_URL, f"data/regions/local/{PASIG_CODE}.json")
    pasig_path = f"debug/pasig_{PASIG_CODE}.json"
    pasig_data = load_or_download(pasig_path, pasig_url)
    return pasig_data["regions"]


def download_precincts(barangays):
    """Download precinct-level data for each barangay."""
    for bgy in tqdm(barangays, desc="Downloading precinct data"):
        code = bgy["code"]
        name = bgy["name"].replace("/", "_").strip()
        code_prefix = code[:2]

        precinct_url = urljoin(BASE_URL, f"{PRECINCT_BASE}/{code_prefix}/{code}.json")
        path = f"pasig_precincts/{name}_{code}.json"
        load_or_download(path, precinct_url)


def extract_election_results():
    """Extract vote results from downloaded precinct files."""
    all_results = []
    precinct_files = [f for f in os.listdir("pasig_precincts") if f.endswith(".json")]

    er_loop = tqdm(precinct_files, desc="Downloading ER data", unit="file")

    for filename in er_loop:
        with open(os.path.join("pasig_precincts", filename)) as f:
            precinct_data = json.load(f)

        for region in precinct_data.get("regions", []):
            er_code = region["code"]
            er_url = urljoin(BASE_URL, f"data/er/{er_code[:3]}/{er_code}.json")
            er_path = f"pasig_er/{er_code}.json"
            er_data = load_or_download(er_path, er_url)

            # Update progress bar with current ER code
            er_loop.set_postfix_str(f"Processing ER {er_code}")

            for contest in er_data.get("national", []) + er_data.get("local", []):
                contest_name = contest["contestName"]
                for cand in contest["candidates"]["candidates"]:
                    all_results.append({
                        "precinct": er_code,
                        "contest": contest_name,
                        "candidate": cand["name"],
                        "votes": cand["votes"],
                        "percentage": cand["percentage"]
                    })

    return all_results


def main():
    """Main execution function."""
    barangays = get_pasig_barangays()
    download_precincts(barangays)
    results = extract_election_results()
    df = pd.DataFrame(results)
    df.to_csv("pasig_results.csv", index=False)
    print("Results saved to pasig_results.csv")


if __name__ == "__main__":
    main()
