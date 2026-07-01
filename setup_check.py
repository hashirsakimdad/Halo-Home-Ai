"""
HoloHome AI — Auto Setup & Health Check
Run this FIRST before anything else.
It will check and install everything automatically.
Usage: python setup_check.py
"""

import importlib
import os
import platform
import shutil
import subprocess
import sys

# Run from project root regardless of caller cwd
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ══════════════════════════════════════════
# COLORS for terminal output
# ══════════════════════════════════════════
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Enable ANSI colors and UTF-8 output on Windows
if platform.system() == "Windows":
    os.system("")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def ok(msg):
    """Print a success message."""
    print(f"{GREEN}[OK] {msg}{RESET}")


def fail(msg):
    """Print a failure message."""
    print(f"{RED}[FAIL] {msg}{RESET}")


def warn(msg):
    """Print a warning message."""
    print(f"{YELLOW}[WARN] {msg}{RESET}")


def info(msg):
    """Print an info message."""
    print(f"{BLUE}[INFO] {msg}{RESET}")


def head(msg):
    """Print a section header."""
    print(f"\n{BOLD}{msg}{RESET}\n" + "-" * 50)


def run_cmd(cmd, capture=True, shell=False):
    """Run a command and return success, stdout, stderr."""
    try:
        if isinstance(cmd, str) and not shell:
            cmd = cmd.split()
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=capture,
            text=True,
            timeout=300,
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)


def pip_install(package, import_name=None):
    """Install a package via pip if not already installed."""
    check_name = import_name or package.split(">=")[0].split("==")[0].replace("-", "_")
    try:
        importlib.import_module(check_name)
        ok(f"{package} — already installed")
        return True
    except ImportError:
        warn(f"{package} — not found, installing...")
        success, out, err = run_cmd(
            [sys.executable, "-m", "pip", "install", package, "-q"]
        )
        if success:
            ok(f"{package} — installed!")
            return True
        fail(f"{package} — FAILED to install: {err[:100]}")
        return False


# ══════════════════════════════════════════
# CHECK 1: Python version
# ══════════════════════════════════════════
head("CHECK 1: Python")
py_version = sys.version_info
if py_version >= (3, 10):
    ok(f"Python {py_version.major}.{py_version.minor}.{py_version.micro}")
else:
    fail(f"Python {py_version.major}.{py_version.minor} — need 3.10+")
    print("  Download from: https://python.org")
    sys.exit(1)

# ══════════════════════════════════════════
# CHECK 2: pip
# ══════════════════════════════════════════
head("CHECK 2: pip")
success, out, _ = run_cmd([sys.executable, "-m", "pip", "--version"])
if success:
    ok(f"pip — {out.strip()[:40]}")
else:
    fail("pip not found — bootstrapping...")
    run_cmd([sys.executable, "-m", "ensurepip", "--upgrade"])
    run_cmd([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "-q"])

# ══════════════════════════════════════════
# CHECK 3: Required Python packages
# ══════════════════════════════════════════
head("CHECK 3: Python packages")

packages = [
    ("httpx>=0.27.0", "httpx"),
    ("pydantic>=2.0.0", "pydantic"),
    ("pydantic-settings", "pydantic_settings"),
    ("python-dotenv", "dotenv"),
    ("fastapi>=0.115.0", "fastapi"),
    ("uvicorn", "uvicorn"),
    ("langgraph>=0.2.0", "langgraph"),
    ("langchain>=0.3.0", "langchain"),
    ("langchain-community", "langchain_community"),
    ("chromadb>=0.5.0", "chromadb"),
    ("requests", "requests"),
    ("paho-mqtt>=2.0.0", "paho"),
]

failed_packages = []
for pkg, imp in packages:
    if not pip_install(pkg, imp):
        failed_packages.append(pkg)

if failed_packages:
    warn(f"{len(failed_packages)} packages failed — try manually:")
    for p in failed_packages:
        print(f"  pip install {p}")
else:
    ok("All core packages ready!")

# ══════════════════════════════════════════
# CHECK 4: Voice packages (optional for Phase 1)
# ══════════════════════════════════════════
head("CHECK 4: Voice packages (Phase 2)")

voice_packages = [
    ("openai-whisper", "whisper"),
    ("sounddevice", "sounddevice"),
    ("scipy", "scipy"),
    ("numpy", "numpy"),
    ("pyttsx3", "pyttsx3"),
    ("pygame", "pygame"),
]

voice_ready = True
for pkg, imp in voice_packages:
    try:
        importlib.import_module(imp)
        ok(f"{pkg} — ready")
    except ImportError:
        warn(f"{pkg} — not installed (needed for Phase 2 voice mode)")
        voice_ready = False

if not voice_ready:
    info("Install voice packages when ready for Phase 2:")
    print("  pip install openai-whisper sounddevice scipy numpy pyttsx3 pygame")

# ══════════════════════════════════════════
# CHECK 5: Ollama
# ══════════════════════════════════════════
head("CHECK 5: Ollama")

ollama_path = shutil.which("ollama")

if ollama_path:
    ok(f"Ollama installed at: {ollama_path}")

    try:
        import httpx

        r = httpx.get("http://localhost:11434/api/tags", timeout=3)
        if r.status_code == 200:
            ok("Ollama server is RUNNING")

            models = r.json().get("models", [])
            model_names = [m["name"] for m in models]
            info(f"Available models: {model_names if model_names else 'none yet'}")

            has_llama = any("llama3.2" in m for m in model_names)
            if has_llama:
                ok("llama3.2 model found!")
            else:
                warn("llama3.2 not found — pull it:")
                print("  ollama pull llama3.2:1b")
        else:
            warn("Ollama installed but server not running")
            print("  Fix: Open new terminal → run: ollama serve")
    except Exception:
        warn("Ollama installed but NOT running")
        print("  Fix: Open new terminal → run: ollama serve")
