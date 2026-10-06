# Implementation Notes

## Rasa NLU

The chatbot uses a CPU-friendly Rasa pipeline based on tokenisation, lexical and count-vector features, DIETClassifier and a fallback classifier. This follows the brief's recommendation to begin with the DIETClassifier because it balances accuracy and latency for a prototype deployment.

## Rasa Core

Rasa Core uses stories and rules to manage dialogue state. Slots persist destination, origin, dates, budget, travellers, sustainability preference and transport mode across turns.

## Custom actions

The main custom action file is `actions/actions.py`.

Key actions:

- `action_collect_missing_trip_info`: adaptive questioning and slot collection.
- `action_calculate_carbon`: estimates emissions using Climatiq if available or fallback factors.
- `action_fetch_transport_options`: compares train, coach, flight and car emissions.
- `action_fetch_hotels`: retrieves Amadeus-style or mock hotel data.
- `action_rank_eco_options`: ranks accommodation by weighted eco-score.
- `action_recommend_cultural_experiences`: returns community-supporting local experiences.
- `action_recommend_offsets`: suggests verified-style offset examples.
- `action_package_handover_context`: prepares a human advisor summary.
- `action_two_stage_clarification`: handles ambiguous input before escalation.

## Weighted eco-score

The ranking model is deliberately transparent:

`Eco-score = 50% carbon impact + 25% budget fit + 25% sustainability preference match`

This is simple enough to explain to users and markers, while still demonstrating applied decision logic.

## Mock data rationale

The brief expects API integration but also recognises that reliable free APIs may be unavailable for some eco-certification and carbon offset data. Therefore, this prototype includes static JSON files as a transparent fallback. The report should explain this as a realistic prototype limitation rather than pretending all data is live.
