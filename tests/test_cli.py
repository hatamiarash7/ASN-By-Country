"""Unit tests for the CLI module."""

from unittest.mock import MagicMock, patch

import pytest

from src.cli import cli, create_parser, main, run_scraper, validate_country_codes
from src.models import FetchResult


class TestCreateParser:
    """Tests for argument parser creation."""

    def test_parser_creation(self) -> None:
        """Test that parser is created successfully."""
        parser = create_parser()
        assert parser is not None

    def test_parser_required_countries(self) -> None:
        """Test that countries argument is required."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_parser_single_country(self) -> None:
        """Test parsing single country."""
        parser = create_parser()
        args = parser.parse_args(["IR"])
        assert args.countries == ["IR"]

    def test_parser_multiple_countries(self) -> None:
        """Test parsing multiple countries."""
        parser = create_parser()
        args = parser.parse_args(["IR", "US", "DE"])
        assert args.countries == ["IR", "US", "DE"]

    def test_parser_default_data_type(self) -> None:
        """Test default data type is 'asn'."""
        parser = create_parser()
        args = parser.parse_args(["IR"])
        assert args.data_type == "asn"

    def test_parser_data_type_options(self) -> None:
        """Test all data type options."""
        parser = create_parser()

        for data_type in ["asn", "ipv4", "ipv6", "all"]:
            args = parser.parse_args(["IR", "--data-type", data_type])
            assert args.data_type == data_type

    def test_parser_short_data_type_flag(self) -> None:
        """Test short -d flag for data type."""
        parser = create_parser()
        args = parser.parse_args(["IR", "-d", "ipv4"])
        assert args.data_type == "ipv4"

    def test_parser_default_max_workers(self) -> None:
        """Test default max workers value."""
        parser = create_parser()
        args = parser.parse_args(["IR"])
        assert args.max_workers == 5

    def test_parser_custom_max_workers(self) -> None:
        """Test custom max workers value."""
        parser = create_parser()
        args = parser.parse_args(["IR", "--max-workers", "10"])
        assert args.max_workers == 10

    def test_parser_short_max_workers_flag(self) -> None:
        """Test short -w flag for max workers."""
        parser = create_parser()
        args = parser.parse_args(["IR", "-w", "3"])
        assert args.max_workers == 3

    def test_parser_quiet_flag(self) -> None:
        """Test quiet flag."""
        parser = create_parser()
        args = parser.parse_args(["IR", "--quiet"])
        assert args.quiet is True

    def test_parser_short_quiet_flag(self) -> None:
        """Test short -q flag."""
        parser = create_parser()
        args = parser.parse_args(["IR", "-q"])
        assert args.quiet is True

    def test_parser_invalid_data_type(self) -> None:
        """Test invalid data type raises error."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["IR", "--data-type", "invalid"])


class TestValidateCountryCodes:
    """Tests for country code validation."""

    def test_valid_uppercase_codes(self) -> None:
        """Test valid uppercase country codes."""
        codes = validate_country_codes(["IR", "US", "DE"])
        assert codes == ["IR", "US", "DE"]

    def test_valid_lowercase_codes(self) -> None:
        """Test that lowercase codes are uppercased."""
        codes = validate_country_codes(["ir", "us", "de"])
        assert codes == ["IR", "US", "DE"]

    def test_valid_mixed_case_codes(self) -> None:
        """Test that mixed case codes are uppercased."""
        codes = validate_country_codes(["Ir", "uS", "De"])
        assert codes == ["IR", "US", "DE"]

    def test_codes_with_whitespace(self) -> None:
        """Test that whitespace is stripped."""
        codes = validate_country_codes(["  IR  ", " US", "DE "])
        assert codes == ["IR", "US", "DE"]

    def test_invalid_single_letter(self) -> None:
        """Test that single letter codes are rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_country_codes(["A"])
        assert "Invalid country code" in str(exc_info.value)

    def test_invalid_three_letters(self) -> None:
        """Test that three letter codes are rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_country_codes(["IRN"])
        assert "Invalid country code" in str(exc_info.value)

    def test_invalid_numeric_code(self) -> None:
        """Test that numeric codes are rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_country_codes(["12"])
        assert "Invalid country code" in str(exc_info.value)

    def test_invalid_alphanumeric_code(self) -> None:
        """Test that alphanumeric codes are rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_country_codes(["I1"])
        assert "Invalid country code" in str(exc_info.value)

    def test_empty_list(self) -> None:
        """Test empty list returns empty list."""
        codes = validate_country_codes([])
        assert codes == []

    def test_first_invalid_stops_validation(self) -> None:
        """Test that validation stops at first invalid code."""
        with pytest.raises(ValueError) as exc_info:
            validate_country_codes(["IR", "INVALID", "US"])
        assert "INVALID" in str(exc_info.value)


