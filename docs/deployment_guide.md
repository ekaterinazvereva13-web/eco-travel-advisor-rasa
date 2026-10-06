# Deployment Guide

## Local deployment

1. Install dependencies.
2. Train Rasa model with `rasa train`.
3. Start the action server with `rasa run actions --actions actions`.
4. Start Rasa server with `rasa run --enable-api --cors "*" --debug`.
5. Serve the frontend from `/frontend` using `python -m http.server 3000`.

## Docker deployment

```bash
cp .env.example .env
docker compose up --build
```

## HuggingFace Spaces deployment approach

For a zero-cost demonstration, use a Docker Space.

Suggested steps:

1. Create a HuggingFace account.
2. Create a new Space using Docker SDK.
3. Upload project files.
4. Add environment variables in Space settings.
5. Use Docker Compose or adapt the Dockerfile to start Rasa, action server and frontend.
6. Test endpoint health.
7. Add the public Space link to the report.

## Security notes

- Do not upload `.env`.
- Use environment variables for API keys.
- Limit logs containing personal travel details.
- Use HTTPS in deployment.
- Explain that the prototype does not persist user profiles.
