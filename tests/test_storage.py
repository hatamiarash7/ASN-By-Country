"""Unit tests for the storage module."""

import os
from unittest.mock import patch

from src.models import FetchResult
from src.storage import FileStorage


class TestFileStorage:
    """Tests for FileStorage class."""

    def test_init_creates_directory(self, temp_output_dir: str) -> None:
        """Test that initialization creates output directory."""
        storage = FileStorage(output_dir=temp_output_dir)
        assert os.path.exists(storage.output_dir)

    def test_save_successful_result(self, temp_output_dir: str) -> None:
        """Test saving a successful fetch result."""
        storage = FileStorage(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="asn",
            data_rows=[{"ASN": "AS12880", "Name": "DCI"}],
            allocations=["AS12880"],
        )

        success: bool = storage.save(result)

        assert success is True
        assert os.path.exists(os.path.join(temp_output_dir, "IR_asn_list.csv"))
        assert os.path.exists(os.path.join(temp_output_dir, "asn_ranges.txt"))

    def test_save_failed_result(self, temp_output_dir: str) -> None:
        """Test that failed results are not saved."""
        storage = FileStorage(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="XX",
            data_type="asn",
            error="Connection failed",
        )

        success: bool = storage.save(result)

        assert success is False

    def test_save_result_without_allocations(self, temp_output_dir: str) -> None:
        """Test saving result with data but no allocations."""
        storage = FileStorage(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="asn",
            data_rows=[{"ASN": "AS99999"}],
            allocations=[],
        )

        success: bool = storage.save(result)

        assert success is True
        assert os.path.exists(os.path.join(temp_output_dir, "IR_asn_list.csv"))
        # Ranges file should not be created for empty allocations
        assert not os.path.exists(os.path.join(temp_output_dir, "asn_ranges.txt"))

    def test_csv_content(self, temp_output_dir: str) -> None:
        """Test that CSV content is correctly written."""
        storage = FileStorage(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="asn",
            data_rows=[
                {"ASN": "AS12880", "Name": "DCI"},
                {"ASN": "AS25124", "Name": "TIC"},
            ],
            allocations=["AS12880", "AS25124"],
        )

        storage.save(result)

        csv_path: str = os.path.join(temp_output_dir, "IR_asn_list.csv")
        with open(csv_path) as f:
            content: str = f.read()

        assert "ASN" in content
        assert "Name" in content
        assert "AS12880" in content
        assert "DCI" in content

    def test_ranges_content(self, temp_output_dir: str) -> None:
        """Test that ranges file content is correctly written."""
        storage = FileStorage(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="asn",
            data_rows=[{"ASN": "AS12880"}],
            allocations=["AS12880", "AS25124"],
        )

        storage.save(result)

        ranges_path: str = os.path.join(temp_output_dir, "asn_ranges.txt")
        with open(ranges_path) as f:
            lines: list[str] = [line.strip() for line in f.readlines()]

        # Check that each allocation exists as a separate line
        assert "AS12880" in lines
        assert "AS25124" in lines
        # Optional: check exact order
        assert lines == ["AS12880", "AS25124"]

    def test_ranges_appends(self, temp_output_dir: str) -> None:
        """Test that ranges are appended for multiple countries."""
        storage = FileStorage(output_dir=temp_output_dir)

        result1 = FetchResult(
            country_code="IR",
            data_type="asn",
            data_rows=[{"ASN": "AS12880"}],
            allocations=["AS12880"],
        )
        result2 = FetchResult(
            country_code="US",
            data_type="asn",
            data_rows=[{"ASN": "AS3356"}],
            allocations=["AS3356"],
        )

        storage.save(result1)
        storage.save(result2)

        ranges_path: str = os.path.join(temp_output_dir, "asn_ranges.txt")
        with open(ranges_path) as f:
            lines: list[str] = f.readlines()

        assert len(lines) == 2
        assert "AS12880" in lines[0]
        assert "AS3356" in lines[1]

    def test_clear_ranges_file(self, temp_output_dir: str) -> None:
        """Test clearing ranges file."""
        storage = FileStorage(output_dir=temp_output_dir)

        # Create a ranges file
        ranges_path: str = os.path.join(temp_output_dir, "asn_ranges.txt")
        with open(ranges_path, "w") as f:
            f.write("AS12880\n")

        assert os.path.exists(ranges_path)

        storage.clear_ranges_file("asn")

        assert not os.path.exists(ranges_path)

    def test_clear_nonexistent_ranges_file(self, temp_output_dir: str) -> None:
        """Test clearing non-existent ranges file doesn't raise error."""
        storage = FileStorage(output_dir=temp_output_dir)
        # Should not raise any exception
        storage.clear_ranges_file("ipv6")

    def test_multiple_data_types(self, temp_output_dir: str) -> None:
        """Test saving different data types."""
        storage = FileStorage(output_dir=temp_output_dir)

        asn_result = FetchResult(
            country_code="IR",
            data_type="asn",
            data_rows=[{"ASN": "AS12880"}],
            allocations=["AS12880"],
        )
        ipv4_result = FetchResult(
            country_code="IR",
            data_type="ipv4",
            data_rows=[{"IP": "5.22.0.0/19"}],
            allocations=["5.22.0.0/19"],
        )

        storage.save(asn_result)
        storage.save(ipv4_result)

        assert os.path.exists(os.path.join(temp_output_dir, "IR_asn_list.csv"))
        assert os.path.exists(os.path.join(temp_output_dir, "IR_ipv4_list.csv"))
        assert os.path.exists(os.path.join(temp_output_dir, "asn_ranges.txt"))
        assert os.path.exists(os.path.join(temp_output_dir, "ipv4_ranges.txt"))

    def test_save_os_error_returns_false(self, temp_output_dir: str) -> None:
        """Test that save returns False on OSError."""
        storage = FileStorage(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="asn",
            data_rows=[{"ASN": "AS12880"}],
            allocations=["AS12880"],
        )

        with patch.object(storage, "_save_csv", side_effect=OSError("Disk full")):
            success = storage.save(result)

        assert success is False


