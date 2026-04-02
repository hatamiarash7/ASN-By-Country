"""Data storage and file operations."""

import ipaddress
import logging
import os
from pathlib import Path
from typing import Protocol

import pandas as pd
from pandas import DataFrame

from src.config import OUTPUT_DIR
from src.models import FetchResult
from src.network import ip_prefix_to_cidrs

logger: logging.Logger = logging.getLogger(__name__)


class StorageBackend(Protocol):
    """Protocol for storage backends."""

    def save(self, result: FetchResult) -> bool: ...


class FileStorage:
    """Handles saving fetched data to local files."""

    def __init__(self, output_dir: str = OUTPUT_DIR) -> None:
        """
        Initialize FileStorage.

        Args:
            output_dir: Directory for output files.
        """
        self.output_dir: str = output_dir
        self._ensure_output_dir()

    def _ensure_output_dir(self) -> None:
        """Ensure output directory exists."""
        os.makedirs(self.output_dir, exist_ok=True)

    def save(self, result: FetchResult) -> bool:
        """
        Save fetch result to files.

        Args:
            result: FetchResult to save.

        Returns:
            True if save was successful, False otherwise.
        """
        if not result.is_success:
            return False

        try:
            csv_path: str = self._save_csv(result)
            allocations: list[str] | None = result.allocations

            if not allocations and result.data_type in ["ipv4", "ipv6"]:
                allocations = self._allocations_from_csv(csv_path, result.data_type)

            self._save_prefixes_file(result.data_type, allocations)
            return True
        except OSError:
            return False

    def _save_csv(self, result: FetchResult) -> str:
        """
        Save detailed data to CSV file.
        Args:
            result: FetchResult containing data to save.
        Returns:
            Path to the saved CSV file.
        """
        csv_path: Path = (
            Path(self.output_dir) / f"{result.country_code}_{result.data_type}_list.csv"
        )
        pd.DataFrame(result.data_rows).to_csv(csv_path, index=False)
        return str(csv_path)

    def _allocations_from_csv(self, csv_path: str, data_type: str) -> list[str]:
        """Generate allocations list from CSV if scraper didn't produce them."""
        df: DataFrame = pd.read_csv(csv_path)
        allocations: list[str] = []

        if data_type == "ipv4":
            for _, row in df.iterrows():
                first: str = str(row.get("First") or "").strip()
                prefix: str = str(row.get("Prefix") or "").strip()
                if first and prefix:
                    if prefix.lower() == "aggreg":
                        if last := str(row.get("Last") or "").strip():
                            try:
                                allocations.extend(ip_prefix_to_cidrs(first, last))
                            except ValueError:
                                logger.warning(
                                    "Failed to compute CIDRs for prefix %s - %s",
                                    first,
                                    last,
                                )
                    else:
                        allocations.append(f"{first}{prefix}")
        elif data_type == "ipv6":
            for _, row in df.iterrows():
                ipv6_prefix: str = str(row.get("First") or "").strip()
                length: str = str(row.get("Prefix") or "").strip()
                allocations.append(f"{ipv6_prefix}{length}")
        return allocations

    def _save_prefixes_file(self, data_type: str, allocations: list[str] | None) -> str:
        """
        Save allocations to prefixes file.
        Args:
            data_type: Type of data ('asn', 'ipv4', 'ipv6').
            allocations: List of allocations to save.
        Returns:
            Path to the prefixes file.
        """
        all_ips: list[str] = []
        prefix_file: Path = Path(self.output_dir) / f"{data_type}_prefixes.txt"
        with prefix_file.open("a", encoding="utf-8") as f:
            for alloc in allocations or []:
                f.write(alloc + "\n")
                if data_type in ("asn", "ipv6"):
                    continue  # ASNs don't expand to IPs and IPv6 expansion is skipped due to size
                try:
                    network = ipaddress.ip_network(alloc, strict=False)
                    # Get all hosts in the network
                    ips: list[str] = [str(ip) for ip in network.hosts()]
                    all_ips.extend(ips)
                except ValueError as e:
                    logger.warning(
                        "Error parsing %s: %s",
                        alloc,
                        e,
                    )

        # ASNs don't expand to IPs and IPv6 expansion is skipped due to size
        if data_type == "ipv4":
            expanded_prefix_file: Path = Path(self.output_dir) / f"{data_type}_prefixes_expanded.txt"
            with expanded_prefix_file.open("a", encoding="utf-8") as f:
                for ip in all_ips:
                    f.write(ip + "\n")

        return str(prefix_file)

    def clear_prefixes_file(self, data_type: str) -> None:
        """
        Clear a prefixes file before starting fresh.
        Args:
            data_type: Type of data ('asn', 'ipv4', 'ipv6').
        """
        prefix_file: Path = Path(self.output_dir) / f"{data_type}_prefixes.txt"
        if prefix_file.exists():
            prefix_file.unlink()
