"""Data storage and file operations."""

import logging
import os
from pathlib import Path
from typing import Protocol

import pandas as pd
from pandas import DataFrame

from src.config import OUTPUT_DIR
from src.models import FetchResult
from src.network import ip_range_to_cidrs

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

            # If allocations are empty, try generating from CSV
            if not allocations and result.data_type in ["ipv4", "ipv6"]:
                allocations = self._allocations_from_csv(csv_path, result.data_type)

            if allocations:
                self._save_ranges_file(result.data_type, allocations)
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
                        last: str = str(row.get("Last") or "").strip()
                        if last:
                            try:
                                allocations.extend(ip_range_to_cidrs(first, last))
                            except ValueError:
                                logger.warning(
                                    "Failed to compute CIDRs for range %s - %s",
                                    first,
                                    last,
                                )
                    else:
                        allocations.append(f"{first}{prefix}")
        elif data_type == "ipv6":
            for _, row in df.iterrows():
                ipv6_prefix: str = str(row.get("Prefix") or "").strip()
                length: str = str(row.get("Length") or "").strip()
                if ipv6_prefix and length:
                    allocations.append(f"{ipv6_prefix}/{length}")
                elif ipv6_prefix:
                    allocations.append(ipv6_prefix)
        return allocations

    def _save_ranges_file(self, data_type: str, allocations: list[str]) -> str:
        """
        Save allocations to ranges file.
        Args:
            result: FetchResult containing allocations to save.
        Returns:
            Path to the ranges file.
        """
        range_file: Path = Path(self.output_dir) / f"{data_type}_ranges.txt"
        with range_file.open("a", encoding="utf-8") as f:
            for alloc in allocations:
                f.write(f"{alloc}\n")
        return str(range_file)

    def clear_ranges_file(self, data_type: str) -> None:
        """
        Clear a ranges file before starting fresh.
        Args:
            data_type: Type of data ('asn', 'ipv4', 'ipv6').
        """
        range_file: Path = Path(self.output_dir) / f"{data_type}_ranges.txt"
        if range_file.exists():
            range_file.unlink()