class TestAllocationsFromCsv:
    """Tests for _allocations_from_csv method."""

    def test_ipv4_normal_prefix(self, temp_output_dir: str) -> None:
        """Test generating allocations from CSV with normal IPv4 prefix."""
        storage = FileStorage(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="ipv4",
            data_rows=[
                {"First": "5.22.0.0", "Last": "5.22.31.255", "Prefix": "/19"},
                {"First": "10.0.0.0", "Last": "10.0.0.255", "Prefix": "/24"},
            ],
            allocations=None,  # Force allocation generation from CSV
        )

        storage.save(result)

        ranges_path = os.path.join(temp_output_dir, "ipv4_ranges.txt")
        with open(ranges_path) as f:
            lines = [line.strip() for line in f.readlines()]

        assert "5.22.0.0/19" in lines
        assert "10.0.0.0/24" in lines

    def test_ipv4_aggreg_prefix(self, temp_output_dir: str) -> None:
        """Test generating allocations from CSV with Aggreg prefix."""
        storage = FileStorage(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="ipv4",
            data_rows=[
                {"First": "91.237.254.0", "Last": "91.238.0.255", "Prefix": "Aggreg"},
            ],
            allocations=None,
        )

        storage.save(result)

        ranges_path = os.path.join(temp_output_dir, "ipv4_ranges.txt")
        with open(ranges_path) as f:
            lines = [line.strip() for line in f.readlines()]

        # 91.237.254.0 - 91.238.0.255 = /23 + /24
        assert "91.237.254.0/23" in lines
        assert "91.238.0.0/24" in lines

    def test_ipv4_aggreg_missing_last(self, temp_output_dir: str) -> None:
        """Test Aggreg prefix with missing Last field."""
        storage = FileStorage(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="ipv4",
            data_rows=[
                {"First": "5.22.0.0", "Prefix": "Aggreg"},  # No Last field
            ],
            allocations=None,
        )

        storage.save(result)

        # No ranges file should be created since no allocations could be generated
        ranges_path = os.path.join(temp_output_dir, "ipv4_ranges.txt")
        assert not os.path.exists(ranges_path)

    def test_ipv4_aggreg_invalid_range(self, temp_output_dir: str) -> None:
        """Test Aggreg prefix with invalid IP range logs warning."""
        storage = FileStorage(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="ipv4",
            data_rows=[
                {"First": "invalid", "Last": "also_invalid", "Prefix": "Aggreg"},
            ],
            allocations=None,
        )

        # Should not raise, just logs warning and skips
        storage.save(result)

        # No ranges file should be created
        ranges_path = os.path.join(temp_output_dir, "ipv4_ranges.txt")
        assert not os.path.exists(ranges_path)

    def test_ipv4_missing_first(self, temp_output_dir: str) -> None:
        """Test IPv4 row with missing First field."""
        storage = FileStorage(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="ipv4",
            data_rows=[
                {"Last": "5.22.31.255", "Prefix": "/19"},  # No First
            ],
            allocations=None,
        )

        storage.save(result)

        # No ranges file created
        ranges_path = os.path.join(temp_output_dir, "ipv4_ranges.txt")
        assert not os.path.exists(ranges_path)

    def test_ipv4_missing_prefix(self, temp_output_dir: str) -> None:
        """Test IPv4 row with missing Prefix field."""
        storage = FileStorage(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="ipv4",
            data_rows=[
                {"First": "5.22.0.0", "Last": "5.22.31.255"},  # No Prefix
            ],
            allocations=None,
        )

        storage.save(result)

        # No ranges should be generated
        ranges_path = os.path.join(temp_output_dir, "ipv4_ranges.txt")
        assert not os.path.exists(ranges_path)

    def test_ipv6_with_length(self, temp_output_dir: str) -> None:
        """Test generating allocations from CSV for IPv6 with Length."""
        storage = FileStorage(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="ipv6",
            data_rows=[
                {"Prefix": "2001:db8::", "Length": "32"},
                {"Prefix": "2001:db9::", "Length": "48"},
            ],
            allocations=None,
        )

        storage.save(result)

        ranges_path = os.path.join(temp_output_dir, "ipv6_ranges.txt")
        with open(ranges_path) as f:
            lines = [line.strip() for line in f.readlines()]

        assert "2001:db8::/32" in lines
        assert "2001:db9::/48" in lines

    def test_ipv6_without_length(self, temp_output_dir: str) -> None:
        """Test generating allocations from CSV for IPv6 without Length."""
        storage = FileStorage(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="ipv6",
            data_rows=[
                {"Prefix": "2001:db8::"},  # No Length
            ],
            allocations=None,
        )

        storage.save(result)

        ranges_path = os.path.join(temp_output_dir, "ipv6_ranges.txt")
        with open(ranges_path) as f:
            lines = [line.strip() for line in f.readlines()]

        assert "2001:db8::" in lines

    def test_ipv6_missing_prefix(self, temp_output_dir: str) -> None:
        """Test IPv6 row with missing Prefix field."""
        storage = FileStorage(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="ipv6",
            data_rows=[
                {"Length": "32"},  # No Prefix
            ],
            allocations=None,
        )

        storage.save(result)

        # No ranges should be generated
        ranges_path = os.path.join(temp_output_dir, "ipv6_ranges.txt")
        assert not os.path.exists(ranges_path)
