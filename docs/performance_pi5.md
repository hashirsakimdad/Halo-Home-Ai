# Performance Notes (Raspberry Pi 5)

Guidelines:

- Prefer small models (`llama3.2:1b`)
- Use `WHISPER_MODEL=base` or smaller (`tiny`) if latency is high
- Keep wake word detection lightweight (separate thread/process)

