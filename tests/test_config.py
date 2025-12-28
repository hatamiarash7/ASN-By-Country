"""Unit tests for the config module."""

from src.config import (
    BASE_URLS,
    DEFAULT_TIMEOUT,
    MAX_WORKERS,
    OUTPUT_DIR,
    REQUEST_HEADERS,
    VALID_DATA_TYPES,
)


class TestConfig:
    """Tests for configuration constants."""

    def test_default_timeout_is_positive(self) -> None:
        """Test that default timeout is a positive integer."""
        assert DEFAULT_TIMEOUT > 0
        assert isinstance(DEFAULT_TIMEOUT, int)

    def test_max_workers_is_positive(self) -> None:
        """Test that max workers is a positive integer."""
        assert MAX_WORKERS > 0
        assert isinstance(MAX_WORKERS, int)

    def test_output_dir_is_string(self) -> None:
        """Test that output directory is a string."""
        assert isinstance(OUTPUT_DIR, str)
        assert len(OUTPUT_DIR) > 0

    def test_base_urls_contains_all_types(self) -> None:
        """Test that base URLs contain all data types."""
        assert "asn" in BASE_URLS
        assert "ipv4" in BASE_URLS
        assert "ipv6" in BASE_URLS

    def test_base_urls_have_country_placeholder(self) -> None:
        """Test that base URLs contain country placeholder."""
        for data_type, url in BASE_URLS.items():
            assert "{country}" in url, f"URL for {data_type} missing country placeholder"

    def test_base_urls_are_https(self) -> None:
        """Test that all base URLs use HTTPS."""
        for data_type, url in BASE_URLS.items():
            assert url.startswith("https://"), f"URL for {data_type} should use HTTPS"

    def test_request_headers_has_user_agent(self) -> None:
        """Test that request headers include User-Agent."""
        assert "User-Agent" in REQUEST_HEADERS

    def test_request_headers_has_accept(self) -> None:
        """Test that request headers include Accept."""
        assert "Accept" in REQUEST_HEADERS

    def test_valid_data_types(self) -> None:
        """Test valid data types tuple."""
        assert "asn" in VALID_DATA_TYPES
        assert "ipv4" in VALID_DATA_TYPES
        assert "ipv6" in VALID_DATA_TYPES
        assert len(VALID_DATA_TYPES) == 3
