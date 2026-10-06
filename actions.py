from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Text

import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction

try:
    from .eco_logic import (
        carbon_band,
        estimate_carbon_kg,
        estimate_distance_km,
        rank_options,
        build_handover_summary,
    )
except ImportError:  # allows running directly in some Rasa environments
    from eco_logic import (
        carbon_band,
        estimate_carbon_kg,
        estimate_distance_km,
        rank_options,
        build_handover_summary,
    )

DATA_DIR = Path(__file__).resolve().parent / "mock_data"


def load_json(filename: str) -> Any:
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


def slot_value(tracker: Tracker, name: str, default: Any = None) -> Any:
    value = tracker.get_slot(name)
    return value if value not in [None, ""] else default


def travellers_value(tracker: Tracker) -> float:
    try:
        return max(float(slot_value(tracker, "travelers", 1) or 1), 1.0)
    except (TypeError, ValueError):
        return 1.0


def destination_options_buttons() -> List[Dict[str, str]]:
    return [
        {"title": "Berlin", "payload": '/provide_destination{"destination":"Berlin"}'},
        {"title": "Barcelona", "payload": '/provide_destination{"destination":"Barcelona"}'},
        {"title": "Lisbon", "payload": '/provide_destination{"destination":"Lisbon"}'},
        {"title": "Edinburgh", "payload": '/provide_destination{"destination":"Edinburgh"}'},
    ]


class ActionCollectMissingTripInfo(Action):
    def name(self) -> Text:
        return "action_collect_missing_trip_info"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        destination = slot_value(tracker, "destination")
        origin = slot_value(tracker, "origin")
        dates = slot_value(tracker, "travel_dates")
        budget = slot_value(tracker, "budget")
        sustainability = slot_value(tracker, "sustainability_level")

        if not destination:
            dispatcher.utter_message(
                text="To start, which destination are you considering?",
                buttons=destination_options_buttons(),
            )
            return []
        if not origin:
            dispatcher.utter_message(text=f"Great. Where will you travel from to reach {destination}?")
            return []
        if not dates:
            dispatcher.utter_message(text="What travel dates or trip duration should I use?")
            return []
        if not budget:
            dispatcher.utter_message(
                text="What budget style should I optimise for?",
                buttons=[
                    {"title": "Budget", "payload": '/provide_budget{"budget":"budget"}'},
                    {"title": "Mid-range", "payload": '/provide_budget{"budget":"mid-range"}'},
                    {"title": "Premium", "payload": '/provide_budget{"budget":"premium"}'},
                ],
            )
            return []
        if not sustainability:
            dispatcher.utter_message(
                text="How strongly should I prioritise sustainability?",
                buttons=[
                    {"title": "Lowest carbon", "payload": '/provide_sustainability_preference{"sustainability_level":"high"}'},
                    {"title": "Balanced", "payload": '/provide_sustainability_preference{"sustainability_level":"medium"}'},
                    {"title": "Price first", "payload": '/provide_sustainability_preference{"sustainability_level":"low"}'},
                ],
            )
            return []

        dispatcher.utter_message(
            text=(
                f"Thanks. I will prepare a {sustainability}-sustainability plan for {destination} "
                f"from {origin}, around {dates}, with a {budget} budget."
            )
        )
        return [FollowupAction("action_fetch_transport_options")]


