# Wake Word

Wake word detection uses **Vosk** (offline, free) in `core/wake_word.py`.

## Configure

- `.env` → `WAKE_WORD` (default `hey holo`)
- `.env` → `VOSK_MODEL_PATH` (folder path)

## Run

Wake word is used in `python main.py --mode voice` (unless `--no-wake-word` is passed).

