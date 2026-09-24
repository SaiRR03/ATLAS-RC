"""Inference and applicability controls for the ATLAS-RC2 public demonstrator.

The public demonstrator predicts *reported/announced investment*. It does not
predict verified construction outturn cost.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTEFACT = ROOT / "artefacts" / "atlas_rc2.joblib"


@lru_cache(maxsize=1)
def load_bundle(path: str | Path = DEFAULT_ARTEFACT) -> dict:
    return joblib.load(path)


def _money(value: float) -> str:
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:,.2f}bn"
    if value >= 1_000_000:
        return f"${value / 1_000_000:,.1f}m"
    return f"${value:,.0f}"


def estimate_investment(
    capacity_mw: float,
    floor_area_sqft: float | None = None,
    state: str | None = None,
    announced_year: int | None = None,
    artefact_path: str | Path = DEFAULT_ARTEFACT,
) -> dict:
    """Estimate a central benchmark and an ~80% marginal conformal interval."""
    if not np.isfinite(capacity_mw) or capacity_mw <= 0:
        raise ValueError("Power capacity must be greater than zero.")
    if floor_area_sqft is not None and (
        not np.isfinite(floor_area_sqft) or floor_area_sqft <= 0
    ):
        raise ValueError("Floor area must be greater than zero when supplied.")

    bundle = load_bundle(artefact_path)
    domain = bundle["domain"]
    complete_expanded = (
        floor_area_sqft is not None and state is not None and announced_year is not None
    )
    model_name = "expanded" if complete_expanded else "capacity_only"
    chosen = bundle["models"][model_name]

    row = pd.DataFrame(
        {
            "log_capacity": [np.log(capacity_mw)],
            "log_area": [np.log(floor_area_sqft) if floor_area_sqft else np.nan],
            "state": [state or "Unknown"],
            "announced_year": [announced_year if announced_year else np.nan],
        }
    )
    log_central = float(chosen["pipeline"].predict(row[chosen["columns"]])[0])
    qhat = float(chosen["qhat"])
    lower_80, central, upper_80 = np.exp(
        [log_central - qhat, log_central, log_central + qhat]
    )

    warnings: list[str] = []
    if capacity_mw < domain["capacity_min"] or capacity_mw > domain["capacity_max"]:
        warnings.append("Capacity lies outside the central 98% of the training evidence.")
    if complete_expanded:
        if floor_area_sqft < domain["area_min"] or floor_area_sqft > domain["area_max"]:
            warnings.append("Floor area lies outside the central 98% of the training evidence.")
        if state not in domain["states"]:
            warnings.append("The selected state was not represented in the training evidence.")
        if announced_year < domain["year_min"] or announced_year > domain["year_max"]:
            warnings.append("Announcement year lies outside the observed training period.")
        warnings.append(
            "The expanded specification is experimental: grouped validation did not improve "
            "log-MAE versus the capacity-only specification in this demonstrator."
        )
    else:
        warnings.append(
            "The capacity-only specification was used because area, state and year were not all supplied."
        )

    status = "SUPPORTED"
    if warnings:
        status = "USE WITH CAUTION"
    if capacity_mw < domain["capacity_min"] / 2 or capacity_mw > domain["capacity_max"] * 2:
        status = "OUTSIDE MODEL DOMAIN"

    return {
        "interval_lower_80_usd": float(lower_80),
        "central_usd": float(central),
        "interval_upper_80_usd": float(upper_80),
        "interval_lower_80_usd_per_mw": float(lower_80 / capacity_mw),
        "central_usd_per_mw": float(central / capacity_mw),
        "interval_upper_80_usd_per_mw": float(upper_80 / capacity_mw),
        "formatted": {
            "lower_80": _money(lower_80),
            "central": _money(central),
            "upper_80": _money(upper_80),
            "central_per_mw": _money(central / capacity_mw) + "/MW",
        },
        "applicability": status,
        "warnings": warnings,
        "model_used": model_name,
        "nominal_coverage": chosen["coverage"],
        "model_version": bundle["version"],
        "target": bundle["target"],
    }
