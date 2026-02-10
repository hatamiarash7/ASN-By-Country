"""Unit tests for the mikrotik module."""

import os

from src.mikrotik import MikroTikExporter
from src.models import FetchResult


class TestMikroTikExporter:
    """Tests for MikroTikExporter class."""

    def test_init_creates_directory(self, temp_output_dir: str) -> None:
        """Test that initialization creates output directory."""
        exporter = MikroTikExporter(output_dir=temp_output_dir)
        assert exporter.output_dir.exists()

    def test_init_creates_nested_directory(self, temp_output_dir: str) -> None:
        """Test that initialization creates nested output directory."""
        nested_dir = os.path.join(temp_output_dir, "nested", "dir")
        exporter = MikroTikExporter(output_dir=nested_dir)
        assert exporter.output_dir.exists()

    def test_export_skips_asn(self, temp_output_dir: str) -> None:
        """Test that export skips ASN data type."""
        exporter = MikroTikExporter(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="asn",
            data_rows=[{"Range": "AS12880"}],
            allocations=["AS12880"],
        )

        exporter.export(result)

        # Should not create any file for ASN
        assert not os.path.exists(os.path.join(temp_output_dir, "IR_asn.rsc"))

    def test_export_ipv4_with_allocations(self, temp_output_dir: str) -> None:
        """Test export of IPv4 data with allocations."""
        exporter = MikroTikExporter(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="ipv4",
            data_rows=[{"First": "5.22.0.0", "Prefix": "/19"}],
            allocations=["5.22.0.0/19", "5.23.0.0/20"],
        )

        exporter.export(result)

        rsc_path = os.path.join(temp_output_dir, "IR_ipv4.rsc")
        assert os.path.exists(rsc_path)

        with open(rsc_path) as f:
            content = f.read()

        assert "/ip firewall address-list add list=ir-ipv4 address=5.22.0.0/19" in content
        assert "/ip firewall address-list add list=ir-ipv4 address=5.23.0.0/20" in content

    def test_export_ipv6_with_allocations(self, temp_output_dir: str) -> None:
        """Test export of IPv6 data with allocations."""
        exporter = MikroTikExporter(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="ipv6",
            data_rows=[{"First": "2001:db8::", "Prefix": "/32"}],
            allocations=["2001:db8::/32", "2001:db9::/48"],
        )

        exporter.export(result)

        rsc_path = os.path.join(temp_output_dir, "IR_ipv6.rsc")
        assert os.path.exists(rsc_path)

        with open(rsc_path) as f:
            content = f.read()

        assert "/ipv6 firewall address-list add list=ir-ipv6 address=2001:db8::/32" in content
        assert "/ipv6 firewall address-list add list=ir-ipv6 address=2001:db9::/48" in content

    def test_export_skips_empty_allocations(self, temp_output_dir: str) -> None:
        """Test that export skips when allocations are empty and no data_rows."""
        exporter = MikroTikExporter(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="ipv4",
            data_rows=None,
            allocations=None,
        )

        exporter.export(result)

        # Should not create any file
        assert not os.path.exists(os.path.join(temp_output_dir, "IR_ipv4.rsc"))

    def test_export_generates_from_data_rows(self, temp_output_dir: str) -> None:
        """Test that export generates allocations from data_rows when allocations is empty."""
        exporter = MikroTikExporter(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="ipv4",
            data_rows=[
                {"First": "5.22.0.0", "Last": "5.22.7.255", "Prefix": "/19"},
                {"First": "10.0.0.0", "Last": "10.0.0.255", "Prefix": "/24"},
            ],
            allocations=None,
        )

        exporter.export(result)

        rsc_path = os.path.join(temp_output_dir, "IR_ipv4.rsc")
        assert os.path.exists(rsc_path)

        with open(rsc_path) as f:
            content = f.read()

        assert "5.22.0.0/19" in content
        assert "10.0.0.0/24" in content

    def test_export_handles_aggreg_in_data_rows(self, temp_output_dir: str) -> None:
        """Test that export handles Aggreg prefix in data_rows."""
        exporter = MikroTikExporter(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="ipv4",
            data_rows=[
                {"First": "91.237.254.0", "Last": "91.238.0.255", "Prefix": "Aggreg"},
            ],
            allocations=None,
        )

        exporter.export(result)

        rsc_path = os.path.join(temp_output_dir, "IR_ipv4.rsc")
        assert os.path.exists(rsc_path)

        with open(rsc_path) as f:
            content = f.read()

        # 91.237.254.0 - 91.238.0.255 = /23 + /24
        assert "91.237.254.0/23" in content
        assert "91.238.0.0/24" in content

    def test_export_ipv6_from_data_rows(self, temp_output_dir: str) -> None:
        """Test that export generates IPv6 allocations from data_rows."""
        exporter = MikroTikExporter(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="ipv6",
            data_rows=[
                {"Prefix": "2001:db8::", "Length": "32"},
                {"Prefix": "2001:db9::"},  # No Length
            ],
            allocations=None,
        )

        exporter.export(result)

        rsc_path = os.path.join(temp_output_dir, "IR_ipv6.rsc")
        assert os.path.exists(rsc_path)

        with open(rsc_path) as f:
            content = f.read()

        assert "2001:db8::/32" in content
        assert "2001:db9::" in content

    def test_export_appends_to_existing_file(self, temp_output_dir: str) -> None:
        """Test that export appends to existing rsc file."""
        exporter = MikroTikExporter(output_dir=temp_output_dir)

        result1 = FetchResult(
            country_code="IR",
            data_type="ipv4",
            data_rows=[{"First": "5.22.0.0"}],
            allocations=["5.22.0.0/19"],
        )
        result2 = FetchResult(
            country_code="IR",
            data_type="ipv4",
            data_rows=[{"First": "10.0.0.0"}],
            allocations=["10.0.0.0/24"],
        )

        exporter.export(result1)
        exporter.export(result2)

        rsc_path = os.path.join(temp_output_dir, "IR_ipv4.rsc")
        with open(rsc_path) as f:
            lines = f.readlines()

        assert len(lines) == 2
        assert "5.22.0.0/19" in lines[0]
        assert "10.0.0.0/24" in lines[1]

    def test_export_with_empty_data_rows_list(self, temp_output_dir: str) -> None:
        """Test export with empty data_rows list."""
        exporter = MikroTikExporter(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="ipv4",
            data_rows=[],
            allocations=None,
        )

        exporter.export(result)

        # Should not create any file for empty data
        assert not os.path.exists(os.path.join(temp_output_dir, "IR_ipv4.rsc"))


