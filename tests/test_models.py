"""Unit tests for the models module."""

from src.models import FetchResult, ScraperStats


class TestFetchResult:
    """Tests for FetchResult dataclass."""

    def test_successful_result(self) -> None:
        """Test a successful fetch result."""
        result = FetchResult(
            country_code="IR",
            data_type="asn",
            data_rows=[{"ASN": "AS12880"}],
            allocations=["AS12880"],
        )
        assert result.is_success is True
        assert result.has_allocations is True
        assert result.error is None

    def test_failed_result(self) -> None:
        """Test a failed fetch result."""
        result = FetchResult(
            country_code="XX",
            data_type="asn",
            error="Connection failed",
        )
        assert result.is_success is False
        assert result.has_allocations is False

    def test_result_without_allocations(self) -> None:
        """Test result with data but no allocations."""
        result = FetchResult(
            country_code="IR",
            data_type="asn",
            data_rows=[{"ASN": "AS99999"}],
            allocations=[],
        )
        assert result.is_success is True
        assert result.has_allocations is False

    def test_result_with_none_allocations(self) -> None:
        """Test result with None allocations."""
        result = FetchResult(
            country_code="IR",
            data_type="asn",
            data_rows=[{"ASN": "AS99999"}],
            allocations=None,
        )
        assert result.has_allocations is False


class TestScraperStats:
    """Tests for ScraperStats dataclass."""

    def test_initial_state(self) -> None:
        """Test initial state of stats."""
        stats = ScraperStats()
        assert stats.total_requests == 0
        assert stats.successful_requests == 0
        assert stats.failed_requests == 0
        assert len(stats.countries_processed) == 0

    def test_record_success(self) -> None:
        """Test recording successful requests."""
        stats = ScraperStats()
        stats.record_success("IR")
        stats.record_success("US")

        assert stats.total_requests == 2
        assert stats.successful_requests == 2
        assert stats.failed_requests == 0
        assert stats.countries_processed == {"IR", "US"}

    def test_record_failure(self) -> None:
        """Test recording failed requests."""
        stats = ScraperStats()
        stats.record_failure("XX")

        assert stats.total_requests == 1
        assert stats.successful_requests == 0
        assert stats.failed_requests == 1
        assert "XX" in stats.countries_processed

    def test_success_rate_empty(self) -> None:
        """Test success rate with no requests."""
        stats = ScraperStats()
        assert stats.success_rate == 0.0

    def test_success_rate_all_success(self) -> None:
        """Test success rate with all successful requests."""
        stats = ScraperStats()
        stats.record_success("IR")
        stats.record_success("US")
        assert stats.success_rate == 100.0

    def test_success_rate_mixed(self) -> None:
        """Test success rate with mixed results."""
        stats = ScraperStats()
        stats.record_success("IR")
        stats.record_success("US")
        stats.record_failure("XX")
        stats.record_failure("YY")

        assert stats.success_rate == 50.0

    def test_same_country_multiple_times(self) -> None:
        """Test that same country is not duplicated in set."""
        stats = ScraperStats()
        stats.record_success("IR")
        stats.record_success("IR")
        stats.record_success("IR")

        assert stats.total_requests == 3
        assert len(stats.countries_processed) == 1
