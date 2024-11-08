"""
This script retrieves AS numbers, IPv4, and/or IPv6 addresses
with prefixes for one or more given country codes.
"""

import argparse
import os
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.progress import track

# Suppress FutureWarnings
warnings.simplefilter(action="ignore", category=FutureWarning)

console = Console(log_path=False)

# Argument parsing
parser = argparse.ArgumentParser(
    description="Get AS numbers, IPv4, and/or IPv6 allocations of one or more countries"  # noqa: E501
)
parser.add_argument(
    "countries",
    nargs="+",
    help="Country codes (e.g., 'FR', 'US')",
)
parser.add_argument(
    "--data-type",
    choices=["asn", "ipv4", "ipv6", "all"],
    default="asn",
    help="Specify which data to fetch: 'asn', 'ipv4', 'ipv6', or 'all'",
)
args = parser.parse_args()

# Set Headers
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ASNumberFetcher/1.0)"}

# Base URLs
BASE_URLS = {
    "asn": "https://www-public.imtbs-tsp.eu/~maigron/rir-stats/rir-delegations/delegations/asn/{country}-asn-delegations.html",  # noqa: E501
    "ipv4": "https://www-public.imtbs-tsp.eu/~maigron/rir-stats/rir-delegations/delegations/ipv4/{country}-ipv4-delegations.html",  # noqa: E501
    "ipv6": "https://www-public.imtbs-tsp.eu/~maigron/rir-stats/rir-delegations/delegations/ipv6/{country}-ipv6-delegations.html",  # noqa: E501
}


def fetch_data(country_code, data_type):
    """Fetch ASN, IPv4, or IPv6 data for a given country code."""
    url = BASE_URLS[data_type].format(country=country_code.lower())
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        # Locate the table
        table = soup.find(
            "table",
            attrs={"class": f"delegs {data_type} ripencc"},
        )
        if not table:
            console.log(
                f"[yellow]No data table found for {data_type.upper()} in {country_code}.[/yellow]"  # noqa: E501
            )
            return country_code, data_type, None, None

        # Extract headers and rows
        headers = [header.text.strip() for header in table.find_all("th")]
        rows = table.find_all("tr")[2:]

        # Collect data rows
        data_rows = []
        allocations = []
        for row in rows:
            columns = [td.text.strip() for td in row.find_all("td")]
            if columns:
                row_data = dict(zip(headers[1:], columns))
                data_rows.append(row_data)

                if data_type == "asn" and columns[6] == "Allocated":
                    allocations.append(columns[3])  # Collect allocated ASNs
                elif data_type in ["ipv4", "ipv6"] and columns[7] == "Allocated":
                    ip_with_prefix = f"{columns[3]}{columns[4].strip()}"
                    allocations.append(ip_with_prefix)

        return country_code, data_type, data_rows, allocations

    except requests.exceptions.RequestException as e:
        console.log(
            f"[red]Error fetching {data_type.upper()} data for {country_code}: {e}[/red]"  # noqa: E501
        )
        return country_code, data_type, None, None


# Run fetch requests in parallel
country_data = {}
output_dir = "output_data"
os.makedirs(output_dir, exist_ok=True)

console.log("[blue]Fetching data for countries...[/blue]")

# Prepare to fetch all specified data types
data_types = [args.data_type] if args.data_type != "all" else ["asn", "ipv4", "ipv6"]

# Create a new console instance for cleaner logging within the progress bar
console_no_time = Console(log_path=False, log_time=False)

with ThreadPoolExecutor() as executor:
    futures = [
        executor.submit(fetch_data, country, data_type)
        for country in args.countries
        for data_type in data_types
    ]

    for future in track(
        as_completed(futures),
        total=len(futures),
        description="Processing data...",
    ):
        country_code, data_type, data_rows, allocations = future.result()
        if data_rows is not None:
            # Save data to CSV for each country and type
            df = pd.DataFrame(data_rows)
            csv_filename = os.path.join(
                output_dir, f"{country_code}_{data_type}_list.csv"
            )
            df.to_csv(csv_filename, index=False)

            # Improve readability with a new console instance
            console_no_time.log(
                f" [green]Data saved for {data_type.upper()} in {country_code}[/green]"  # noqa: E501
            )

            # Write IP or ASN ranges to ranges file
            if data_type in ["asn", "ipv4", "ipv6"]:
                range_file_path = os.path.join(
                    output_dir,
                    f"{data_type}_ranges.txt",
                )
                with open(range_file_path, "a", encoding="UTF-8") as range_file:
                    range_file.write(",".join(allocations) + "\n")

console.log(
    f"[green]Completed fetching data for {len(args.countries)} countries.[/green]"  # noqa: E501
)
