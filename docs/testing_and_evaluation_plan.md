# Testing and Evaluation Plan

## 1. NLU testing

Command:

```bash
rasa test nlu --cross-validation --folds 5
```

Evidence to collect:

- Intent classification report.
- Entity extraction report.
- Confusion matrix screenshot.
- Two misclassification examples and how the training data was improved.

Suggested target:

- F1 score above 0.85 for main intents after refinement.
- Good separation between `plan_trip`, `ask_transport_options`, `ask_accommodation` and `ask_carbon_footprint`.

## 2. Dialogue/Core testing

Command:

```bash
rasa test core --stories tests/test_stories.yml
```

Evidence to collect:

- Passed/failed story outputs.
- Any failed story transition explanation.
- Screenshot of test summary.

## 3. Custom action unit testing

Command:

```bash
pytest tests/test_eco_logic.py
```

Evidence to collect:

- Passing test screenshot.
- Explanation that pure functions were tested separately from Rasa runtime.

## 4. UI/UX testing

Suggested method:

- 3 to 5 participants.
- Think-aloud task: plan a low-carbon weekend trip.
- Short Likert questionnaire from 1 to 5.

Suggested questions:

1. The chatbot questions were clear.
2. The carbon estimate was understandable.
3. The colour-coded cards helped compare options.
4. The sustainability recommendations felt trustworthy.
5. The human handover option was easy to identify.

## 5. Ethics and privacy testing

Check that:

- The bot explains estimates are approximate.
- No API keys are hard-coded.
- `.env` is excluded from GitHub.
- The frontend has accessible labels and keyboard-operable buttons.
- Handover summary only contains necessary travel-planning context.
