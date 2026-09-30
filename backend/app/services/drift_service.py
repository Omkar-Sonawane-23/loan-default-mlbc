"""Small, auditable population stability utilities for model monitoring."""
from __future__ import annotations

import numpy as np


def population_stability_index(reference, current, bins: int = 10) -> float | None:
    """Calculate PSI for numeric samples using reference-derived quantile bins.

    Returns None when either sample is empty/constant; bins are clipped away
    from zero to keep the statistic finite. This is a screening signal, not a
    statistical test or proof that model quality changed.
    """
    ref = np.asarray(reference, dtype=float)
    cur = np.asarray(current, dtype=float)
    ref, cur = ref[np.isfinite(ref)], cur[np.isfinite(cur)]
    if ref.size == 0 or cur.size == 0 or np.unique(ref).size < 2:
        return None
    edges = np.unique(np.quantile(ref, np.linspace(0, 1, bins + 1)))
    if edges.size < 2:
        return None
    edges[0], edges[-1] = -np.inf, np.inf
    ref_counts, _ = np.histogram(ref, bins=edges)
    cur_counts, _ = np.histogram(cur, bins=edges)
    ref_pct = np.clip(ref_counts / ref.size, 1e-6, None)
    cur_pct = np.clip(cur_counts / cur.size, 1e-6, None)
    return float(np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct)))


def drift_band(psi: float | None) -> str:
    """Conventional PSI screening bands; thresholds are configurable policy."""
    if psi is None:
        return "INSUFFICIENT_DATA"
    if psi < 0.1:
        return "LOW"
    if psi < 0.25:
        return "MODERATE"
    return "HIGH"