class TestAllocationsFromCsv:
    """Tests for _allocations_from_csv method."""

    def test_empty_data_rows(self, temp_output_dir: str) -> None:
        """Test with empty data_rows."""
        exporter = MikroTikExporter(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="ipv4",
            data_rows=None,
            allocations=None,
        )

        allocations = exporter._allocations_from_csv(result)
        assert allocations == []

    def test_ipv4_normal_prefix(self, temp_output_dir: str) -> None:
        """Test IPv4 with normal prefix."""
        exporter = MikroTikExporter(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="ipv4",
            data_rows=[
                {"First": "192.168.0.0", "Last": "192.168.0.255", "Prefix": "/24"},
            ],
            allocations=None,
        )

        allocations = exporter._allocations_from_csv(result)
        assert allocations == ["192.168.0.0/24"]

    def test_ipv4_aggreg_prefix(self, temp_output_dir: str) -> None:
        """Test IPv4 with Aggreg prefix."""
        exporter = MikroTikExporter(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="ipv4",
            data_rows=[
                {"First": "91.237.254.0", "Last": "91.238.0.255", "Prefix": "Aggreg"},
            ],
            allocations=None,
        )

        allocations = exporter._allocations_from_csv(result)
        assert "91.237.254.0/23" in allocations
        assert "91.238.0.0/24" in allocations

    def test_ipv4_aggreg_without_last(self, temp_output_dir: str) -> None:
        """Test IPv4 with Aggreg prefix but missing Last field."""
        exporter = MikroTikExporter(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="ipv4",
            data_rows=[
                {"First": "192.168.0.0", "Prefix": "Aggreg"},  # No Last
            ],
            allocations=None,
        )

        allocations = exporter._allocations_from_csv(result)
        assert allocations == []

    def test_ipv6_with_length(self, temp_output_dir: str) -> None:
        """Test IPv6 with Length field."""
        exporter = MikroTikExporter(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="ipv6",
            data_rows=[
                {"Prefix": "2001:db8::", "Length": "32"},
            ],
            allocations=None,
        )

        allocations = exporter._allocations_from_csv(result)
        assert allocations == ["2001:db8::/32"]

    def test_ipv6_without_length(self, temp_output_dir: str) -> None:
        """Test IPv6 without Length field."""
        exporter = MikroTikExporter(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="ipv6",
            data_rows=[
                {"Prefix": "2001:db8::"},
            ],
            allocations=None,
        )

        allocations = exporter._allocations_from_csv(result)
        assert allocations == ["2001:db8::"]

    def test_missing_first_field(self, temp_output_dir: str) -> None:
        """Test IPv4 row missing First field."""
        exporter = MikroTikExporter(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="ipv4",
            data_rows=[
                {"Prefix": "/24"},  # No First
            ],
            allocations=None,
        )

        allocations = exporter._allocations_from_csv(result)
        assert allocations == []

    def test_missing_prefix_field(self, temp_output_dir: str) -> None:
        """Test IPv4 row missing Prefix field."""
        exporter = MikroTikExporter(output_dir=temp_output_dir)
        result = FetchResult(
            country_code="IR",
            data_type="ipv4",
            data_rows=[
                {"First": "192.168.0.0"},  # No Prefix
            ],
            allocations=None,
        )

        allocations = exporter._allocations_from_csv(result)
        assert allocations == []
