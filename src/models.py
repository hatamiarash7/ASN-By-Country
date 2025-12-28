"""Data models for the application."""

from dataclasses import dataclass, field


@dataclass
class FetchResult:
    """Result of a data fetch operation."""

    country_code: str
    data_type: str
    data_rows: list[dict] | None = None
    allocations: list[str] | None = None
    error: str | None = None

    @property
    def is_success(self) -> bool:
        """Check if the fetch was successful."""
        return self.data_rows is not None and self.error is None

    @property
    def has_allocations(self) -> bool:
        """Check if allocations were found."""
        return bool(self.allocations)


@dataclass
class ScraperStats:
    """Statistics for scraping operations."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    countries_processed: set = field(default_factory=set)

    def record_success(self, country_code: str) -> None:
        """Record a successful request."""
        self.total_requests += 1
        self.successful_requests += 1
        self.countries_processed.add(country_code)

    def record_failure(self, country_code: str) -> None:
        """Record a failed request."""
        self.total_requests += 1
        self.failed_requests += 1
        self.countries_processed.add(country_code)

    @property
    def success_rate(self) -> float:
        """Calculate success rate as a percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