class ActionCalculateCarbon(Action):
    def name(self) -> Text:
        return "action_calculate_carbon"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        origin = slot_value(tracker, "origin", "London")
        destination = slot_value(tracker, "destination", "Berlin")
        travellers = travellers_value(tracker)
        mode = slot_value(tracker, "transport_mode", "train")
        distance_km = estimate_distance_km(origin, destination)

        live_result = self._try_climatiq(distance_km, mode, travellers)
        if live_result:
            kgco2e = live_result["kgco2e"]
            source = "Climatiq API"
        else:
            kgco2e = estimate_carbon_kg(distance_km, mode, travellers)
            source = "prototype fallback factor"

        band = carbon_band(kgco2e, travellers)
        estimate = {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "distance_km": distance_km,
            "travelers": travellers,
            "kgco2e": kgco2e,
            "band": band,
            "source": source,
        }

        dispatcher.utter_message(
            text=(
                f"Estimated emissions for {mode} from {origin} to {destination}: "
                f"{kgco2e:.1f} kgCO2e for {int(travellers)} traveller(s). "
                f"This is a {band} impact estimate using {source}."
            )
        )
        dispatcher.utter_message(
            json_message={
                "type": "carbon_card",
                "title": "Carbon footprint estimate",
                "band": band,
                "items": [
                    {"label": "Route", "value": f"{origin} → {destination}"},
                    {"label": "Mode", "value": mode},
                    {"label": "Distance", "value": f"{distance_km:.0f} km"},
                    {"label": "Estimated emissions", "value": f"{kgco2e:.1f} kgCO2e"},
                    {"label": "Data source", "value": source},
                ],
                "disclaimer": "Prototype estimates are indicative and should not be treated as audited carbon accounting.",
            }
        )
        return [SlotSet("last_carbon_estimate", estimate)]

    def _try_climatiq(self, distance_km: float, mode: str, travellers: float) -> Dict[str, Any] | None:
        api_key = os.getenv("CLIMATIQ_API_KEY")
        if not api_key:
            return None
        # Climatiq endpoints vary by factor; this is a defensive prototype wrapper.
        # If the request fails, the action transparently falls back to local factors.
        try:
            url = "https://beta4.api.climatiq.io/estimate"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "emission_factor": {
                    "activity_id": "passenger_vehicle-vehicle_type_car-fuel_source_na-distance_na-engine_size_na",
                    "data_version": "^6",
                },
                "parameters": {"distance": distance_km, "distance_unit": "km"},
            }
            response = requests.post(url, headers=headers, json=payload, timeout=8)
            response.raise_for_status()
            data = response.json()
            kg = float(data.get("co2e", 0)) * travellers
            if kg > 0:
                return {"kgco2e": round(kg, 2), "raw": data}
        except Exception:
            return None
        return None


class ActionFetchTransportOptions(Action):
    def name(self) -> Text:
        return "action_fetch_transport_options"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        origin = slot_value(tracker, "origin", "London")
        destination = slot_value(tracker, "destination", "Berlin")
        travellers = travellers_value(tracker)
        distance_km = estimate_distance_km(origin, destination)
        modes = ["train", "coach", "flight", "car"]
        cards = []
        for mode in modes:
            kg = estimate_carbon_kg(distance_km, mode, travellers)
            band = carbon_band(kg, travellers)
            cards.append({
                "title": mode.title(),
                "subtitle": f"Approx. {distance_km:.0f} km route",
                "band": band,
                "metrics": {
                    "kgCO2e": f"{kg:.1f}",
                    "Impact": band,
                },
                "recommendation": self._recommendation_text(mode, band),
            })
        dispatcher.utter_message(text=f"Here are indicative transport options for {origin} to {destination}.")
        dispatcher.utter_message(json_message={"type": "result_cards", "title": "Transport comparison", "cards": cards})
        return []

    def _recommendation_text(self, mode: str, band: str) -> str:
        if band == "green":
            return "Recommended lower-emission option where time and accessibility allow."
        if band == "amber":
            return "Moderate-impact option; compare cost and time before choosing."
        return "High-emission option; consider rail/coach or offsetting if unavoidable."


class ActionFetchHotels(Action):
    def name(self) -> Text:
        return "action_fetch_hotels"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        destination = slot_value(tracker, "destination", "Berlin")
        hotels = self._try_amadeus_hotels(destination) or self._mock_hotels(destination)
        dispatcher.utter_message(text=f"I found {len(hotels)} accommodation option(s) for {destination}. I will rank them by carbon impact, price fit and sustainability match.")
        dispatcher.utter_message(json_message={"type": "raw_options", "category": "hotels", "options": hotels})
        return []

    def _mock_hotels(self, destination: str) -> List[Dict[str, Any]]:
        all_hotels = load_json("eco_hotels.json")
        matches = [h for h in all_hotels if h["city"].lower() == destination.lower()]
        return matches or all_hotels[:3]

    def _try_amadeus_hotels(self, destination: str) -> List[Dict[str, Any]] | None:
        client_id = os.getenv("AMADEUS_CLIENT_ID")
        client_secret = os.getenv("AMADEUS_CLIENT_SECRET")
        if not client_id or not client_secret:
            return None
        # Amadeus sandbox integration placeholder: uses mock fallback if token/search fail.
        # For a final live version, map city names to IATA/city codes and call the hotel search endpoint.
        try:
            token_response = requests.post(
                "https://test.api.amadeus.com/v1/security/oauth2/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
                timeout=8,
            )
            token_response.raise_for_status()
            # Keeping mock fallback because the sandbox hotel endpoint may not include eco-certification.
            return None
        except Exception:
            return None


