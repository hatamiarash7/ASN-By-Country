"""Unit tests for the scraper module."""

from unittest.mock import Mock, patch

from requests.exceptions import ConnectionError, Timeout

from src.scraper import DataFetcher


class TestDataFetcher:
    """Tests for DataFetcher class."""

    def test_init_default_values(self) -> None:
        """Test initialization with default values."""
        fetcher = DataFetcher()
        assert fetcher.timeout == 10
        assert "User-Agent" in fetcher.headers

    def test_init_custom_values(self) -> None:
        """Test initialization with custom values."""
        custom_headers = {"User-Agent": "CustomAgent/1.0"}
        fetcher = DataFetcher(timeout=30, headers=custom_headers)
        assert fetcher.timeout == 30
        assert fetcher.headers == custom_headers

    @patch("src.scraper.requests.get")
    def test_fetch_success_asn(
        self, mock_get: Mock, sample_html_asn: str, mock_response: Mock
    ) -> None:
        """Test successful ASN fetch."""
        mock_response.text = sample_html_asn
        mock_get.return_value = mock_response

        fetcher = DataFetcher()
        result = fetcher.fetch("IR", "asn")

        assert result.is_success is True
        assert result.country_code == "IR"
        assert result.data_type == "asn"
        assert len(result.data_rows) == 3
        assert "AS12880" in result.allocations
        assert "AS25124" in result.allocations
        # AS99999 should NOT be in allocations (Reserved, not Allocated)
        assert "AS99999" not in result.allocations

    @patch("src.scraper.requests.get")
    def test_fetch_success_ipv4(
        self, mock_get: Mock, sample_html_ipv4: str, mock_response: Mock
    ) -> None:
        """Test successful IPv4 fetch."""
        mock_response.text = sample_html_ipv4
        mock_get.return_value = mock_response

        fetcher = DataFetcher()
        result = fetcher.fetch("IR", "ipv4")

        assert result.is_success is True
        assert len(result.data_rows) == 2
        assert "5.22.0.0/19" in result.allocations
        # 5.23.0.0/20 should NOT be in allocations (Reserved)
        assert "5.23.0.0/20" not in result.allocations

    @patch("src.scraper.requests.get")
    def test_fetch_no_table(
        self, mock_get: Mock, sample_html_no_table: str, mock_response: Mock
    ) -> None:
        """Test fetch when no table is found."""
        mock_response.text = sample_html_no_table
        mock_get.return_value = mock_response

        fetcher = DataFetcher()
        result = fetcher.fetch("XX", "asn")

        assert result.is_success is False
        assert "No data table found" in result.error

    @patch("src.scraper.requests.get")
    def test_fetch_connection_error(self, mock_get: Mock) -> None:
        """Test fetch with connection error."""
        mock_get.side_effect = ConnectionError("Failed to connect")

        fetcher = DataFetcher()
        result = fetcher.fetch("IR", "asn")

        assert result.is_success is False
        assert "Request error" in result.error

    @patch("src.scraper.requests.get")
    def test_fetch_timeout(self, mock_get: Mock) -> None:
        """Test fetch with timeout."""
        mock_get.side_effect = Timeout("Request timed out")

        fetcher = DataFetcher()
        result = fetcher.fetch("IR", "asn")

        assert result.is_success is False
        assert "Request error" in result.error

    @patch("src.scraper.requests.get")
    def test_fetch_uses_lowercase_country_code(
        self, mock_get: Mock, sample_html_asn: str, mock_response: Mock
    ) -> None:
        """Test that country code is converted to lowercase in URL."""
        mock_response.text = sample_html_asn
        mock_get.return_value = mock_response

        fetcher = DataFetcher()
        fetcher.fetch("IR", "asn")

        call_args = mock_get.call_args
        assert "ir-asn-delegations" in call_args.kwargs["url"]

    def test_extract_allocation_asn(self) -> None:
        """Test allocation extraction for ASN data."""
        columns = ["1", "ripencc", "IR", "AS12880", "DCI", "2003-01-01", "Allocated"]
        result = DataFetcher._extract_allocation(columns, "asn")
        assert result == "AS12880"

    def test_extract_allocation_asn_not_allocated(self) -> None:
        """Test allocation extraction for non-allocated ASN."""
        columns = ["1", "ripencc", "IR", "AS99999", "Test", "2003-01-01", "Reserved"]
        result = DataFetcher._extract_allocation(columns, "asn")
        assert result is None

    def test_extract_allocation_ipv4(self) -> None:
        """Test allocation extraction for IPv4 data."""
        columns = ["1", "ripencc", "IR", "5.22.0.0", "/19", "8192", "2012-01-01", "Allocated"]
        result = DataFetcher._extract_allocation(columns, "ipv4")
        assert result == "5.22.0.0/19"

    def test_extract_allocation_ipv6(self) -> None:
        """Test allocation extraction for IPv6 data."""
        columns = ["1", "ripencc", "IR", "2001:db8::", "/32", "1", "2012-01-01", "Allocated"]
        result = DataFetcher._extract_allocation(columns, "ipv6")
        assert result == "2001:db8::/32"

    def test_extract_allocation_short_columns(self) -> None:
        """Test allocation extraction with insufficient columns."""
        columns = ["1", "ripencc"]
        result = DataFetcher._extract_allocation(columns, "asn")
        assert result is None