class TestRunScraper:
    """Tests for run_scraper function."""

    @patch("src.cli.DataFetcher")
    @patch("src.cli.FileStorage")
    @patch("src.cli.MikroTikExporter")
    def test_run_scraper_success(
        self, mock_mikrotik: MagicMock, mock_storage: MagicMock, mock_fetcher: MagicMock
    ) -> None:
        """Test successful scraping run."""
        mock_fetcher_instance = mock_fetcher.return_value
        mock_fetcher_instance.fetch.return_value = FetchResult(
            country_code="IR",
            data_type="asn",
            data_rows=[{"ASN": "AS12880"}],
            allocations=["AS12880"],
        )

        mock_storage_instance = mock_storage.return_value
        mock_storage_instance.output_dir = "/tmp/output"

        stats = run_scraper(
            countries=["IR"],
            data_types=["asn"],
            max_workers=1,
            quiet=True,
        )

        assert stats.successful_requests == 1
        assert stats.failed_requests == 0
        assert stats.total_requests == 1
        assert mock_storage_instance.save.called

    @patch("src.cli.DataFetcher")
    @patch("src.cli.FileStorage")
    def test_run_scraper_failure(self, mock_storage: MagicMock, mock_fetcher: MagicMock) -> None:
        """Test scraping run with failure."""
        mock_fetcher_instance = mock_fetcher.return_value
        mock_fetcher_instance.fetch.return_value = FetchResult(
            country_code="XX",
            data_type="asn",
            error="Country not found",
        )

        mock_storage_instance = mock_storage.return_value
        mock_storage_instance.output_dir = "/tmp/output"

        stats = run_scraper(
            countries=["XX"],
            data_types=["asn"],
            max_workers=1,
            quiet=True,
        )

        assert stats.successful_requests == 0
        assert stats.failed_requests == 1
        assert not mock_storage_instance.save.called

    @patch("src.cli.DataFetcher")
    @patch("src.cli.FileStorage")
    @patch("src.cli.MikroTikExporter")
    def test_run_scraper_ipv4_exports_rsc(
        self, mock_mikrotik: MagicMock, mock_storage: MagicMock, mock_fetcher: MagicMock
    ) -> None:
        """Test that IPv4 data triggers RSC export."""
        mock_fetcher_instance = mock_fetcher.return_value
        mock_fetcher_instance.fetch.return_value = FetchResult(
            country_code="IR",
            data_type="ipv4",
            data_rows=[{"First": "5.22.0.0", "Prefix": "/19"}],
            allocations=["5.22.0.0/19"],
        )

        mock_storage_instance = mock_storage.return_value
        mock_storage_instance.output_dir = "/tmp/output"

        mock_mikrotik_instance = mock_mikrotik.return_value

        stats = run_scraper(
            countries=["IR"],
            data_types=["ipv4"],
            max_workers=1,
            quiet=True,
        )

        assert stats.successful_requests == 1
        assert mock_mikrotik_instance.export.called

    @patch("src.cli.DataFetcher")
    @patch("src.cli.FileStorage")
    def test_run_scraper_asn_no_rsc_export(
        self, mock_storage: MagicMock, mock_fetcher: MagicMock
    ) -> None:
        """Test that ASN data does not trigger RSC export."""
        mock_fetcher_instance = mock_fetcher.return_value
        mock_fetcher_instance.fetch.return_value = FetchResult(
            country_code="IR",
            data_type="asn",
            data_rows=[{"ASN": "AS12880"}],
            allocations=["AS12880"],
        )

        mock_storage_instance = mock_storage.return_value
        mock_storage_instance.output_dir = "/tmp/output"

        stats = run_scraper(
            countries=["IR"],
            data_types=["asn"],
            max_workers=1,
            quiet=True,
        )

        assert stats.successful_requests == 1

    @patch("src.cli.DataFetcher")
    @patch("src.cli.FileStorage")
    @patch("src.cli.MikroTikExporter")
    def test_run_scraper_multiple_countries(
        self, mock_mikrotik: MagicMock, mock_storage: MagicMock, mock_fetcher: MagicMock
    ) -> None:
        """Test scraping multiple countries."""
        mock_fetcher_instance = mock_fetcher.return_value
        mock_fetcher_instance.fetch.side_effect = [
            FetchResult(
                country_code="IR",
                data_type="asn",
                data_rows=[{"ASN": "AS12880"}],
                allocations=["AS12880"],
            ),
            FetchResult(
                country_code="US",
                data_type="asn",
                data_rows=[{"ASN": "AS3356"}],
                allocations=["AS3356"],
            ),
        ]

        mock_storage_instance = mock_storage.return_value
        mock_storage_instance.output_dir = "/tmp/output"

        stats = run_scraper(
            countries=["IR", "US"],
            data_types=["asn"],
            max_workers=2,
            quiet=True,
        )

        assert stats.successful_requests == 2
        assert stats.failed_requests == 0

    @patch("src.cli.DataFetcher")
    @patch("src.cli.FileStorage")
    def test_run_scraper_clears_ranges_files(
        self, mock_storage: MagicMock, mock_fetcher: MagicMock
    ) -> None:
        """Test that ranges files are cleared before scraping."""
        mock_fetcher_instance = mock_fetcher.return_value
        mock_fetcher_instance.fetch.return_value = FetchResult(
            country_code="IR",
            data_type="asn",
            data_rows=[{"ASN": "AS12880"}],
            allocations=["AS12880"],
        )

        mock_storage_instance = mock_storage.return_value
        mock_storage_instance.output_dir = "/tmp/output"

        run_scraper(
            countries=["IR"],
            data_types=["asn"],
            max_workers=1,
            quiet=True,
        )

        mock_storage_instance.clear_ranges_file.assert_called_with("asn")


