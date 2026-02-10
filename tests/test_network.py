"""Unit tests for the network utility module."""

import pytest

from src.network import ip_range_to_cidrs


class TestIpRangeToCidrs:
    """Tests for ip_range_to_cidrs function."""

    def test_single_cidr(self) -> None:
        """Test range that maps to exactly one CIDR block."""
        result = ip_range_to_cidrs("192.168.0.0", "192.168.0.255")
        assert result == ["192.168.0.0/24"]

    def test_aggreg_768_addresses(self) -> None:
        """Test 768-address range from real data (91.237.254.0 - 91.238.0.255)."""
        result = ip_range_to_cidrs("91.237.254.0", "91.238.0.255")
        assert result == ["91.237.254.0/23", "91.238.0.0/24"]

    def test_aggreg_768_addresses_second(self) -> None:
        """Test 768-address range from real data (194.33.125.0 - 194.33.127.255)."""
        result = ip_range_to_cidrs("194.33.125.0", "194.33.127.255")
        assert result == ["194.33.125.0/24", "194.33.126.0/23"]

    def test_aggreg_88_range(self) -> None:
        """Test 768-address range from real data (88.135.33.0 - 88.135.35.255)."""
        result = ip_range_to_cidrs("88.135.33.0", "88.135.35.255")
        assert result == ["88.135.33.0/24", "88.135.34.0/23"]

    def test_single_host(self) -> None:
        """Test range covering a single IP address."""
        result = ip_range_to_cidrs("10.0.0.1", "10.0.0.1")
        assert result == ["10.0.0.1/32"]

    def test_large_range(self) -> None:
        """Test a larger range that decomposes into multiple CIDRs."""
        result = ip_range_to_cidrs("10.0.0.0", "10.0.2.255")
        assert result == ["10.0.0.0/23", "10.0.2.0/24"]

    def test_whitespace_handling(self) -> None:
        """Test that leading/trailing whitespace is stripped."""
        result = ip_range_to_cidrs("  192.168.0.0  ", "  192.168.0.255  ")
        assert result == ["192.168.0.0/24"]

    def test_invalid_first_ip(self) -> None:
        """Test with an invalid first IP address."""
        with pytest.raises(ValueError):
            ip_range_to_cidrs("invalid", "192.168.0.255")

    def test_invalid_last_ip(self) -> None:
        """Test with an invalid last IP address."""
        with pytest.raises(ValueError):
            ip_range_to_cidrs("192.168.0.0", "invalid")

    def test_first_greater_than_last(self) -> None:
        """Test error when first IP is greater than last IP."""
        with pytest.raises(ValueError):
            ip_range_to_cidrs("192.168.1.0", "192.168.0.0")

    def test_full_class_c(self) -> None:
        """Test a full /24 range."""
        result = ip_range_to_cidrs("10.10.10.0", "10.10.10.255")
        assert result == ["10.10.10.0/24"]

    def test_two_adjacent_class_c(self) -> None:
        """Test two adjacent /24 blocks forming a /23."""
        result = ip_range_to_cidrs("10.10.0.0", "10.10.1.255")
        assert result == ["10.10.0.0/23"]
