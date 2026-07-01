# Tests

Run all tests:

```powershell
cd "D:\HaloHome AI"
. .venv\Scripts\Activate.ps1
pytest -v
```

Tests avoid requiring voice dependencies by keeping heavy imports lazy.

