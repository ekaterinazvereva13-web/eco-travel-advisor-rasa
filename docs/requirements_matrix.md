# Requirements Matrix

| ID | Requirement | Type | Implementation Evidence |
|---|---|---|---|
| FR1 | Collect destination, origin, dates, budget and sustainability preference through adaptive multi-turn dialogue. | Functional | `domain.yml` slots, `data/stories.yml`, `action_collect_missing_trip_info` |
| FR2 | Provide location-based recommendations using manual location input. | Functional | `origin` and `destination` slots; fallback distance map in `eco_logic.py` |
| FR3 | Retrieve eco accommodation, transport and cultural experience data. | Functional | `eco_hotels.json`, `cultural_experiences.json`, `ActionFetchHotels`, `ActionRecommendCulturalExperiences` |
| FR4 | Calculate approximate carbon footprint per transport mode. | Functional | `ActionCalculateCarbon`, `estimate_carbon_kg`, Climatiq wrapper/fallback |
| FR5 | Rank options using carbon impact, price and preference match. | Functional | `weighted_eco_score`: 50% carbon, 25% budget, 25% preference |
| FR6 | Escalate complex cases to a human advisor with full context. | Functional | `ActionPackageHandoverContext`, handover UI card |
| FR7 | Handle ambiguous inputs through fallback and two-stage clarification. | Functional | `FallbackClassifier`, RulePolicy fallback, `ActionTwoStageClarification` |
| NFR1 | Usability through clear language, quick replies and result cards. | Non-functional | `frontend/index.html`, `frontend/app.js`, response buttons |
| NFR2 | Response latency target under 3 seconds for critical interactions. | Non-functional | DIETClassifier pipeline, local mock fallback if API calls fail/time out |
| NFR3 | Accessibility and screen-reader support. | Non-functional | HTML semantic structure, `aria-live`, labels, keyboard buttons |
| NFR4 | Reliability under API failure. | Non-functional | Try/except wrappers; fallback JSON data when APIs fail |
| NFR5 | GDPR-conscious data handling. | Non-functional | `.env`, privacy response, no persistent personal data storage in prototype |
