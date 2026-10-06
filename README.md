# Eco-Travel Advisor — Rasa Conversational Agent

This repository is a complete implementation pack for the MSc Advanced Conversational UI Design and Chatbot Development set exercise: **Eco-Travel Advisor – Conversational Agent for Sustainable Tourism Planning using the Rasa Platform**.

The project implements a Rasa Open Source chatbot that supports sustainable tourism planning through multi-turn dialogue, approximate carbon footprint calculation, eco-friendly accommodation/activity recommendations, weighted eco-scoring, fallback clarification, and human handover with conversation context.

## 1. What is included

```text
eco_travel_advisor_rasa_pack/
├── actions/
│   ├── actions.py                  # Rasa custom actions
│   ├── eco_logic.py                # Pure Python scoring/carbon helper functions
│   ├── requirements-actions.txt    # Dependencies for action server
│   └── mock_data/                  # Curated static fallback/mock databases
├── data/
│   ├── nlu.yml                     # Intents, entities and examples
│   ├── rules.yml                   # Rules, fallback and handover logic
│   └── stories.yml                 # Multi-turn dialogue paths
├── frontend/
│   ├── index.html                  # Vanilla HTML/JS chat UI using Rasa REST channel
│   ├── app.js                      # Renders bot messages, buttons and colour-coded cards
│   └── styles.css                  # Accessible UI styling
├── tests/
│   ├── test_stories.yml            # Rasa Core test stories
│   └── test_eco_logic.py           # Pytest tests for scoring/carbon functions
├── docs/
│   ├── requirements_matrix.md
│   ├── conversation_flows.md
│   ├── implementation_notes.md
│   ├── testing_and_evaluation_plan.md
│   ├── deployment_guide.md
│   ├── evidence_checklist.md
│   └── report_writing_skeleton.md
├── config.yml                      # Rasa NLU pipeline and policies
├── domain.yml                      # Intents, entities, slots, responses and actions
├── credentials.yml                 # REST channel enabled
├── endpoints.yml                   # Action server endpoint
├── docker-compose.yml              # Rasa + action server + frontend
├── Dockerfile.frontend             # Simple Nginx frontend container
├── .env.example                    # Environment variables template
└── .gitignore
```

## 2. Recommended local setup

Install Python 3.10 or 3.11. Rasa 3.x is recommended for this pack.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install rasa==3.6.20
pip install -r actions/requirements-actions.txt
```

Train the model:

```bash
rasa train
```

Run the action server:

```bash
rasa run actions --actions actions
```

In another terminal, run the chatbot server:

```bash
rasa run --enable-api --cors "*" --debug
```

Open the frontend:

```bash
cd frontend
python -m http.server 3000
```

Then visit: `http://localhost:3000`

## 3. Docker setup

Copy `.env.example` to `.env` and add API keys if available. The chatbot will still work with mock data if API keys are not provided.

```bash
cp .env.example .env
docker compose up --build
```

Frontend: `http://localhost:3000`  
Rasa server: `http://localhost:5005`  
Action server: `http://localhost:5055`

## 4. API keys and fallback behaviour

The assignment brief expects API integration with Climatiq and Amadeus. This pack supports those keys through environment variables:

```bash
CLIMATIQ_API_KEY=your_key_here
AMADEUS_CLIENT_ID=your_id_here
AMADEUS_CLIENT_SECRET=your_secret_here
```

When keys are missing, failed, or rate-limited, the bot uses a curated mock JSON database. This is documented because reliable free APIs for eco-certified hotels, real-time certification data and carbon offset data may be limited.

## 5. Testing commands

```bash
rasa test nlu --cross-validation --folds 5
rasa test core --stories tests/test_stories.yml
pytest tests/test_eco_logic.py
```

Save screenshots of these outputs for the report.

## 6. Suggested GitHub submission checklist

- Upload this full folder to GitHub.
- Keep `.env` out of GitHub.
- Include `.env.example`.
- Include screenshots in a `/report_screenshots` folder.
- Add the GitHub link in the final report.

## 7. Academic note

Use this implementation as the practical basis for the report. The report still needs academic analysis, citations and critical reflection. Do not claim that live APIs were used if you only used mock data; state that the architecture supports live APIs but fallback mock data was used where keys/free access were unavailable.
