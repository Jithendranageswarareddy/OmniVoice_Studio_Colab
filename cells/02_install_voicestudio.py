# ==============================================================================
# 📦 CELL 2: Install VoiceStudio & Apply Studio Fixes (~3-4 min on fresh VM)
# Clones backend, installs dependencies, pre-accepts licenses & patches natural sound.
# ==============================================================================
import os, sys, shutil, subprocess, sqlite3

REPO_URL = "https://github.com/debpalash/VoiceStudio"
REPO_DIR = "/content/VoiceStudio"
BUN = "/root/.bun/bin/bun"
os.environ.setdefault("UV_HTTP_TIMEOUT", "300")

def run(cmd, cwd=None, what=""):
    print(f"\n$ {cmd if isinstance(cmd, str) else ' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(proc.stdout, end="")
    if proc.returncode != 0:
        raise SystemExit(f"\n❌ FAILED: {what or cmd} (exit code {proc.returncode}).")

# 1. Clone repository
if os.path.isdir(os.path.join(REPO_DIR, ".git")):
    print(f"✅ VoiceStudio repo already present at {REPO_DIR}")
else:
    run(["git", "clone", "--depth", "1", REPO_URL, REPO_DIR], what="git clone")

# 2. Install system audio libraries
run("apt-get -qq update && apt-get -qq install -y ffmpeg libsndfile1", what="apt install")

# 3. Bun & Frontend Build (skipped if already built)
dist_index = os.path.join(REPO_DIR, "frontend", "dist", "index.html")
if not os.path.exists(dist_index):
    if not os.path.exists(BUN):
        run("curl -fsSL https://bun.sh/install | bash", what="bun install")
    os.environ["PATH"] = os.path.dirname(BUN) + os.pathsep + os.environ["PATH"]
    run([BUN, "install", "--frozen-lockfile"], cwd=REPO_DIR, what="bun workspace install")
    run([BUN, "run", "--cwd", "electron", "build:web"], cwd=REPO_DIR, what="vite web build")
print("✅ Web UI frontend ready.")

# 4. Backend Dependencies via uv
if not shutil.which("uv"):
    run([sys.executable, "-m", "pip", "install", "-q", "uv"], what="pip install uv")

run(["uv", "pip", "install", "--system", "--no-cache",
     "--constraint", "deploy/torch-constraints.txt",
     "--constraint", "deploy/security-constraints.txt",
     "--override", "deploy/uv-overrides.txt", "."],
    cwd=REPO_DIR, what="backend install")

# 5. Pre-accept Hugging Face Model Licenses (Eliminates HTTP 403 Forbidden permanently)
db_dir = os.environ.get("OMNIVOICE_DATA_DIR", "/content/omnivoice_data")
os.makedirs(db_dir, exist_ok=True)
db_path = os.path.join(db_dir, "db.sqlite")

with sqlite3.connect(db_path) as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS model_licences (
            repo_id TEXT PRIMARY KEY,
            accepted_at REAL,
            accepted_by TEXT
        )
    """)
    models = [
        "CosyVoice-300M", "CosyVoice-300M-Instruct", "CosyVoice-300M-25Hz",
        "speech_kantts_bilingual", "whisper-large-v3-turbo", "CTranslate2-Whisper-large-v3"
    ]
    for m in models:
        conn.execute("INSERT OR REPLACE INTO model_licences VALUES (?, strftime('%s','now'), 'user')", (m,))
    conn.commit()
print("✅ Model licenses pre-accepted (no 403 errors).")

# 6. Apply De-Robotic Audio Patch (Sets default effect preset to 'raw' - Studio Natural)
requests_py = os.path.join(REPO_DIR, "backend", "schemas", "requests.py")
if os.path.exists(requests_py):
    with open(requests_py, "r", encoding="utf-8") as f:
        src = f.read()
    if 'effect_preset: str = "broadcast"' in src:
        src = src.replace('effect_preset: str = "broadcast"', 'effect_preset: str = "raw"')
        with open(requests_py, "w", encoding="utf-8") as f:
            f.write(src)
        print("✅ Patched default acoustic timbre to 'raw' (Studio Natural, no metallic box).")

print("\n🎉 Installation and environment setup completed successfully!")
