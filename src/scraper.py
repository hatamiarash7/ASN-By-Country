"""Web scraping functionality for ASN data."""

import logging

import requests
from bs4 import BeautifulSoup, Tag
from requests.exceptions import RequestException

from src.config import BASE_URLS, DEFAULT_TIMEOUT, REQUEST_HEADERS
from src.models import FetchResult
from src.network import ip_range_to_cidrs

logger: logging.Logger = logging.getLogger(__name__)


class DataFetcher:
    """Handles fetching and processing of country network data."""

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        headers: dict[str, str] | None = None,
    ) -> None:
        """
        Initialize the DataFetcher.

        Args:
            timeout: Request timeout in seconds.
            headers: Optional custom headers for requests.
        """
        self.timeout: int = timeout
        self.headers: dict[str, str] = headers or REQUEST_HEADERS

    def fetch(self, country_code: str, data_type: str) -> FetchResult:
        """
        Fetch ASN, IPv4, or IPv6 data for a given country code.

        Args:
            country_code: Two-letter country code (e.g., 'FR', 'US').
            data_type: Type of data to fetch ('asn', 'ipv4', 'ipv6').

        Returns:
            FetchResult containing the fetched data or error information.
        """
        url: str = BASE_URLS[data_type].format(country=country_code.lower())

        try:
            response: requests.Response = requests.get(
                url=url,
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data_rows, allocations = self._parse_response(response.text, data_type)

            if data_rows is None:
                return FetchResult(
                    country_code=country_code,
                    data_type=data_type,
                    error=f"No data table found for {data_type.upper()} in {country_code}",
                )

            return FetchResult(
                country_code=country_code,
                data_type=data_type,
                data_rows=data_rows,
                allocations=allocations,
            )

        except RequestException as e:
            return FetchResult(
                country_code=country_code,
                data_type=data_type,
                error=f"Request error: {e!s}",
            )
        except Exception as e:
            return FetchResult(
                country_code=country_code,
                data_type=data_type,
                error=f"Unexpected error: {e!s}",
            )

    def _parse_response(
        self, html_content: str, data_type: str
    ) -> tuple[list[dict] | None, list[str] | None]:
        """
        Parse HTML response and extract data.

        Args:
            html_content: Raw HTML content.
            data_type: Type of data being parsed.

        Returns:
            Tuple of (data_rows, allocations) or (None, None) if parsing fails.
        """
        soup = BeautifulSoup(html_content, "lxml")
        table = soup.find("table", attrs={"class": f"delegs {data_type} ripencc"})

        if not table or not isinstance(table, Tag):
            return None, None

        headers: list[str] = [header.text.strip() for header in table.find_all("th")]
        rows = table.find_all("tr")[2:]  # Skip header rows

        data_rows: list[dict[str, str]] = []
        allocations: list[str] = []

        for row in rows:
            columns: list[str] = [td.text.strip() for td in row.find_all("td")]
            if not columns:
                continue

            row_data: dict[str, str] = dict(zip(headers[1:], columns))
            data_rows.append(row_data)

            extracted: list[str] | None = self._extract_allocation(columns, data_type)
            if extracted:
                allocations.extend(extracted)

        return data_rows, allocations

    @staticmethod
    def _extract_allocation(columns: list[str], data_type: str) -> list[str] | None:
        """
        Extract allocation(s) from a row based on data type.

        The real website tables have these column layouts:
        - ASN (7 cols): Zone, Country, Parameter, Range, Number, Date, Status
        - IPv4 (9 cols): Zone, Country, Parameter, First, Last, Prefix, Number, Date, Status
        - IPv6 (9 cols): Zone, Country, Parameter, First, Last, Prefix, Number, Date, Status

        When the Prefix column contains "Aggreg" instead of a CIDR prefix,
        the delegation covers a non-CIDR-aligned range. In this case, we
        decompose the First-Last range into minimal covering CIDR subnets.

        Args:
            columns: List of column values from the table row.
            data_type: Type of data ('asn', 'ipv4', 'ipv6').

        Returns:
            List of allocation strings if allocated/assigned, None otherwise.
        """
        if data_type == "asn" and len(columns) > 6 and columns[6] == "Allocated":
            return [columns[3]]

        if data_type in ("ipv4", "ipv6") and len(columns) > 8:
            status: str = columns[8].strip()
            if status not in ("Allocated", "Assigned"):
                return None

            prefix: str = columns[5].strip()
            first_ip: str = columns[3].strip()

            if prefix.lower() == "aggreg":
                last_ip: str = columns[4].strip()
                try:
                    return ip_range_to_cidrs(first_ip, last_ip)
                except ValueError:
                    logger.warning(
                        "Failed to compute CIDRs for range %s - %s",
                        first_ip,
                        last_ip,
                    )
                    return None

            return [f"{first_ip}{prefix}"]

        return None
