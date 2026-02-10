"""Network utility functions for IP address operations."""

import ipaddress
from ipaddress import IPv4Address, IPv6Address


def ip_range_to_cidrs(first_ip: str, last_ip: str) -> list[str]:
    """
    Convert an IP address range to a minimal list of CIDR subnets.

    Uses Python's ipaddress.summarize_address_range() to compute the
    smallest set of CIDR networks that exactly covers the range from
    first_ip to last_ip (inclusive).

    Args:
        first_ip: Start IP address of the range (e.g., "91.237.254.0").
        last_ip: End IP address of the range (e.g., "91.238.0.255").

    Returns:
        List of CIDR notation strings (e.g., ["91.237.254.0/23", "91.238.0.0/24"]).

    Raises:
        ValueError: If the IP addresses are invalid or first > last.
    """
    first: IPv4Address | IPv6Address = ipaddress.ip_address(first_ip.strip())
    last: IPv4Address | IPv6Address = ipaddress.ip_address(last_ip.strip())

    networks = ipaddress.summarize_address_range(first, last)
    return [str(net) for net in networks]
