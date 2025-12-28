"""Pytest configuration and fixtures."""

import tempfile
from unittest.mock import Mock

import pytest


@pytest.fixture
def sample_html_asn() -> str:
    """Sample HTML response for ASN data."""
    return """
    <html>
    <body>
    <table class="delegs asn ripencc">
        <tr><th>#</th><th>Registry</th><th>Country</th><th>ASN</th><th>Name</th><th>Date</th><th>Status</th></tr>
        <tr><th></th><th></th><th></th><th></th><th></th><th></th><th></th></tr>
        <tr><td>1</td><td>ripencc</td><td>IR</td><td>AS12880</td><td>DCI</td><td>2003-01-01</td><td>Allocated</td></tr>
        <tr><td>2</td><td>ripencc</td><td>IR</td><td>AS25124</td><td>TIC</td><td>2004-05-15</td><td>Allocated</td></tr>
        <tr><td>3</td><td>ripencc</td><td>IR</td><td>AS99999</td><td>Test</td><td>2005-03-20</td><td>Reserved</td></tr>
    </table>
    </body>
    </html>
    """


@pytest.fixture
def sample_html_ipv4() -> str:
    """Sample HTML response for IPv4 data."""
    return """
    <html>
    <body>
    <table class="delegs ipv4 ripencc">
        <tr><th>#</th><th>Registry</th><th>Country</th><th>IP</th><th>Prefix</th><th>Size</th><th>Date</th><th>Status</th></tr>
        <tr><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th></tr>
        <tr><td>1</td><td>ripencc</td><td>IR</td><td>5.22.0.0</td><td>/19</td><td>8192</td><td>2012-01-01</td><td>Allocated</td></tr>
        <tr><td>2</td><td>ripencc</td><td>IR</td><td>5.23.0.0</td><td>/20</td><td>4096</td><td>2012-02-15</td><td>Reserved</td></tr>
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
def temp_output_dir():
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
