# Health Check

When running API mode, use:

```powershell
curl http://localhost:8000/health
```

Status is `healthy` when Ollama responds; otherwise it returns `degraded` (but HoloHome should still respond with offline fallback text).

