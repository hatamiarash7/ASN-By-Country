#!/usr/bin/env python3
"""
Country Network Data Scraper

This script retrieves AS numbers, IPv4, and/or IPv6 addresses with prefixes
for one or more given country codes from RIR delegation statistics.

Features:
- Multi-threaded fetching for improved performance
- Comprehensive error handling
- Clean data output in CSV and text formats
- Progress tracking with rich console output
"""

import argparse
import os
import sys
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup, PageElement
from requests.exceptions import RequestException
from rich.console import Console

DEFAULT_TIMEOUT = 10
MAX_WORKERS = 5  # Optimal balance between performance and server load
OUTPUT_DIR = "output_data"

# Suppress FutureWarnings from pandas
warnings.simplefilter(action="ignore", category=FutureWarning)

# Initialize console for rich output
console = Console(log_path=False)


class DataFetcher:
    """Handles fetching and processing of country network data."""

    BASE_URLS: dict[str, str] = {
        "asn": "https://www-public.imtbs-tsp.eu/~maigron/rir-stats/rir-delegations/delegations/asn/{country}-asn-delegations.html",
        "ipv4": "https://www-public.imtbs-tsp.eu/~maigron/rir-stats/rir-delegations/delegations/ipv4/{country}-ipv4-delegations.html",
        "ipv6": "https://www-public.imtbs-tsp.eu/~maigron/rir-stats/rir-delegations/delegations/ipv6/{country}-ipv6-delegations.html",
    }

    HEADERS: dict[str, str] = {
        "User-Agent": "CountryNetworkScraper/1.0 (+https://github.com/yourusername/network-scraper)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    @staticmethod
    def fetch_data(
        country_code: str, data_type: str
    ) -> Tuple[str, str, Optional[List[Dict]], Optional[List[str]]]:
        """
        Fetch ASN, IPv4, or IPv6 data for a given country code.

        Args:
            country_code: Two-letter country code (e.g., 'FR', 'US')
            data_type: Type of data to fetch ('asn', 'ipv4', 'ipv6')

        Returns:
            Tuple containing:
            - country_code: The input country code
            - data_type: The input data type
            - data_rows: List of dictionaries with table data (None if error)
            - allocations: List of allocated resources (None if error)
        """
        url: str = DataFetcher.BASE_URLS[data_type].format(country=country_code.lower())

        try:
            # Fetch the HTML content
            response: requests.Response = requests.get(
                url=url,
                headers=DataFetcher.HEADERS,
                timeout=DEFAULT_TIMEOUT,
            )
            response.raise_for_status()

            # Parse the HTML
            soup = BeautifulSoup(response.text, "lxml")
            table: PageElement | None = soup.find(
                "table", attrs={"class": f"delegs {data_type} ripencc"}
            )

            if not table:
                console.log(
                    f"[yellow]No data table found for {data_type.upper()} in {country_code}[/yellow]"
                )
                return country_code, data_type, None, None

            # Process table headers and rows
            headers: list = [header.text.strip() for header in table.find_all("th")]
            rows: list[PageElement] = table.find_all("tr")[2:]  # Skip header rows

            data_rows: list = []
            allocations: list = []

            for row in rows:
                columns: list = [td.text.strip() for td in row.find_all("td")]
                if not columns:
                    continue

                row_data: dict = dict(zip(headers[1:], columns))
                data_rows.append(row_data)

                # Extract allocated resources based on data type
                if data_type == "asn" and columns[6] == "Allocated":
                    allocations.append(columns[3])  # ASN
                elif data_type in ["ipv4", "ipv6"] and columns[7] == "Allocated":
                    ip_with_prefix = f"{columns[3]}{columns[4].strip()}"
                    allocations.append(ip_with_prefix)

            return country_code, data_type, data_rows, allocations

        except RequestException as e:
            console.log(
                f"[red]Error fetching {data_type.upper()} data for {country_code}: {str(e)}[/red]"
            )
            return country_code, data_type, None, None
        except Exception as e:
            console.log(
                f"[red]Unexpected error processing {data_type.upper()} data for {country_code}: {str(e)}[/red]"
            )
            return country_code, data_type, None, None


def save_data(
    country_code: str, data_type: str, data_rows: List[Dict], allocations: List[str]
) -> None:
    """
    Save fetched data to appropriate files.

    Args:
        country_code: Two-letter country code
        data_type: Type of data ('asn', 'ipv4', 'ipv6')
        data_rows: List of dictionaries containing table data
        allocations: List of allocated resources
    """
    try:
        # Ensure output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Save detailed data to CSV
        if data_rows:
            csv_filename: str = os.path.join(
                OUTPUT_DIR, f"{country_code}_{data_type}_list.csv"
            )
            pd.DataFrame(data_rows).to_csv(csv_filename, index=False)
            console.log(
                f"[green]Saved {data_type.upper()} data for {country_code} to {csv_filename}[/green]"
            )

        # Save allocations to ranges file
        if allocations:
            range_file_path: str = os.path.join(OUTPUT_DIR, f"{data_type}_ranges.txt")
            with open(range_file_path, "a", encoding="utf-8") as range_file:
                range_file.write(",".join(allocations) + "\n")
            console.log(
                f"[green]Updated {data_type.upper()} ranges file with {country_code} data[/green]"
            )

    except (IOError, OSError) as e:
        console.log(
            f"[red]Error saving data for {country_code} {data_type}: {str(e)}[/red]"
        )
    except Exception as e:
        console.log(
            f"[red]Unexpected error saving data for {country_code} {data_type}: {str(e)}[/red]"
        )


def main() -> None:
    """Main execution function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Get AS numbers, IPv4, and/or IPv6 allocations of one or more countries"
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
    parser.add_argument(
        "--max-workers",
        type=int,
        default=MAX_WORKERS,
        help=f"Maximum number of concurrent workers (default: {MAX_WORKERS})",
    )
    args: argparse.Namespace = parser.parse_args()

    # Determine data types to fetch
    data_types: list[str] = (
        [args.data_type] if args.data_type != "all" else ["asn", "ipv4", "ipv6"]
    )

    console.log(
        f"[blue]Starting data fetch for {len(args.countries)} countries...[/blue]"
    )

    # Process data using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures: list = [
            executor.submit(DataFetcher.fetch_data, country, data_type)
            for country in args.countries
            for data_type in data_types
        ]

        for future in as_completed(futures):
            country_code, data_type, data_rows, allocations = future.result()
            if data_rows is not None:
                save_data(country_code, data_type, data_rows, allocations)

    console.log(
        f"[green]Completed fetching data for {len(args.countries)} countries.[/green]"
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.log("[yellow]Script interrupted by user. Exiting...[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.log(f"[red]Critical error: {str(e)}[/red]")
        sys.exit(1)
