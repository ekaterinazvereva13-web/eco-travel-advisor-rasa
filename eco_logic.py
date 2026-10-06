"""Pure helper functions for the Eco-Travel Advisor action server.

These functions are kept independent from Rasa SDK so they can be unit-tested with pytest.
Values are approximate and intended for prototype-level comparison, not audited carbon accounting.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

# Approximate passenger kgCO2e per km values for prototype comparisons.
# Real deployment should replace these with verified factors from a carbon API.
EMISSION_FACTORS_KG_PER_KM = {
    "flight": 0.180,
    "car": 0.120,
    "coach": 0.035,
    "train": 0.028,
    "public_transport": 0.045,
    "cycling": 0.000,
    "walking": 0.000,
}

DEFAULT_ROUTE_DISTANCES_KM = {
    ("london", "berlin"): 930,
    ("london", "barcelona"): 1140,
    ("london", "lisbon"): 1585,
    ("london", "edinburgh"): 640,
    ("manchester", "berlin"): 1050,
    ("leeds", "edinburgh"): 330,
}


def normalise_text(value: Optional[str]) -> str:
    """Normalise user-provided text for matching."""
    return (value or "").strip().lower()


def estimate_distance_km(origin: Optional[str], destination: Optional[str]) -> float:
    """Return an approximate route distance in km from static fallback data."""
    origin_key = normalise_text(origin)
    destination_key = normalise_text(destination)
    if (origin_key, destination_key) in DEFAULT_ROUTE_DISTANCES_KM:
        return float(DEFAULT_ROUTE_DISTANCES_KM[(origin_key, destination_key)])
    if (destination_key, origin_key) in DEFAULT_ROUTE_DISTANCES_KM:
        return float(DEFAULT_ROUTE_DISTANCES_KM[(destination_key, origin_key)])
    # conservative fallback for an international city break
    return 800.0


def estimate_carbon_kg(distance_km: float, mode: str, travellers: float = 1.0) -> float:
    """Estimate kgCO2e for a transport mode and number of travellers."""
    mode_key = normalise_text(mode) or "train"
    factor = EMISSION_FACTORS_KG_PER_KM.get(mode_key, EMISSION_FACTORS_KG_PER_KM["train"])
    travellers = max(float(travellers or 1.0), 1.0)
    return round(distance_km * factor * travellers, 2)


def carbon_band(kgco2e: float, travellers: float = 1.0) -> str:
    """Classify emissions into a UI band."""
    per_person = kgco2e / max(float(travellers or 1.0), 1.0)
    if per_person <= 40:
        return "green"
    if per_person <= 140:
        return "amber"
    return "red"


def parse_budget_level(budget: Optional[str]) -> str:
    """Map free-text budgets to broad levels."""
    b = normalise_text(budget)
    if any(term in b for term in ["premium", "luxury", "high"]):
        return "premium"
    if any(term in b for term in ["mid", "medium", "moderate"]):
        return "mid-range"
    if any(term in b for term in ["cheap", "low", "budget", "£", "pound", "euro"]):
        return "budget"
    return "mid-range"


def budget_score(option_price_level: str, user_budget: Optional[str]) -> float:
    """Score price alignment from 0 to 100."""
    user = parse_budget_level(user_budget)
    option = parse_budget_level(option_price_level)
    if user == option:
        return 100.0
    if user == "premium" and option in {"mid-range", "budget"}:
        return 80.0
    if user == "mid-range" and option in {"budget", "premium"}:
        return 70.0
    if user == "budget" and option == "mid-range":
        return 65.0
    return 40.0


def carbon_score_from_band(band: str) -> float:
    """Convert carbon band to a numeric score."""
    return {"green": 100.0, "amber": 65.0, "red": 25.0}.get(normalise_text(band), 50.0)


def preference_match_score(option_tags: Iterable[str], sustainability_level: Optional[str]) -> float:
    """Score how well an option matches the sustainability preference."""
    level = normalise_text(sustainability_level) or "medium"
    tags = {normalise_text(t) for t in option_tags}
    strong_tags = {"eco-certified", "renewable energy", "zero waste", "local community", "rail access", "low carbon"}
    moderate_tags = {"public transport", "recycling", "bike rental", "local food", "walking tour"}
    if level == "high":
        return 100.0 if tags & strong_tags else 70.0 if tags & moderate_tags else 45.0
    if level == "low":
        return 80.0 if tags else 60.0
    return 90.0 if tags & (strong_tags | moderate_tags) else 55.0


def weighted_eco_score(option: Dict[str, Any], user_budget: Optional[str], sustainability_level: Optional[str]) -> float:
    """Calculate transparent weighted eco-score.

    Formula:
    50% carbon impact + 25% budget alignment + 25% preference match.
    """
    carbon = carbon_score_from_band(option.get("carbon_band", "amber"))
    price = budget_score(option.get("price_level", "mid-range"), user_budget)
    pref = preference_match_score(option.get("tags", []), sustainability_level)
    return round((0.50 * carbon) + (0.25 * price) + (0.25 * pref), 1)


def rank_options(options: List[Dict[str, Any]], user_budget: Optional[str], sustainability_level: Optional[str]) -> List[Dict[str, Any]]:
    """Return options ranked by weighted eco-score."""
    ranked = []
    for option in options:
        enriched = dict(option)
        enriched["eco_score"] = weighted_eco_score(enriched, user_budget, sustainability_level)
        ranked.append(enriched)
    return sorted(ranked, key=lambda item: item["eco_score"], reverse=True)


def build_handover_summary(slots: Dict[str, Any], latest_message: str = "") -> Dict[str, Any]:
    """Package key context for a human travel advisor."""
    return {
        "destination": slots.get("destination"),
        "origin": slots.get("origin"),
        "travel_dates": slots.get("travel_dates"),
        "budget": slots.get("budget"),
        "travelers": slots.get("travelers") or 1,
        "sustainability_level": slots.get("sustainability_level") or "medium",
        "transport_mode": slots.get("transport_mode"),
        "last_carbon_estimate": slots.get("last_carbon_estimate"),
        "latest_message": latest_message,
        "handover_reason": "User requested human advisor or automated clarification was insufficient.",
    }
