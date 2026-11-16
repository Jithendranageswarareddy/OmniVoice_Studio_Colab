# ==============================================================================
# ⚡ CELL 5: Direct Voice Cloner (In-Notebook Fast Generator)
# Uses identical Sentence-Chunking & 180ms Breath Mastering as Customized Studio UI.
# ==============================================================================
import requests, os, wave, io, time, subprocess, importlib, re
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
దీనికి సంబంధించిన ఒక ఆసక్తికరమైన స్కిల్ గురించి ఇప్పుడు తెలుసుకుందాం... దాని పేరు సబిటైజింగ్!"""

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

# ── 3. Chunked GPU Synthesis (Prevents Dropped Words & Hallucinations) ─────────
def split_into_chunks(text: str, max_chars: int = 150):
    raw_sentences = re.split(r'([.?!।\n]+)', text)
    chunks = []
    current = ""
    for s in raw_sentences:
        if not s:
            continue
        if re.match(r'^[.?!।\n]+$', s):
            current += s
            if len(current.strip()) > 0:
                chunks.append(current.strip())
                current = ""
        else:
            if current:
                chunks.append(current.strip())
            current = s
    if current.strip():
        chunks.append(current.strip())
    refined = []
    for s in chunks:
        if len(s) <= max_chars:
            refined.append(s)
        else:
            clauses = re.split(r'([,;:\-–])', s)
            sub = ""
            for cl in clauses:
                if len(sub) + len(cl) <= max_chars:
                    sub += cl
                else:
                    if sub.strip():
                        refined.append(sub.strip())
                    sub = cl
            if sub.strip():
                refined.append(sub.strip())
    return [c for c in refined if len(c.strip()) > 0]

chunks = split_into_chunks(SCRIPT_TEXT.strip())
print(f"✂️ Split script into {len(chunks)} natural sentences for crisp articulation.")

wav_parts = []
t0 = time.time()
for idx, chunk in enumerate(chunks):
    print(f"🚀 [{idx+1}/{len(chunks)}] Synthesizing on GPU: \"{chunk[:35]}...\"")
    payload = {
        "text": chunk,
        "language": "Telugu",
        "profile_id": profile_id,
        "num_step": 8,           # Studio Realism (8 steps, no phase noise)
        "guidance_scale": 1.3,   # Crisp Telugu plosives without metallic buzz
        "speed": 1.0,            # Natural conversational speed
        "effect_preset": "raw",  # Pure acoustic vocal timbre
        "wav_bits": "16",
        "stream": "false"
    }
    res = requests.post(f"{BASE_URL}/generate", data=payload, timeout=300)
    if res.status_code != 200:
        raise RuntimeError(f"Generation error {res.status_code}: {res.text}")
    wav_parts.append(res.content)

gen_duration = time.time() - t0
print(f"✅ All {len(chunks)} sentences synthesized in {gen_duration:.1f}s!")

# ── 4. Natural 180ms Breath Concatenation & Mastering ──────────────────────────
first_params = None
all_frames = []
for w_bytes in wav_parts:
    if not w_bytes or len(w_bytes) < 44:
        continue
    with wave.open(io.BytesIO(w_bytes), "rb") as wf:
        params = wf.getparams()
        if first_params is None:
            first_params = params
        all_frames.append(wf.readframes(params.nframes))
        # 180ms natural human breathing pause between thoughts
        silence_samples = int(params.framerate * 0.18)
        all_frames.append(b'\x00\x00' * silence_samples * params.nchannels)

raw_audio_bytes = b"".join(all_frames)

# Studio presence EQ (+1.8dB high-shelf above 4.5kHz)
audio = np.frombuffer(raw_audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
sr = first_params.framerate
gain_db = 1.8
A = 10.0 ** (gain_db / 40.0)
w0 = 2.0 * np.pi * 4500.0 / sr
alpha = np.sin(w0) / 2.0 * np.sqrt(2.0)
cos_w0 = np.cos(w0)

b0 =    A * ((A + 1.0) + (A - 1.0) * cos_w0 + 2.0 * np.sqrt(A) * alpha)
b1 = -2.0*A * ((A - 1.0) + (A + 1.0) * cos_w0)
b2 =    A * ((A + 1.0) + (A - 1.0) * cos_w0 - 2.0 * np.sqrt(A) * alpha)
a0 =         (A + 1.0) - (A - 1.0) * cos_w0 + 2.0 * np.sqrt(A) * alpha
a1 =    2.0 * ((A - 1.0) - (A + 1.0) * cos_w0)
a2 =         (A + 1.0) - (A - 1.0) * cos_w0 - 2.0 * np.sqrt(A) * alpha

b = np.array([b0, b1, b2]) / a0
a = np.array([a0, a1, a2]) / a0
polished = signal.lfilter(b, a, audio)
polished = np.clip(polished, -0.98, 0.98)
polished_bytes = (polished * 32767.0).astype(np.int16).tobytes()

out_dir = "/content/cloned_takes"
os.makedirs(out_dir, exist_ok=True)
wav_out = os.path.join(out_dir, "studio_master.wav")
mp3_out = os.path.join(out_dir, "studio_master.mp3")

with wave.open(wav_out, "wb") as out_wf:
    out_wf.setnchannels(first_params.nchannels)
    out_wf.setsampwidth(first_params.sampwidth)
    out_wf.setframerate(first_params.framerate)
    out_wf.writeframes(polished_bytes)

# Master to broadcast standard -16 LUFS MP3
cmd = ["ffmpeg", "-y", "-i", wav_out, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "libmp3lame", "-b:a", "192k", mp3_out]
subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

duration_sec = len(polished) / float(sr)
print(f"🎵 Studio Master Ready: {mp3_out} ({duration_sec:.1f}s)")

# ── 5. In-Notebook Audio Player & Download ────────────────────────────────────
if display and Audio and os.path.exists(mp3_out):
    display(Audio(mp3_out, autoplay=True))
    try:
        colab_files = importlib.import_module("google.colab.files")
        colab_files.download(mp3_out)
        print("💾 Download started automatically!")
    except Exception:
        print(f"👉 File saved at: {mp3_out}")
