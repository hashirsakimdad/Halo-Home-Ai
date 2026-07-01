# Install (Windows)

## 1) Create venv + install deps

```powershell
cd "D:\HaloHome AI"
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2) Configure env

```powershell
copy .env.example .env
```

## 3) Run setup check

```powershell
python setup_check.py
```

## 4) First run (text mode)

```powershell
python main.py --mode text
```

