# Report Writing Skeleton — 2,500 to 3,000 words

## Title

Eco-Travel Advisor: A Rasa-Based Conversational Agent for Sustainable Tourism Planning

## 1. Introduction — 250 to 300 words

Introduce sustainable tourism planning, the problem of confusing environmental information, and the need for a chatbot that supports low-carbon choices. State that the project develops a Rasa-based Eco-Travel Advisor using multi-turn dialogue, carbon estimation, eco-stay recommendations, cultural experiences and human handover.

## 2. Literature Review and Trend Analysis — 500 to 600 words

Cover:

- Sustainable travel chatbots and digital tourism assistants.
- Conversational UI, NLP and Rasa-style task-oriented dialogue.
- LLMs/multimodal systems as trends, but explain why Rasa is more transparent and controllable for this assignment.
- Persuasive UX and behaviour change through comparison, feedback and warnings.
- Ethical issues: greenwashing, transparency, privacy, accessibility and inclusivity.

End with the gap: many travel bots optimise convenience and price, while fewer combine carbon transparency, sustainable recommendations, fallback explanations and human handover.

## 3. Requirements Analysis — 350 to 450 words

Use the table in `docs/requirements_matrix.md`. Explain functional and non-functional requirements. Mention latency, GDPR, accessibility and reliability under API failure.

## 4. Conversational UI and Prototype Design — 450 to 550 words

Discuss:

- User journey.
- Three scenarios: city break, rural/eco trip, business trip.
- Quick replies, cards, colour coding, warnings and handover indicator.
- How the design reduces cognitive load.
- Why carbon estimates include disclaimers.

Insert screenshots of the frontend and conversation flow diagrams.

## 5. Rasa Implementation and NLP Design — 650 to 750 words

Discuss:

- Rasa NLU intents/entities.
- Slots for destination, origin, dates, budget, sustainability level and transport mode.
- DIETClassifier pipeline and fallback classifier.
- Stories/rules for dialogue management.
- Custom actions in `actions.py`.
- Climatiq and Amadeus API wrappers plus mock fallback.
- Weighted eco-score formula.

## 6. Testing and Evaluation — 400 to 500 words

Include:

- NLU test method and results.
- Core dialogue test method and results.
- Unit tests for scoring/carbon logic.
- User testing method and feedback, if completed.
- Limitations and design changes after testing.

## 7. Deployment and Professional Documentation — 250 to 350 words

Explain:

- Local deployment.
- Docker Compose.
- HuggingFace Spaces recommendation.
- Environment variables.
- Secure endpoint/API-key handling.
- GitHub documentation and README.

## 8. Ethics, Privacy and Sustainability Reflection — 250 to 300 words

Discuss:

- Avoiding greenwashing.
- Approximate estimates and transparent limitations.
- GDPR principles and data minimisation.
- Accessibility and inclusive design.
- Human handover for complex cases.

## 9. Conclusion — 150 to 200 words

Summarise the completed chatbot, key learning outcomes and future improvements such as live verified eco-certification APIs, multilingual voice input and deeper route optimisation.

## References

Use Harvard referencing. Avoid Wikipedia/UKEssays. Recommended source types:

- Rasa documentation.
- Conversational UI and chatbot academic papers.
- Sustainable tourism and carbon footprint literature.
- GDPR/privacy sources.
- Accessibility/WCAG guidance.
- Climatiq and Amadeus developer documentation.