else:
    fail("Ollama NOT installed")
    print()
    print("  Install Ollama:")
    print("  1. Go to: https://ollama.com/download")
    print("  2. Download OllamaSetup.exe")
    print("  3. BEFORE installing, set D drive:")
    print("     Windows key → search 'Environment Variables'")
    print("     Add new System variable:")
    print("       Name:  OLLAMA_MODELS")
    print("       Value: D:\\ollama-models")
    print("  4. Install Ollama")
    print("  5. Open terminal → ollama serve")
    print("  6. New terminal → ollama pull llama3.2:1b")

# ══════════════════════════════════════════
# CHECK 6: Git
# ══════════════════════════════════════════
head("CHECK 6: Git")

success, out, _ = run_cmd("git --version", shell=True)
if success:
    ok(f"Git — {out.strip()}")

    success2, out2, _ = run_cmd("git remote -v", shell=True)
    if "hashirsakimdad" in out2:
        ok("GitHub repo connected: Halo-Home-Ai")
    else:
        warn("Git remote not set")
        print("  Fix:")
        print("  git remote add origin https://github.com/hashirsakimdad/Halo-Home-Ai.git")
else:
    fail("Git not installed")
    print("  Download: https://git-scm.com/download/win")

# ══════════════════════════════════════════
# CHECK 7: Project structure
# ══════════════════════════════════════════
head("CHECK 7: Project folders & files")

required_dirs = [
    "agents",
    "core",
    "api",
    "config",
    "display",
    "data",
    "logs",
    "tests",
    "data/chroma_db",
    "data/voice_profiles/default",
]

required_files = [
    "main.py",
    "config/settings.py",
    "core/llm.py",
    "core/memory.py",
    "core/orchestrator.py",
    "core/wake_word.py",
    "agents/base_agent.py",
    "agents/voice_agent.py",
    "agents/home_agent.py",
    "agents/education_agent.py",
    "agents/schedule_agent.py",
    "agents/interior_agent.py",
    "agents/security_agent.py",
    "api/server.py",
    "requirements.txt",
]

for d in required_dirs:
    os.makedirs(d, exist_ok=True)
ok("All directories created/verified")

missing_files = []
for f in required_files:
    if os.path.exists(f):
        ok(f"{f}")
    else:
        fail(f"{f} — MISSING")
        missing_files.append(f)

if missing_files:
    warn(f"\n{len(missing_files)} files missing — Cursor will create them")
else:
    ok("All required files present!")

# ══════════════════════════════════════════
# CHECK 8: .env file
# ══════════════════════════════════════════
head("CHECK 8: .env configuration")

if os.path.exists(".env"):
    ok(".env file found")
    with open(".env", encoding="utf-8") as f:
        content = f.read()
    needed = ["OLLAMA_BASE_URL", "OLLAMA_MODEL", "CHROMA_PERSIST_DIR"]
    for key in needed:
        if key in content:
            ok(f"  {key} set")
        else:
            warn(f"  {key} missing from .env")
else:
    warn(".env not found — creating with defaults...")
    env_content = """OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b
OLLAMA_MODELS_PATH=D:\\ollama-models
ACTIVE_VOICE_PROFILE=default
VOICE_LANGUAGE=en
WHISPER_MODEL=base
WAKE_WORD=hey holo
SILENCE_TIMEOUT=2.0
VOSK_MODEL_PATH=data/vosk-model-small-en-us-0.15
CHROMA_PERSIST_DIR=data/chroma_db
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
OFFLINE_MODE=False
"""
    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)
    ok(".env created with defaults!")

# ══════════════════════════════════════════
# CHECK 9: Import test
# ══════════════════════════════════════════
head("CHECK 9: Import all modules")

import_errors = []
modules = [
    "config.settings",
    "core.llm",
    "core.memory",
    "core.orchestrator",
    "agents.base_agent",
    "agents.home_agent",
    "agents.education_agent",
    "agents.schedule_agent",
    "agents.interior_agent",
    "agents.security_agent",
    "api.server",
]

for mod in modules:
    try:
        importlib.import_module(mod)
        ok(mod)
    except Exception as e:
        fail(f"{mod} — {str(e)[:80]}")
        import_errors.append((mod, str(e)))

# ══════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════
head("FINAL SUMMARY")

if not failed_packages and not import_errors and ollama_path:
    print(f"{GREEN}{BOLD}ALL CHECKS PASSED!{RESET}")
    print(f"\n{BOLD}Run HoloHome now:{RESET}")
    print("  1. Open new terminal → ollama serve")
    print("  2. Come back here → python main.py --mode text")
    print("  3. Type anything and talk to HoloHome!")
else:
    print(f"{YELLOW}{BOLD}Some issues found:{RESET}")

    if failed_packages:
        print(f"\n{RED}Failed packages ({len(failed_packages)}):{RESET}")
        for p in failed_packages:
            print(f"  pip install {p}")

    if import_errors:
        print(f"\n{RED}Import errors ({len(import_errors)}) — give these to Cursor to fix:{RESET}")
        for mod, err in import_errors:
            print(f"  {mod}: {err}")

    if not ollama_path:
        print(f"\n{RED}Ollama missing — install from ollama.com/download{RESET}")

    print(f"\n{YELLOW}Fix these issues then run setup_check.py again!{RESET}")

print("\n" + "=" * 50)
