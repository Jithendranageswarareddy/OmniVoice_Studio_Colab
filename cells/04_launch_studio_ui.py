# ==============================================================================
# 🌐 CELL 4: Launch VoiceStudio Backend & Open Web UI
# Starts Uvicorn server on port 3900 and opens the browser UI.
# ==============================================================================
import os, sys, time, subprocess, json, urllib.request

REPO_DIR = "/content/VoiceStudio"
PORT = 3900
LOG_PATH = "/content/omnivoice_backend.log"
HEALTH_URL = f"http://127.0.0.1:{PORT}/health"

def health():
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=5) as r:
            return json.load(r)
    except Exception:
        return None

info = health()
if info:
    print(f"✅ VoiceStudio backend is already running: {info}")
else:
    # Kill any stale port process
    subprocess.run(f"kill -9 $(lsof -t -i:{PORT}) 2>/dev/null || true", shell=True)
    time.sleep(1)

    env = os.environ.copy()
    env["OMNIVOICE_SERVER_MODE"] = "1"
    env.setdefault("OMNIVOICE_DATA_DIR", "/content/omnivoice_data")
    env["PYTHONUNBUFFERED"] = "1"

    # Colab Proxy Trust
    try:
        import importlib
        colab_output = importlib.import_module("google.colab.output")
        proxy_url = colab_output.eval_js(f"google.colab.kernel.proxyPort({PORT})")
        from urllib.parse import urlsplit
        parts = urlsplit(str(proxy_url or "").strip())
        origin = f"https://{parts.hostname}" + (f":{parts.port}" if parts.port else "")
        env["OMNIVOICE_ALLOWED_ORIGINS"] = origin
        env["OMNIVOICE_ALLOWED_HOSTS"] = "*"
    except Exception:
        pass

    log = open(LOG_PATH, "ab")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app",
         "--app-dir", "backend", "--host", "127.0.0.1", "--port", str(PORT)],
        cwd=REPO_DIR, env=env, stdout=log, stderr=subprocess.STDOUT,
    )
    print(f"🚀 Starting VoiceStudio backend (PID {proc.pid})...")

    deadline = time.time() + 180
    while time.time() < deadline:
        if proc.poll() is not None:
            break
        info = health()
        if info:
            break
        print(".", end="", flush=True)
        time.sleep(3)
    print()

    if info:
        print(f"🎉 Backend is LIVE! Running on device: {info.get('device', 'cuda')}")
    else:
        print(f"⚠️ Check log file for details: {LOG_PATH}")

# ── Launch Web UI ─────────────────────────────────────────────────────────────
# 1. Native Colab Port Proxy Window
try:
    import importlib
    colab_output = importlib.import_module("google.colab.output")
    colab_output.serve_kernel_port_as_window(PORT)
    print("\n👉 Click the link above to open VoiceStudio Web UI in your browser!")
except Exception as e:
    print(f"Colab window handler: {e}")

# 2. Cloudflare Public HTTPS Tunnel (100% reliable across any browser & mobile)
print("\n🔗 Generating Cloudflare Public Tunnel link (accessible from anywhere)...")
subprocess.run("wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /usr/local/bin/cloudflared && chmod +x /usr/local/bin/cloudflared", shell=True)
subprocess.run(f"nohup cloudflared tunnel --url http://127.0.0.1:{PORT} --no-autoupdate > /content/cloudflared.log 2>&1 &", shell=True)
time.sleep(4)

try:
    tunnel_url = subprocess.run("grep -o 'https://.*trycloudflare.com' /content/cloudflared.log | head -1",
                                shell=True, capture_output=True, text=True).stdout.strip()
    if tunnel_url:
        print(f"\n🌟 PUBLIC WEB STUDIO URL: {tunnel_url}")
        print("   (Open this link in your browser to clone voices immediately!)")
except Exception:
    pass