class ActionRankEcoOptions(Action):
    def name(self) -> Text:
        return "action_rank_eco_options"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        destination = slot_value(tracker, "destination", "Berlin")
        budget = slot_value(tracker, "budget", "mid-range")
        sustainability = slot_value(tracker, "sustainability_level", "medium")
        hotels = [h for h in load_json("eco_hotels.json") if h["city"].lower() == destination.lower()]
        if not hotels:
            hotels = load_json("eco_hotels.json")[:3]
        ranked = rank_options(hotels, budget, sustainability)
        cards = []
        for item in ranked[:3]:
            cards.append({
                "title": item["name"],
                "subtitle": f"{item['city']} · {item['price_level']} · Eco-score {item['eco_score']}/100",
                "band": item.get("carbon_band", "amber"),
                "metrics": {
                    "Certification": item.get("certification", "Self-declared"),
                    "Price": item.get("price_level", "mid-range"),
                    "Eco-score": f"{item['eco_score']}/100",
                },
                "recommendation": item.get("description", "Sustainable accommodation option."),
            })
        dispatcher.utter_message(text="I ranked the accommodation options using 50% carbon impact, 25% price fit and 25% sustainability preference match.")
        dispatcher.utter_message(json_message={"type": "result_cards", "title": "Ranked eco-stay recommendations", "cards": cards})
        return []


class ActionRecommendCulturalExperiences(Action):
    def name(self) -> Text:
        return "action_recommend_cultural_experiences"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        destination = slot_value(tracker, "destination", "Berlin")
        experiences = [e for e in load_json("cultural_experiences.json") if e["city"].lower() == destination.lower()]
        if not experiences:
            experiences = load_json("cultural_experiences.json")[:3]
        cards = [{
            "title": e["name"],
            "subtitle": f"{e['city']} · {e['duration']} · {e['price_level']}",
            "band": "green",
            "metrics": {"Community benefit": e["community_benefit"], "Accessibility": e["accessibility"]},
            "recommendation": e["description"],
        } for e in experiences[:3]]
        dispatcher.utter_message(text=f"These cultural experiences in {destination} are selected because they support local communities and avoid high-emission activities.")
        dispatcher.utter_message(json_message={"type": "result_cards", "title": "Local cultural experiences", "cards": cards})
        return []


class ActionRecommendOffsets(Action):
    def name(self) -> Text:
        return "action_recommend_offsets"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        offsets = load_json("carbon_offsets.json")
        cards = [{
            "title": o["name"],
            "subtitle": o["standard"],
            "band": "green",
            "metrics": {"Project type": o["project_type"], "Region": o["region"]},
            "recommendation": o["note"],
        } for o in offsets[:3]]
        dispatcher.utter_message(text="Offsetting should be secondary to reducing emissions first. Here are examples of verified-style climate contribution options for the prototype.")
        dispatcher.utter_message(json_message={"type": "result_cards", "title": "Carbon offset examples", "cards": cards})
        return []


class ActionPackageHandoverContext(Action):
    def name(self) -> Text:
        return "action_package_handover_context"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        summary = build_handover_summary(tracker.current_slot_values(), tracker.latest_message.get("text", ""))
        dispatcher.utter_message(text="I have prepared the trip context for a human travel advisor. A specialist can continue without asking you to repeat the same details.")
        dispatcher.utter_message(json_message={"type": "handover", "title": "Human advisor handover package", "summary": summary})
        return [SlotSet("handover_requested", True)]


class ActionTwoStageClarification(Action):
    def name(self) -> Text:
        return "action_two_stage_clarification"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        count = int(slot_value(tracker, "clarification_count", 0) or 0) + 1
        if count >= 2:
            dispatcher.utter_message(text="I am still not confident I understood. I can transfer this to a human advisor with the conversation context.")
            dispatcher.utter_message(buttons=[{"title": "Human advisor", "payload": "/request_human_handover"}, {"title": "Restart planning", "payload": "/plan_trip"}])
            return [SlotSet("clarification_count", count)]
        dispatcher.utter_message(
            text="I am not fully sure which travel task you need. Please choose one option.",
            buttons=[
                {"title": "Plan trip", "payload": "/plan_trip"},
                {"title": "Compare transport", "payload": "/ask_transport_options"},
                {"title": "Eco hotels", "payload": "/ask_accommodation"},
                {"title": "Carbon estimate", "payload": "/ask_carbon_footprint"},
                {"title": "Human advisor", "payload": "/request_human_handover"},
            ],
        )
        return [SlotSet("clarification_count", count)]


class ActionResetTrip(Action):
    def name(self) -> Text:
        return "action_reset_trip"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="I have cleared the current trip details. We can start again.")
        return [
            SlotSet("destination", None),
            SlotSet("origin", None),
            SlotSet("travel_dates", None),
            SlotSet("budget", None),
            SlotSet("travelers", None),
            SlotSet("sustainability_level", None),
            SlotSet("transport_mode", None),
            SlotSet("activity_type", None),
            SlotSet("last_carbon_estimate", None),
            SlotSet("handover_requested", False),
            SlotSet("clarification_count", 0),
        ]
