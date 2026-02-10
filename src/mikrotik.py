import logging
from pathlib import Path

from src.models import FetchResult
from src.network import ip_range_to_cidrs

logger: logging.Logger = logging.getLogger(__name__)


class MikroTikExporter:
    """
    Generates RouterOS .rsc scripts from allocations.
    """

    def __init__(self, output_dir: str) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(self, result: FetchResult) -> None:
        # MikroTik export only makes sense for IP allocations
        if result.data_type == "asn":
            return

        # If allocations empty, try loading from CSV
        allocations: list[str] | None = result.allocations
        if not allocations and result.data_rows:
            allocations: list[str] = self._allocations_from_csv(result)

        if not allocations:
            return

        filename: Path = self.output_dir / f"{result.country_code}_{result.data_type}.rsc"
        address_list = f"{result.country_code.lower()}-{result.data_type}"

        filename.parent.mkdir(parents=True, exist_ok=True)

        with filename.open("a", encoding="utf-8") as f:
            for net in allocations:
                if result.data_type == "ipv6":
                    f.write(f"/ipv6 firewall address-list add list={address_list} address={net}\n")
                else:
                    f.write(f"/ip firewall address-list add list={address_list} address={net}\n")

    def _allocations_from_csv(self, result: FetchResult) -> list[str]:
        """
        Generate allocations from CSV data_rows if not set.
        """
        allocations: list[str] = []

        if not result.data_rows:
            return allocations

        for row in result.data_rows:
            if result.data_type == "ipv4":
                first: str | None = row.get("First")
                prefix: str | None = row.get("Prefix")
                if first and prefix:
                    if prefix.strip().lower() == "aggreg":
                        last: str | None = row.get("Last")
                        if last:
                            try:
                                allocations.extend(ip_range_to_cidrs(first.strip(), last.strip()))
                            except ValueError:
                                logger.warning(
                                    "Failed to compute CIDRs for range %s - %s",
                                    first,
                                    last,
                                )
                    else:
                        allocations.append(f"{first.strip()}{prefix.strip()}")
            elif result.data_type == "ipv6":
                prefix: str | None = row.get("Prefix")
                length: str | None = row.get("Length")
                if prefix and length:
                    allocations.append(f"{prefix.strip()}/{length}")
                elif prefix:
                    allocations.append(prefix.strip())

        return allocations
