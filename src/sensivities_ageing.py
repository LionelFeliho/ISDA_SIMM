from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

import pandas as pd

from . import simm_tenor_list


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class TenorBucket:
    """Tenor bucket definition with a day count."""

    tenor: str
    days: float


def _tenor_to_days(tenor: str) -> Optional[float]:
    """Convert SIMM-style tenor strings to day counts.

    Uses a 365-day year and 365/12 days per month to align with SIMM scaling.
    """
    normalized = tenor.lower()
    if normalized == "2w":
        return 14.0
    if "m" in normalized:
        return (365.0 / 12.0) * float(normalized.replace("m", ""))
    if "y" in normalized:
        return 365.0 * float(normalized.replace("y", ""))
    return None


def _tenor_buckets() -> List[TenorBucket]:
    """Build sorted tenor buckets for bucketing remaining maturities."""
    buckets: List[TenorBucket] = []
    for tenor in simm_tenor_list:
        days = _tenor_to_days(tenor)
        if days is None:
            continue
        buckets.append(TenorBucket(tenor=tenor, days=days))
    return sorted(buckets, key=lambda bucket: bucket.days)


def _bucket_remaining_tenor(remaining_days: float, buckets: List[TenorBucket]) -> Optional[str]:
    """Map remaining days to the nearest lower (or equal) SIMM tenor bucket."""
    if remaining_days <= 0:
        return None
    chosen = None
    for bucket in buckets:
        if bucket.days <= remaining_days:
            chosen = bucket.tenor
        else:
            break
    return chosen or buckets[0].tenor


def age_sensitivities(crif: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Age spot sensitivities across SIMM tenor buckets.

    Returns a dictionary keyed by "0D" (spot) and each tenor in simm_tenor_list.
    For each tenor key, the CRIF sensitivities are aged by rolling down the
    Label1 tenor bucket by that amount. Sensitivities that mature are dropped.
    """
    buckets = _tenor_buckets()
    if not buckets:
        raise ValueError("No valid tenor buckets found in simm_tenor_list.")

    if "Label1" not in crif.columns:
        raise KeyError("CRIF data must include a Label1 column for tenor aging.")

    aged: Dict[str, pd.DataFrame] = {"0D": crif.copy()}
    for ageing_tenor in simm_tenor_list:
        ageing_days = _tenor_to_days(ageing_tenor)
        if ageing_days is None:
            LOGGER.debug("Skipping unrecognized ageing tenor: %s", ageing_tenor)
            continue

        df = crif.copy()
        new_labels: List[Optional[str]] = []
        for label in df["Label1"].tolist():
            label_str = str(label).lower()
            original_days = _tenor_to_days(label_str)
            if original_days is None:
                new_labels.append(label)
                continue
            remaining_days = original_days - ageing_days
            new_labels.append(_bucket_remaining_tenor(remaining_days, buckets))

        df["Label1"] = new_labels
        df = df[df["Label1"].notna()].reset_index(drop=True)
        aged[ageing_tenor] = df
        LOGGER.debug("Aged sensitivities for %s with %d rows.", ageing_tenor, len(df))

    return aged
