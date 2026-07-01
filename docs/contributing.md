# Contributing

## Principles

- Local-only, free stack (no paid APIs)
- Modular agents; shared wrappers for LLM + memory
- Prefer small, reviewable commits

## Development loop

```powershell
python setup_check.py
pytest -v
python main.py --mode text
```

