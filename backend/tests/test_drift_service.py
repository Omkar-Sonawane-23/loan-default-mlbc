import math

from app.services.drift_service import drift_band, population_stability_index


def test_psi_is_zero_for_identical_distributions():
    sample = [0.01, 0.1, 0.2, 0.4, 0.5, 0.7, 0.9]
    psi = population_stability_index(sample, sample)
    assert psi is not None
    assert abs(psi) < 1e-10


def test_psi_detects_distribution_shift_and_stays_finite():
    reference = [0.05 + i * 0.01 for i in range(50)]
    current = [0.7 + i * 0.005 for i in range(50)]
    psi = population_stability_index(reference, current)
    assert psi is not None and math.isfinite(psi) and psi > 0.25
    assert drift_band(psi) == "HIGH"


def test_psi_empty_or_constant_baseline_is_unavailable():
    assert population_stability_index([], [0.1]) is None
    assert population_stability_index([0.2] * 20, [0.1, 0.3]) is None
    assert drift_band(None) == "INSUFFICIENT_DATA"
