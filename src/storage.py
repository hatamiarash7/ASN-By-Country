"""Data storage and file operations."""

import os
from typing import Protocol

import pandas as pd

from src.config import OUTPUT_DIR
from src.models import FetchResult


class StorageBackend(Protocol):
    """Protocol for storage backends."""

    def save(self, result: FetchResult) -> bool:
        """Save fetch result to storage."""
        ...


class FileStorage:
    """Handles saving fetched data to files."""

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
            self._save_csv(result)
            if result.has_allocations:
                self._save_ranges(result)
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
        csv_filename: str = os.path.join(
            self.output_dir,
            f"{result.country_code}_{result.data_type}_list.csv",
        )
        pd.DataFrame(result.data_rows).to_csv(csv_filename, index=False)
        return csv_filename

    def _save_ranges(self, result: FetchResult) -> str:
        """
        Save allocations to ranges file.

        Args:
            result: FetchResult containing allocations to save.

        Returns:
            Path to the ranges file.
        """
        range_file_path: str = os.path.join(
            self.output_dir,
            f"{result.data_type}_ranges.txt",
        )
        with open(range_file_path, "a", encoding="utf-8") as f:
            f.write(",".join(result.allocations or []) + "\n")
        return range_file_path

    def clear_ranges_file(self, data_type: str) -> None:
        """
        Clear a ranges file before starting fresh.

        Args:
            data_type: Type of data ('asn', 'ipv4', 'ipv6').
        """
        range_file_path: str = os.path.join(self.output_dir, f"{data_type}_ranges.txt")
        if os.path.exists(range_file_path):
            os.remove(range_file_path)
