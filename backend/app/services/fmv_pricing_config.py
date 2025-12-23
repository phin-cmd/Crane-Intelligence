"""
Centralized FMV pricing & tier configuration.

Single source of truth for:
- Public pricing for Spot Check, Professional, and Fleet Valuation
- Tier display labels and behavioral flags
- Base currency (currently USD-only, but structured for future multi-currency)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Union

from ..models.fmv_report import FMVReportType


BASE_CURRENCY = "USD"


@dataclass(frozen=True)
class FMVTierConfig:
    code: str  # internal string key, e.g. "spot_check"
    display_name: str  # e.g. "Spot Check"
    subtitle: str
    price_cents: Optional[int]  # None for dynamically priced tiers
    min_units: int  # logical min units supported by this tier
    max_units: int  # logical max units supported by this tier
    internal_only: bool  # whether language/output must be internal-only
    has_deal_score: bool
    has_wear_score: bool
    has_signature: bool
    has_regional_commentary: bool


TIERS_BY_CODE: Dict[str, FMVTierConfig] = {
    # Spot Check — $250, Internal FMV Snapshot
    "spot_check": FMVTierConfig(
        code="spot_check",
        display_name="Spot Check",
        subtitle="Internal FMV Snapshot",
        price_cents=25000,
        min_units=1,
        max_units=5,
        internal_only=True,
        has_deal_score=False,
        has_wear_score=False,
        has_signature=False,
        has_regional_commentary=False,
    ),
    # Professional — $995, Defensible Valuation Report
    "professional": FMVTierConfig(
        code="professional",
        display_name="Professional",
        subtitle="Defensible Valuation Report",
        price_cents=99500,
        min_units=1,
        max_units=1,
        internal_only=False,
        has_deal_score=True,
        has_wear_score=True,
        has_signature=True,
        has_regional_commentary=True,
    ),
    # Fleet Valuation — from $1,495, Multi-Unit Portfolio Valuation
    "fleet_valuation": FMVTierConfig(
        code="fleet_valuation",
        display_name="Fleet Valuation",
        subtitle="Multi-Unit Portfolio Valuation",
        price_cents=None,  # dynamic, tiered pricing
        min_units=2,
        max_units=50,
        internal_only=False,
        has_deal_score=True,
        has_wear_score=True,
        has_signature=True,
        has_regional_commentary=True,
    ),
}


def _normalize_type(report_type: Union[str, FMVReportType]) -> str:
    if isinstance(report_type, FMVReportType):
        return report_type.value
    return str(report_type).lower().strip()


def get_tier_config(report_type: Union[str, FMVReportType]) -> FMVTierConfig:
    """
    Resolve a tier configuration from either a string key or FMVReportType enum.
    Defaults to Professional if an unknown code is passed.
    """
    key = _normalize_type(report_type)
    return TIERS_BY_CODE.get(key, TIERS_BY_CODE["professional"])


def get_base_price_cents(
    report_type: Union[str, FMVReportType],
    unit_count: Optional[int] = None,
) -> int:
    """
    Get the base price for a given tier in cents.

    For Fleet Valuation, this uses the tiered pricing model based on unit_count:
      1–5:   $1,495
      6–10:  $2,495
      11–25: $4,995
      26–50: $7,995
    For Spot Check and Professional, it uses the fixed price from the config.
    """
    cfg = get_tier_config(report_type)

    # Fixed-price tiers
    if cfg.code in ("spot_check", "professional"):
        if cfg.price_cents is None:
            raise ValueError(f"Price not configured for tier {cfg.code}")
        return cfg.price_cents

    # Fleet Valuation: dynamic tiered pricing
    if cfg.code == "fleet_valuation":
        if unit_count is None:
            # Use lowest tier as the public "from" price if no unit_count provided
            return 1495_00
        if unit_count < 1 or unit_count > 50:
            raise ValueError("Fleet Valuation supports 1-50 cranes")

        if unit_count <= 5:
            return 1495_00
        elif unit_count <= 10:
            return 2495_00
        elif unit_count <= 25:
            return 4995_00
        else:
            return 7995_00

    raise ValueError(f"Unknown report type: {report_type}")


def get_base_price_dollars(
    report_type: Union[str, FMVReportType],
    unit_count: Optional[int] = None,
) -> float:
    """Helper to get base price in dollars, for legacy callers and UI defaults."""
    cents = get_base_price_cents(report_type, unit_count=unit_count)
    return round(cents / 100.0, 2)

