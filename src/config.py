"""Configuration constants and settings."""

from typing import Final

# Network settings
DEFAULT_TIMEOUT: Final[int] = 10
MAX_WORKERS: Final[int] = 5

# Output settings
OUTPUT_DIR: Final[str] = "output_data"

# URL templates for data sources
BASE_URLS: Final[dict[str, str]] = {
    "asn": "https://www-public.imtbs-tsp.eu/~maigron/rir-stats/rir-delegations/delegations/asn/{country}-asn-delegations.html",
    "ipv4": "https://www-public.imtbs-tsp.eu/~maigron/rir-stats/rir-delegations/delegations/ipv4/{country}-ipv4-delegations.html",
    "ipv6": "https://www-public.imtbs-tsp.eu/~maigron/rir-stats/rir-delegations/delegations/ipv6/{country}-ipv6-delegations.html",
}

# HTTP headers for requests
REQUEST_HEADERS: Final[dict[str, str]] = {
    "User-Agent": "CountryNetworkScraper/1.0 (+https://github.com/hatamiarash7/ASN-By-Country)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Valid data types
VALID_DATA_TYPES: Final[tuple[str, ...]] = ("asn", "ipv4", "ipv6")
