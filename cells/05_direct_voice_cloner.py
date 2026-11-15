# ==============================================================================
# ⚡ CELL 5: Direct Voice Cloner (In-Notebook Fast Generator)
# Paste your Telugu script here and hit Run! Output is ready in ~30-45s on GPU.
# ==============================================================================
import requests, os, wave, io, time, subprocess, importlib
import numpy as np
import scipy.signal as signal  # type: ignore

try:
    _disp = importlib.import_module("IPython.display")
    Audio = getattr(_disp, "Audio", None)
    HTML = getattr(_disp, "HTML", None)
    display = getattr(_disp, "display", None)
except Exception:
    Audio = HTML = display = None

BASE_URL = "http://127.0.0.1:3900"

# ── 1. Enter Your Script Below ────────────────────────────────────────────────
SCRIPT_TEXT = """మీరు ఎప్పుడైనా సూపర్ మార్కెట్ కి వెళ్లారా?! అక్కడ క్యాషియర్ దగ్గర మూడు ఆపిల్స్ ఉంటే, వాటిని చూడగానే మూడు అని చెప్పగలరు.
కానీ అదే చోట ఏడు ఆపిల్స్ ఉంటే, వాటిని ఒక్కొక్కటిగా లెక్క పెట్టాల్సి రావచ్చు. 
ఎందుకు ఇలా జరుగుతుంది? మన కళ్ళు ఒకేసారి ఎన్ని వస్తువులని గుర్తించగలవు? 
అసలు లెక్కపెట్టకుండానే వస్తువుల సంఖ్యను గుర్తించడం సాధ్యమేనా? అవును.
దీనికి సంబంధించిన ఒక ఆసక్తికరమైన స్కిల్ గురించి ఇప్పుడు తెలుసుకుందాం... దాని పేరు subitizing!"""

# ── 2. Identify Voice Profile ─────────────────────────────────────────────────
def get_voice_profile():
    try:
        r = requests.get(f"{BASE_URL}/profiles", timeout=10)
        if r.status_code == 200:
            profiles = r.json()
            for p in profiles:
                if "Reddy" in p.get("name", "") or "Jithendra" in p.get("name", ""):
                    return p["id"], p["name"]
            if profiles:
                return profiles[0]["id"], profiles[0]["name"]
    except Exception:
        pass
    return None, None

profile_id, profile_name = get_voice_profile()
print(f"🎙️ Using Cloned Voice: {profile_name} (ID: {profile_id})")

# ── 3. Ultra-Fast GPU Synthesis ───────────────────────────────────────────────
payload = {
    "text": SCRIPT_TEXT.strip(),
    "language": "Telugu",
    "profile_id": profile_id,
    "num_step": 8,           # Studio Realism (8 steps, no phase noise)
    "guidance_scale": 1.3,   # Crisp Telugu plosives without metallic buzz
    "speed": 1.0,            # 1.05 for energetic YouTube hook
    "effect_preset": "raw",  # Pure acoustic vocal timbre
    "wav_bits": "16",
    "stream": "false"
}

t0 = time.time()
print(f"🚀 Generating voiceover on T4 GPU...")
res = requests.post(f"{BASE_URL}/generate", data=payload, timeout=300)
if res.status_code != 200:
    raise RuntimeError(f"Generation error {res.status_code}: {res.text}")

raw_wav_bytes = res.content
gen_duration = time.time() - t0
print(f"✅ Neural generation completed in {gen_duration:.1f} seconds!")

# ── 4. Studio Presence Air Polish & Mastering ────────────────────────────────
with wave.open(io.BytesIO(raw_wav_bytes), "rb") as wf:
    params = wf.getparams()
    audio = np.frombuffer(wf.readframes(params.nframes), dtype=np.int16).astype(np.float32) / 32768.0

# +1.8dB High-shelf presence EQ above 4.5kHz (restores natural vocal brilliance)
gain_db = 1.8
A = 10.0 ** (gain_db / 40.0)
w0 = 2.0 * np.pi * 4500.0 / params.framerate
alpha = np.sin(w0) / 2.0 * np.sqrt(2.0)
cos_w0 = np.cos(w0)

b0 = A * ((A + 1.0) + (A - 1.0) * cos_w0 + 2.0 * np.sqrt(A) * alpha)
b1 = -2.0 * A * ((A - 1.0) + (A + 1.0) * cos_w0)
b2 = A * ((A + 1.0) + (A - 1.0) * cos_w0 - 2.0 * np.sqrt(A) * alpha)
a0 = (A + 1.0) - (A - 1.0) * cos_w0 + 2.0 * np.sqrt(A) * alpha
a1 = 2.0 * ((A - 1.0) - (A + 1.0) * cos_w0)
a2 = (A + 1.0) - (A - 1.0) * cos_w0 - 2.0 * np.sqrt(A) * alpha

b = np.array([b0, b1, b2]) / a0
a = np.array([a0, a1, a2]) / a0
polished = np.clip(signal.lfilter(b, a, audio), -0.98, 0.98)

timestamp = int(time.time())
out_wav = f"/content/voiceover_{timestamp}.wav"
out_mp3 = f"/content/voiceover_{timestamp}.mp3"

with wave.open(out_wav, "wb") as out_wf:
    out_wf.setparams(params)
    out_wf.writeframes((polished * 32767.0).astype(np.int16).tobytes())

# Master to YouTube / Broadcast Standard -16 LUFS MP3
subprocess.run(
    f'ffmpeg -y -i "{out_wav}" -af loudnorm=I=-16:TP=-1.5:LRA=11 -b:a 192k "{out_mp3}" -loglevel error',
    shell=True,
    check=False,
)

audio_dur = len(audio) / params.framerate
print(f"\n🎉 Voiceover Ready! Audio Length: {audio_dur:.2f}s | Saved: {out_mp3}")

# Display Inline Audio Player and Trigger Direct Download to Laptop
if display and Audio:
    display(Audio(out_mp3))

try:
    import importlib
    colab_files = importlib.import_module("google.colab.files")
    colab_files.download(out_mp3)
    print("⬇️ Mastered MP3 downloaded directly to your laptop!")
except Exception:
    if display and HTML:
        display(HTML(f'<a href="/files{out_mp3}" download style="display:inline-block;padding:10px 18px;background:#10b981;color:#fff;border-radius:8px;font-weight:bold;text-decoration:none;">⬇️ Download Mastered Voiceover (.mp3)</a>'))
