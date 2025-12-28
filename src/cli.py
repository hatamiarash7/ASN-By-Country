"""Command-line interface for ASN-By-Country."""

import argparse
import sys
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich.console import Console

from src.config import MAX_WORKERS, VALID_DATA_TYPES
from src.models import FetchResult, ScraperStats
from src.scraper import DataFetcher
from src.storage import FileStorage

console = Console(log_path=False)


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="asn-by-country",
        description="Get AS numbers, IPv4, and/or IPv6 allocations for one or more countries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s FR US DE              Fetch ASN data for France, USA, and Germany
  %(prog)s IR --data-type all    Fetch all data types for Iran
  %(prog)s JP --data-type ipv4   Fetch only IPv4 data for Japan
        """,
    )
    parser.add_argument(
        "countries",
        nargs="+",
        metavar="COUNTRY",
        help="Two-letter country codes (e.g., 'FR', 'US', 'IR')",
    )
    parser.add_argument(
        "-d",
        "--data-type",
        choices=["asn", "ipv4", "ipv6", "all"],
        default="asn",
        help="Type of data to fetch (default: asn)",
    )
    parser.add_argument(
        "-w",
        "--max-workers",
        type=int,
        default=MAX_WORKERS,
        metavar="N",
        help=f"Maximum concurrent workers (default: {MAX_WORKERS})",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress progress output",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )
    return parser


def validate_country_codes(countries: Sequence[str]) -> list[str]:
    """
    Validate and normalize country codes.

    Args:
        countries: Sequence of country code strings.

    Returns:
        List of validated uppercase country codes.

    Raises:
        ValueError: If any country code is invalid.
    """
    validated: list[str] = []
    for code in countries:
        normalized = code.strip().upper()
        if len(normalized) != 2 or not normalized.isalpha():
            raise ValueError(f"Invalid country code: '{normalized}'. Must be 2 letters.")
        validated.append(normalized)
    return validated


def run_scraper(
    countries: list[str],
    data_types: list[str],
    max_workers: int,
    quiet: bool = False,
) -> ScraperStats:
    """
    Run the scraper with given parameters.

    Args:
        countries: List of country codes to scrape.
        data_types: List of data types to fetch.
        max_workers: Maximum number of concurrent workers.
        quiet: Suppress progress output.

    Returns:
        ScraperStats with operation statistics.
    """
    fetcher = DataFetcher()
    storage = FileStorage()
    stats = ScraperStats()

    # Clear existing ranges files for clean output
    for data_type in data_types:
        storage.clear_ranges_file(data_type)

    if not quiet:
        console.log(f"[blue]Starting data fetch for {len(countries)} countries...[/blue]")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures: dict = {
            executor.submit(fetcher.fetch, country, data_type): (country, data_type)
            for country in countries
            for data_type in data_types
        }

        for future in as_completed(futures):
            result: FetchResult = future.result()

            if result.is_success:
                storage.save(result)
                stats.record_success(result.country_code)
                if not quiet:
                    console.log(
                        f"[green]✓ {result.data_type.upper()} data saved for {result.country_code}[/green]"
                    )
            else:
                stats.record_failure(result.country_code)
                if not quiet:
                    console.log(f"[yellow]⚠ {result.error}[/yellow]")

    return stats


def main(argv: Sequence[str] | None = None) -> int:
    """
    Main entry point for CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    parser: argparse.ArgumentParser = create_parser()
    args: argparse.Namespace = parser.parse_args(argv)

    try:
        countries: list[str] = validate_country_codes(args.countries)
    except ValueError as e:
        console.log(f"[red]Error: {e}[/red]")
        return 1

    data_types: list[str] = list(VALID_DATA_TYPES) if args.data_type == "all" else [args.data_type]

    try:
        stats: ScraperStats = run_scraper(
            countries=countries,
            data_types=data_types,
            max_workers=args.max_workers,
            quiet=args.quiet,
        )

        if not args.quiet:
            console.log(
                f"[blue]Completed: {stats.successful_requests}/{stats.total_requests} "
                f"requests successful ({stats.success_rate:.1f}%)[/blue]"
            )

        return 0 if stats.failed_requests == 0 else 1

    except KeyboardInterrupt:
        console.log("[yellow]Interrupted by user.[/yellow]")
        return 130


def cli() -> None:
    """CLI entry point for package installation."""
    sys.exit(main())


if __name__ == "__main__":
    cli()