class TestMain:
    """Tests for main function."""

    @patch("src.cli.run_scraper")
    def test_main_success(self, mock_run_scraper: MagicMock) -> None:
        """Test successful main execution."""
        from src.models import ScraperStats

        mock_stats = ScraperStats()
        mock_stats.record_success("IR")
        mock_run_scraper.return_value = mock_stats

        exit_code = main(["IR", "-q"])

        assert exit_code == 0
        mock_run_scraper.assert_called_once()

    @patch("src.cli.run_scraper")
    def test_main_with_failures_returns_1(self, mock_run_scraper: MagicMock) -> None:
        """Test main returns 1 when there are failures."""
        from src.models import ScraperStats

        mock_stats = ScraperStats()
        mock_stats.record_failure("XX")
        mock_run_scraper.return_value = mock_stats

        exit_code = main(["XX", "-q"])

        assert exit_code == 1

    def test_main_invalid_country_code(self) -> None:
        """Test main with invalid country code."""
        exit_code = main(["INVALID", "-q"])

        assert exit_code == 1

    @patch("src.cli.run_scraper")
    def test_main_all_data_types(self, mock_run_scraper: MagicMock) -> None:
        """Test main with 'all' data type."""
        from src.models import ScraperStats

        mock_stats = ScraperStats()
        mock_run_scraper.return_value = mock_stats

        main(["IR", "-d", "all", "-q"])

        call_args = mock_run_scraper.call_args
        assert set(call_args.kwargs["data_types"]) == {"asn", "ipv4", "ipv6"}

    @patch("src.cli.run_scraper")
    def test_main_custom_max_workers(self, mock_run_scraper: MagicMock) -> None:
        """Test main with custom max workers."""
        from src.models import ScraperStats

        mock_stats = ScraperStats()
        mock_run_scraper.return_value = mock_stats

        main(["IR", "-w", "10", "-q"])

        call_args = mock_run_scraper.call_args
        assert call_args.kwargs["max_workers"] == 10

    @patch("src.cli.run_scraper")
    def test_main_keyboard_interrupt(self, mock_run_scraper: MagicMock) -> None:
        """Test main handles KeyboardInterrupt."""
        mock_run_scraper.side_effect = KeyboardInterrupt()

        exit_code = main(["IR", "-q"])

        assert exit_code == 130


class TestCli:
    """Tests for cli entry point."""

    @patch("src.cli.main")
    def test_cli_calls_main(self, mock_main: MagicMock) -> None:
        """Test cli calls main and exits with its return value."""
        mock_main.return_value = 0

        with pytest.raises(SystemExit) as exc_info:
            cli()

        assert exc_info.value.code == 0
        mock_main.assert_called_once()

    @patch("src.cli.main")
    def test_cli_exits_with_error_code(self, mock_main: MagicMock) -> None:
        """Test cli exits with error code from main."""
        mock_main.return_value = 1

        with pytest.raises(SystemExit) as exc_info:
            cli()

        assert exc_info.value.code == 1
