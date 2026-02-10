"""Pytest configuration and fixtures."""

import tempfile
from collections.abc import Generator
from unittest.mock import Mock

import pytest


@pytest.fixture
def sample_html_asn() -> str:
    """Sample HTML response for ASN data (matches real website structure)."""
    return """
    <html>
    <body>
    <table class="delegs asn ripencc">
        <tr><th colspan="7">RIPE NCC Delegations</th></tr>
        <tr><th>Zone</th><th>Country</th><th>Parameter</th><th>Range</th><th>Number</th><th>Date</th><th>Status</th></tr>
        <tr><td>RIPE NCC</td><td>IR</td><td>ASN</td><td>AS12880</td><td>1</td><td>2003-01-01</td><td>Allocated</td></tr>
        <tr><td>RIPE NCC</td><td>IR</td><td>ASN</td><td>AS25124</td><td>1</td><td>2004-05-15</td><td>Allocated</td></tr>
        <tr><td>RIPE NCC</td><td>IR</td><td>ASN</td><td>AS99999</td><td>1</td><td>2005-03-20</td><td>Reserved</td></tr>
    </table>
    </body>
    </html>
    """


@pytest.fixture
def sample_html_ipv4() -> str:
    """Sample HTML response for IPv4 data (matches real website structure)."""
    return """
    <html>
    <body>
    <table class="delegs ipv4 ripencc">
        <tr><th colspan="9">RIPE NCC Delegations</th></tr>
        <tr><th>Zone</th><th>Country</th><th>Parameter</th><th>First</th><th>Last</th><th>Prefix</th><th>Number</th><th>Date</th><th>Status</th></tr>
        <tr><td>RIPE NCC</td><td>IR</td><td>IPv4</td><td>5.22.0.0</td><td>5.22.7.255</td><td>/19</td><td>8192</td><td>2012-01-01</td><td>Allocated</td></tr>
        <tr><td>RIPE NCC</td><td>IR</td><td>IPv4</td><td>5.23.0.0</td><td>5.23.15.255</td><td>/20</td><td>4096</td><td>2012-02-15</td><td>Reserved</td></tr>
    </table>
    </body>
    </html>
    """


@pytest.fixture
def sample_html_ipv4_aggreg() -> str:
    """Sample HTML response for IPv4 data with Aggreg prefix."""
    return """
    <html>
    <body>
    <table class="delegs ipv4 ripencc">
        <tr><th colspan="9">RIPE NCC Delegations</th></tr>
        <tr><th>Zone</th><th>Country</th><th>Parameter</th><th>First</th><th>Last</th><th>Prefix</th><th>Number</th><th>Date</th><th>Status</th></tr>
        <tr><td>RIPE NCC</td><td>IR</td><td>IPv4</td><td>88.135.32.0</td><td>88.135.32.255</td><td>/24</td><td>256</td><td>2009-11-16</td><td>Assigned</td></tr>
        <tr><td>RIPE NCC</td><td>IR</td><td>IPv4</td><td>91.237.254.0</td><td>91.238.0.255</td><td>Aggreg</td><td>768</td><td>2012-04-03</td><td>Assigned</td></tr>
        <tr><td>RIPE NCC</td><td>IR</td><td>IPv4</td><td>194.33.125.0</td><td>194.33.127.255</td><td>Aggreg</td><td>768</td><td>2012-06-04</td><td>Assigned</td></tr>
    </table>
    </body>
    </html>
    """


@pytest.fixture
def sample_html_no_table() -> str:
    """Sample HTML response with no data table."""
    return """
    <html>
    <body>
    <p>No data available</p>
    </body>
    </html>
    """


@pytest.fixture
def temp_output_dir() -> Generator[str]:
    """Create a temporary output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_response() -> Mock:
    """Create a mock response object."""
    mock = Mock()
    mock.status_code = 200
    mock.raise_for_status = Mock()
    return mock
