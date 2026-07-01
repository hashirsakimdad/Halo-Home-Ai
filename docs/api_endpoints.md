# API Endpoints

When running `python main.py --mode api`:

- `GET /health`: basic status + Ollama reachability
- `POST /chat`: send `{ "message": "...", "context": { ... } }`

