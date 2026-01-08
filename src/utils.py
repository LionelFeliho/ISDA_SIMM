"""Utility helpers for SIMM calculations."""
from __future__ import annotations

import logging
import math
from typing import Iterable, List, Sequence

from . import simm_tenor_list

logger = logging.getLogger(__name__)


# Calculate Concentration Threshold
def concentration_threshold(sum_s: float, threshold: float) -> float:
    """Return the concentration threshold given sensitivity and threshold value."""
    value = float(max(1, math.sqrt(abs(sum_s) / threshold)))
    logger.debug("Concentration threshold computed: %s", value)
    return value


# Sum Sensitivities(AmountUSD) from CRIF
def sum_sensitivities(crif) -> float:
    """Sum CRIF AmountUSD values."""
    total = float(crif["AmountUSD"].sum())
    logger.debug("Summed sensitivities: %s", total)
    return total


# Extract tenors as a list from CRIF
def tenor_list(crif) -> List[str]:
    """Extract SIMM tenors from Label1 values."""
    label_1 = crif["Label1"].tolist()
    tenors = list({x.lower() for x in label_1 if x and x.lower() in simm_tenor_list})
    logger.debug("Tenors extracted: %s", tenors)
    return tenors


# Extract distict values only from a list or a pandas column
def unique_list(x, column: str | None = None) -> List:
    """Return distinct values from a list or dataframe column while preserving order."""
    if isinstance(x, list):
        seen = set()
        return [y for y in x if not (y in seen or seen.add(y))]

    # pandas.DataFrame
    return x[column].unique().tolist()


# Extract currency pairs from CRIF as a list
def currencyPair_list(crif) -> List[str]:
    """Extract currency pairs from qualifier field, removing duplicates."""
    currency_pair = [x for x in list(crif["Qualifier"]) if (str(x) != "nan" and len(str(x)) == 6)]
    currency_pair_list: List[str] = []

    # Prevent from containing duplicates
    # e.g. KRWUSD is considered to be identical with USDKRW
    for pair in currency_pair:
        if pair[3:] + pair[:3] not in currency_pair_list:
            currency_pair_list.append(pair)

    unique_pairs = list(set(currency_pair_list))
    logger.debug("Currency pairs extracted: %s", unique_pairs)
    return unique_pairs


# Extract product classes from CRIF
def product_list(crif) -> List[str]:
    """Extract distinct product classes from CRIF."""
    product_values = [x for x in list(crif["ProductClass"]) if (str(x) != "nan")]
    return list(set(product_values))


# Extract buckets from CRIF
def bucket_list(df) -> List[int]:
    """Extract distinct bucket values from CRIF, normalizing Residual to 0."""
    if "Residual" in list(df["Bucket"]):
        # Residual goes to 0
        bucket_values = [
            int(x)
            for x in list(df["Bucket"])
            if (str(x) != "nan" and x != "Residual" and x != "Residual")
        ]
        bucket_values.append(0)
    else:
        bucket_values = [int(x) for x in list(df["Bucket"]) if str(x) != "nan"]

    buckets = list(set(bucket_values))
    logger.debug("Buckets extracted: %s", buckets)
    return buckets


# Scaling Function of time t (for Curvature Margin)
def scaling_func(t: str) -> float:
    """Return scaling factor for curvature margin time scaling."""
    t = t.lower()
    if t == "2w":
        return 0.5
    if "m" in t:
        days = (365 / 12) * float(t.replace("m", ""))
        return 0.5 * min(1, 14 / days)
    if "y" in t:
        days = 365 * float(t.replace("y", ""))
        return 0.5 * min(1, 14 / days)
    raise ValueError(f"Unknown tenor format: {t}")
