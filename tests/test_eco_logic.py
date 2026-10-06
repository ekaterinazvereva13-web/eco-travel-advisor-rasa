from actions.eco_logic import (
    estimate_distance_km,
    estimate_carbon_kg,
    carbon_band,
    weighted_eco_score,
    rank_options,
)


def test_known_distance_london_berlin():
    assert estimate_distance_km("London", "Berlin") == 930.0


def test_train_emissions_are_lower_than_flight():
    distance = 930
    train = estimate_carbon_kg(distance, "train", 1)
    flight = estimate_carbon_kg(distance, "flight", 1)
    assert train < flight


def test_carbon_band_green_for_low_emissions():
    assert carbon_band(25, 1) == "green"


def test_weighted_score_prefers_green_certified_option():
    option = {"carbon_band": "green", "price_level": "mid-range", "tags": ["eco-certified", "renewable energy"]}
    score = weighted_eco_score(option, "mid-range", "high")
    assert score >= 95


def test_rank_options_orders_by_score():
    options = [
        {"name": "High impact", "carbon_band": "red", "price_level": "premium", "tags": []},
        {"name": "Low impact", "carbon_band": "green", "price_level": "budget", "tags": ["eco-certified"]},
    ]
    ranked = rank_options(options, "budget", "high")
    assert ranked[0]["name"] == "Low impact"
