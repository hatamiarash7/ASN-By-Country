"""Web scraping functionality for ASN data."""

import requests
from bs4 import BeautifulSoup, Tag
from requests.exceptions import RequestException

from src.config import BASE_URLS, DEFAULT_TIMEOUT, REQUEST_HEADERS
from src.models import FetchResult


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

        headers = [header.text.strip() for header in table.find_all("th")]
        rows = table.find_all("tr")[2:]  # Skip header rows

        data_rows: list[dict] = []
        allocations: list[str] = []

        for row in rows:
            columns = [td.text.strip() for td in row.find_all("td")]
            if not columns:
                continue

            row_data = dict(zip(headers[1:], columns))
            data_rows.append(row_data)

            allocation: str | None = self._extract_allocation(columns, data_type)
            if allocation:
                allocations.append(allocation)

        return data_rows, allocations

    @staticmethod
    def _extract_allocation(columns: list[str], data_type: str) -> str | None:
        """
        Extract allocation from a row based on data type.

        Args:
            columns: List of column values.
            data_type: Type of data ('asn', 'ipv4', 'ipv6').

        Returns:
            Allocation string if allocated, None otherwise.
        """
        if data_type == "asn" and len(columns) > 6 and columns[6] == "Allocated":
            return columns[3]  # ASN
        elif data_type in ["ipv4", "ipv6"] and len(columns) > 7 and columns[7] == "Allocated":
            return f"{columns[3]}{columns[4].strip()}"
        return None
