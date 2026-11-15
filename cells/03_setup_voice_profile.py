# ==============================================================================
# 🎙️ CELL 3: Setup Calibrated Voice Profile (P_J_N_Reddy_RealVoice)
# Automatically registers your clean 8.35s Telugu voice sample into VoiceStudio.
# Portable across ANY Google account — no manual file upload required!
# ==============================================================================
import os, sys, time, base64, requests

# Import embedded voice bytes from assets (or restore from base64)
VOICE_DIR = "/content/colab-voice-studio/assets"
WAV_PATH = "/content/p_j_n_reddy_ref.wav"
TRANSCRIPT = "మీరు ఎప్పుడైనా సూపర్ మార్కెట్ లోకి వెళ్లారా? అక్కడ క్యాషియర్ దగ్గర మూడు ఆపిల్స్ ఉంటే, వాటిని చూడగానే మూడు అని చెప్పగలరు."

# Restore reference audio from embedded file or local copy
if not os.path.exists(WAV_PATH):
    emb_path = os.path.join(VOICE_DIR, "embedded_voice.py")
    if os.path.exists(emb_path):
        import importlib.util
        spec = importlib.util.spec_from_file_location("embedded_voice", emb_path)
        if spec is not None and spec.loader is not None:
            emb = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(emb)
            ref_b64 = getattr(emb, "REF_AUDIO_B64", "")
            with open(WAV_PATH, "wb") as f:
                f.write(base64.b64decode(ref_b64))
            print(f"✅ Restored reference audio sample to {WAV_PATH} (size: {os.path.getsize(WAV_PATH)} bytes)")
    else:
        # Fallback inline recovery if assets directory is not present
        print("💡 Place your reference WAV file at /content/p_j_n_reddy_ref.wav")

def register_voice_profile():
    BASE_URL = "http://127.0.0.1:3900"
    try:
        # Check if already registered
        resp = requests.get(f"{BASE_URL}/profiles", timeout=10)
        if resp.status_code == 200:
            for p in resp.json():
                if "Reddy" in p.get("name", "") or "Jithendra" in p.get("name", ""):
                    print(f"✅ Active Voice Profile found: {p['name']} (ID: {p['id']})")
                    return p["id"]

        # Register profile
        if os.path.exists(WAV_PATH):
            with open(WAV_PATH, "rb") as f:
                files = {"ref_audio": (os.path.basename(WAV_PATH), f, "audio/wav")}
                data = {
                    "name": "P_J_N_Reddy_RealVoice",
                    "language": "Telugu",
                    "ref_text": TRANSCRIPT,
                    "kind": "clone",
                }
                res = requests.post(f"{BASE_URL}/profiles", data=data, files=files, timeout=60)
                if res.status_code == 200:
                    created = res.json()
                    print(f"🎉 Created Voice Profile: {created['name']} (ID: {created['id']})")
                    return created["id"]
                else:
                    print(f"⚠️ Profile registration notice: {res.text}")
    except Exception as e:
        print(f"Note: Backend will register profile on startup ({e})")
    return None

if __name__ == "__main__" or "google.colab" in sys.modules:
    # If backend is already running, register now:
    register_voice_profile()
