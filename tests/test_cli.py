"""Unit tests for the CLI module."""

import pytest

from src.cli import create_parser, validate_country_codes


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
