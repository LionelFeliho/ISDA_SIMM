from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

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


def _tenor_buckets(tenors: Sequence[str]) -> List[TenorBucket]:
    """Build sorted tenor buckets for bucketing remaining maturities."""
    buckets: List[TenorBucket] = []
    for tenor in tenors:
        days = _tenor_to_days(tenor)
        if days is None:
            continue
        buckets.append(TenorBucket(tenor=tenor, days=days))
    return sorted(buckets, key=lambda bucket: bucket.days)


def _bucket_remaining_tenor(
    remaining_days: float,
    buckets: List[TenorBucket],
) -> List[Tuple[str, float]]:
    """Map remaining days to tenor buckets with prorata temporis weights."""
    if remaining_days <= 0:
        return []

    if remaining_days <= buckets[0].days:
        return [(buckets[0].tenor, 1.0)]
    if remaining_days >= buckets[-1].days:
        return [(buckets[-1].tenor, 1.0)]

    lower = buckets[0]
    upper = buckets[-1]
    for bucket in buckets:
        if bucket.days <= remaining_days:
            lower = bucket
        elif bucket.days > remaining_days:
            upper = bucket
            break

    if lower.days == upper.days:
        return [(lower.tenor, 1.0)]

    weight_upper = (remaining_days - lower.days) / (upper.days - lower.days)
    weight_lower = 1.0 - weight_upper
    return [(lower.tenor, weight_lower), (upper.tenor, weight_upper)]


def age_sensitivities(
    crif: pd.DataFrame,
    tenors: Optional[Sequence[str]] = None,
) -> Dict[str, pd.DataFrame]:
    """Age spot sensitivities across SIMM tenor buckets.

    Returns a dictionary keyed by "0D" (spot) and each tenor in the input list.
    For each tenor key, the CRIF sensitivities are aged by rolling down the
    Label1 tenor bucket by that amount. Sensitivities that mature are dropped.
    """
    tenor_list = list(tenors) if tenors is not None else list(simm_tenor_list)
    buckets = _tenor_buckets(tenor_list)
    if not buckets:
        raise ValueError("No valid tenor buckets found in the provided list.")

    if "Label1" not in crif.columns:
        raise KeyError("CRIF data must include a Label1 column for tenor aging.")
    if "AmountUSD" not in crif.columns:
        raise KeyError("CRIF data must include an AmountUSD column for prorata aging.")

    aged: Dict[str, pd.DataFrame] = {"0D": crif.copy()}
    for ageing_tenor in tenor_list:
        ageing_days = _tenor_to_days(ageing_tenor)
        if ageing_days is None:
            LOGGER.debug("Skipping unrecognized ageing tenor: %s", ageing_tenor)
            continue

        rows: List[dict] = []
        for _, row in crif.iterrows():
            label = row["Label1"]
            label_str = str(label).lower()
            original_days = _tenor_to_days(label_str)
            if original_days is None:
                rows.append(row.to_dict())
                continue
            remaining_days = original_days - ageing_days
            allocations = _bucket_remaining_tenor(remaining_days, buckets)
            if not allocations:
                continue
            for tenor, weight in allocations:
                new_row = row.to_dict()
                new_row["Label1"] = tenor
                new_row["AmountUSD"] = new_row["AmountUSD"] * weight
                rows.append(new_row)

        df = pd.DataFrame(rows)
        aged[ageing_tenor] = df
        LOGGER.debug("Aged sensitivities for %s with %d rows.", ageing_tenor, len(df))

    return aged
