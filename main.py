"""This script retrieves all AS numbers for one or more given country codes."""

import argparse
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.progress import track
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import warnings
import os

# Suppress FutureWarnings
warnings.simplefilter(action="ignore", category=FutureWarning)

console = Console()

# Argument parsing
parser = argparse.ArgumentParser(description="Get AS numbers of one or more countries")
parser.add_argument("countries", nargs="+", help="Country codes (e.g., 'FR', 'US')")
args = parser.parse_args()

# Set Headers for the request
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ASNumberFetcher/1.0)"}

def fetch_asn_data(country_code):
    """Fetch AS number data for a given country code."""
    url = f"https://www-public.imtbs-tsp.eu/~maigron/RIR_Stats/RIR_Delegations/Delegations/ASN/{country_code}.html"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        # Locate the table
        table = soup.find("table", attrs={"class": "delegs asn ripencc"})
        if not table:
            console.log(f"[yellow]No data table found for {country_code}.[/yellow]")
            return country_code, None, None

        # Extract headers and rows
        headers = [header.text.strip() for header in table.find_all("th")]
        rows = table.find_all("tr")[2:]  # Skip the header rows

        # Collect ASN rows and write AS numbers to ranges file
        data_rows = []
        as_numbers = []
        for row in rows:
            columns = [td.text.strip() for td in row.find_all("td")]
            if columns:
                data_rows.append(dict(zip(headers[1:], columns))) 
                if columns[6] == "Allocated":  # Collect allocateds
                    as_numbers.append(columns[3])

        return country_code, data_rows, as_numbers

    except requests.exceptions.RequestException as e:
        console.log(f"[red]Error fetching data for {country_code}: {e}[/red]")
        return country_code, None, None

# Run fetch in parallel
country_data = {}
asn_list = []
output_dir = "asn_data"
os.makedirs(output_dir, exist_ok=True)

console.log("\t[blue]Fetching AS data for countries...[/blue]")

with ThreadPoolExecutor() as executor:
    future_to_country = {executor.submit(fetch_asn_data, country): country for country in args.countries}

    for future in track(as_completed(future_to_country), total=len(args.countries), description="Processing countries..."):
        country_code, data_rows, as_numbers = future.result()
        if data_rows is not None:
            country_data[country_code] = data_rows
            asn_list.extend(as_numbers)
            # Save data to CSV
            df = pd.DataFrame(data_rows)
            df.to_csv(os.path.join(output_dir, f"{country_code}_asn_list.csv"), index=False)
            console.log(f"[green]Data saved for {country_code}[/green]")

# Write all AS numbers to ranges.txt
ranges_file_path = os.path.join(output_dir, "ranges.txt")
with open(ranges_file_path, "w", encoding="UTF-8") as ranges_file:
    ranges_file.write(",".join(asn_list))

console.log(f"[green]Completed fetching data for {len(args.countries)} countries. ASNs saved to {ranges_file_path}[/green]")