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
        assert result.data_rows is not None
        assert len(result.data_rows) == 3
        assert result.allocations is not None
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
        assert result.data_rows is not None
        assert len(result.data_rows) == 2
        assert result.allocations is not None
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
        assert result.error is not None
        assert "No data table found" in result.error

    @patch("src.scraper.requests.get")
    def test_fetch_connection_error(self, mock_get: Mock) -> None:
        """Test fetch with connection error."""
        mock_get.side_effect = ConnectionError("Failed to connect")

        fetcher = DataFetcher()
        result = fetcher.fetch("IR", "asn")

        assert result.is_success is False
        assert result.error is not None
        assert "Request error" in result.error

    @patch("src.scraper.requests.get")
    def test_fetch_timeout(self, mock_get: Mock) -> None:
        """Test fetch with timeout."""
        mock_get.side_effect = Timeout("Request timed out")

        fetcher = DataFetcher()
        result = fetcher.fetch("IR", "asn")

        assert result.is_success is False
        assert result.error is not None
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
        columns = ["RIPE NCC", "IR", "ASN", "AS12880", "1", "2003-01-01", "Allocated"]
        result = DataFetcher._extract_allocation(columns, "asn")
        assert result == ["AS12880"]

    def test_extract_allocation_asn_not_allocated(self) -> None:
        """Test allocation extraction for non-allocated ASN."""
        columns = ["RIPE NCC", "IR", "ASN", "AS99999", "1", "2003-01-01", "Reserved"]
        result = DataFetcher._extract_allocation(columns, "asn")
        assert result is None

    def test_extract_allocation_ipv4(self) -> None:
        """Test allocation extraction for IPv4 data."""
        columns = [
            "RIPE NCC",
            "IR",
            "IPv4",
            "5.22.0.0",
            "5.22.7.255",
            "/19",
            "8192",
            "2012-01-01",
            "Allocated",
        ]
        result = DataFetcher._extract_allocation(columns, "ipv4")
        assert result == ["5.22.0.0/19"]

    def test_extract_allocation_ipv4_assigned(self) -> None:
        """Test allocation extraction for Assigned IPv4 data."""
        columns = [
            "RIPE NCC",
            "IR",
            "IPv4",
            "88.135.32.0",
            "88.135.32.255",
            "/24",
            "256",
            "2009-11-16",
            "Assigned",
        ]
        result = DataFetcher._extract_allocation(columns, "ipv4")
        assert result == ["88.135.32.0/24"]

    def test_extract_allocation_ipv4_aggreg(self) -> None:
        """Test allocation extraction for Aggreg prefix (91.237.254.0 - 91.238.0.255 = /23 + /24)."""
        columns = [
            "RIPE NCC",
            "IR",
            "IPv4",
            "91.237.254.0",
            "91.238.0.255",
            "Aggreg",
            "768",
            "2012-04-03",
            "Assigned",
        ]
        result = DataFetcher._extract_allocation(columns, "ipv4")
        assert result is not None
        assert "91.237.254.0/23" in result
        assert "91.238.0.0/24" in result
        assert len(result) == 2

    def test_extract_allocation_ipv4_aggreg_another(self) -> None:
        """Test allocation extraction for another Aggreg prefix (194.33.125.0 - 194.33.127.255)."""
        columns = [
            "RIPE NCC",
            "IR",
            "IPv4",
            "194.33.125.0",
            "194.33.127.255",
            "Aggreg",
            "768",
            "2012-06-04",
            "Assigned",
        ]
        result = DataFetcher._extract_allocation(columns, "ipv4")
        assert result is not None
        assert "194.33.125.0/24" in result
        assert "194.33.126.0/23" in result
        assert len(result) == 2

    def test_extract_allocation_ipv6(self) -> None:
        """Test allocation extraction for IPv6 data."""
        columns = [
            "RIPE NCC",
            "IR",
            "IPv6",
            "2001:db8::",
            "2001:db8:ffff:ffff:ffff:ffff:ffff:ffff",
            "/32",
            "1",
            "2012-01-01",
            "Allocated",
        ]
        result = DataFetcher._extract_allocation(columns, "ipv6")
        assert result == ["2001:db8::/32"]

    def test_extract_allocation_short_columns(self) -> None:
        """Test allocation extraction with insufficient columns."""
        columns = ["RIPE NCC", "IR"]
        result = DataFetcher._extract_allocation(columns, "asn")
        assert result is None

    @patch("src.scraper.requests.get")
    def test_fetch_ipv4_aggreg(
        self, mock_get: Mock, sample_html_ipv4_aggreg: str, mock_response: Mock
    ) -> None:
        """Test successful IPv4 fetch with Aggreg prefixes."""
        mock_response.text = sample_html_ipv4_aggreg
        mock_get.return_value = mock_response

        fetcher = DataFetcher()
        result = fetcher.fetch("IR", "ipv4")

        assert result.is_success is True
        assert result.data_rows is not None
        assert len(result.data_rows) == 3
        assert result.allocations is not None
        # Normal /24 row
        assert "88.135.32.0/24" in result.allocations
        # Aggreg row: 91.237.254.0 - 91.238.0.255 → /23 + /24
        assert "91.237.254.0/23" in result.allocations
        assert "91.238.0.0/24" in result.allocations
        # Aggreg row: 194.33.125.0 - 194.33.127.255 → /24 + /23
        assert "194.33.125.0/24" in result.allocations
        assert "194.33.126.0/23" in result.allocations


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @patch("src.scraper.requests.get")
    def test_fetch_unexpected_exception(self, mock_get: Mock) -> None:
        """Test fetch handles unexpected exceptions."""
        mock_get.side_effect = RuntimeError("Unexpected error")

        fetcher = DataFetcher()
        result = fetcher.fetch("IR", "asn")

        assert result.is_success is False
        assert result.error is not None
        assert "Unexpected error" in result.error

    def test_extract_allocation_ipv4_aggreg_invalid_range(self) -> None:
        """Test allocation extraction with invalid IP range for Aggreg."""
        columns = [
            "RIPE NCC",
            "IR",
            "IPv4",
            "invalid_ip",
            "also_invalid",
            "Aggreg",
            "768",
            "2012-04-03",
            "Assigned",
        ]
        result = DataFetcher._extract_allocation(columns, "ipv4")
        assert result is None

    def test_extract_allocation_ipv4_aggreg_reversed_range(self) -> None:
        """Test allocation extraction with reversed IP range (start > end)."""
        columns = [
            "RIPE NCC",
            "IR",
            "IPv4",
            "192.168.1.255",  # Higher than end
            "192.168.1.0",  # Lower than start
            "Aggreg",
            "768",
            "2012-04-03",
            "Assigned",
        ]
        result = DataFetcher._extract_allocation(columns, "ipv4")
        # ip_range_to_cidrs should raise ValueError for reversed range
        assert result is None

    @patch("src.scraper.requests.get")
    def test_fetch_table_with_empty_rows(self, mock_get: Mock, mock_response: Mock) -> None:
        """Test fetch handles table with empty rows."""
        # HTML with a table that has an empty row (no <td> elements)
        html_with_empty_row = """
        <html>
        <body>
        <table class="delegs asn ripencc">
            <tr><th>Zone</th><th>Country</th><th>Type</th><th>Range</th><th>Num</th><th>Date</th><th>Status</th></tr>
            <tr><th></th><th></th><th></th><th></th><th></th><th></th><th></th></tr>
            <tr></tr>
            <tr>
                <td>RIPE NCC</td><td>IR</td><td>ASN</td><td>AS12880</td>
                <td>1</td><td>2003-01-01</td><td>Allocated</td>
            </tr>
        </table>
        </body>
        </html>
        """
        mock_response.text = html_with_empty_row
        mock_get.return_value = mock_response

        fetcher = DataFetcher()
        result = fetcher.fetch("IR", "asn")

        assert result.is_success is True
        assert result.data_rows is not None
        # Should only have one valid row
        assert len(result.data_rows) == 1
        assert result.allocations is not None
        assert "AS12880" in result.allocations

    def test_extract_allocation_ipv6_not_allocated(self) -> None:
        """Test allocation extraction for non-allocated IPv6."""
        columns = [
            "RIPE NCC",
            "IR",
            "IPv6",
            "2001:db8::",
            "2001:db8:ffff:ffff:ffff:ffff:ffff:ffff",
            "/32",
            "1",
            "2012-01-01",
            "Reserved",
        ]
        result = DataFetcher._extract_allocation(columns, "ipv6")
        assert result is None

    def test_extract_allocation_ipv4_reserved(self) -> None:
        """Test that Reserved status is excluded."""
        columns = [
            "RIPE NCC",
            "IR",
            "IPv4",
            "10.0.0.0",
            "10.255.255.255",
            "/8",
            "16777216",
            "2000-01-01",
            "Reserved",
        ]
        result = DataFetcher._extract_allocation(columns, "ipv4")
        assert result is None

    def test_extract_allocation_unknown_data_type(self) -> None:
        """Test allocation extraction with unknown data type."""
        columns = [
            "RIPE NCC",
            "IR",
            "Unknown",
            "value1",
            "value2",
            "value3",
            "value4",
            "value5",
            "Allocated",
        ]
        result = DataFetcher._extract_allocation(columns, "unknown")
        assert result is None

    @patch("src.scraper.requests.get")
    def test_fetch_http_error(self, mock_get: Mock, mock_response: Mock) -> None:
        """Test fetch handles HTTP errors."""
        from requests.exceptions import HTTPError

        mock_get.side_effect = HTTPError("404 Not Found")

        fetcher = DataFetcher()
        result = fetcher.fetch("XX", "asn")

        assert result.is_success is False
        assert result.error is not None
        assert "Request error" in result.error
