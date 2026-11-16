#!/usr/bin/env python3
"""
Dedicated Google Colab Voice Cloning Studio Server
Replicates the exact local laptop voice cloning studio on Google Colab GPU.
"""

import asyncio
import io
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import uuid
import wave
import base64
from typing import Optional

import requests
import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IS_KAGGLE = os.path.exists("/kaggle/working")
ROOT_WORKSPACE = "/kaggle/working" if IS_KAGGLE else "/content"
OUTPUT_DIR = os.path.join(ROOT_WORKSPACE, "cloned_takes")
INPUT_DIR = os.path.join(ROOT_WORKSPACE, "input")
VOICESTUDIO_URL = "http://127.0.0.1:3900"
FFMPEG_BIN = "ffmpeg"

# Enforce offline HuggingFace environment to avoid Cloudflare/429 JSONDecodeError
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(INPUT_DIR, exist_ok=True)

app = FastAPI(title="Voice Cloning Studio (Colab Edition)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store
jobs = {}

# Embedded clean 8.35s Telugu voice sample (portable across any Colab session)
REF_WAV_PATH = os.path.join(INPUT_DIR, "p_j_n_reddy_ref.wav")
REF_TRANSCRIPT = "మీరు ఎప్పుడైనా సూపర్ మార్కెట్ లోకి వెళ్లారా? అక్కడ క్యాషియర్ దగ్గర మూడు ఆపిల్స్ ఉంటే, వాటిని చూడగానే మూడు అని చెప్పగలరు."

def ensure_reference_voice_file():
    """Ensure clean 8.35s reference wav exists on disk."""
    if not os.path.exists(REF_WAV_PATH):
        # Look in assets or parent
        alt_path = os.path.join(os.path.dirname(BASE_DIR), "assets", "p_j_n_reddy_ref.wav")
        if os.path.exists(alt_path):
            shutil.copyfile(alt_path, REF_WAV_PATH)
        else:
            # Check embedded_voice.py
            emb_path = os.path.join(os.path.dirname(BASE_DIR), "assets", "embedded_voice.py")
            if os.path.exists(emb_path):
                import importlib.util
                spec = importlib.util.spec_from_file_location("embedded_voice", emb_path)
                if spec is not None and spec.loader is not None:
                    emb = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(emb)
                    with open(REF_WAV_PATH, "wb") as f:
                        f.write(base64.b64decode(getattr(emb, "REF_AUDIO_B64", "")))

def ensure_voice_profile_registered():
    """Registers P_J_N_Reddy_RealVoice profile in VoiceStudio if missing."""
    ensure_reference_voice_file()
    auto_accept_model_licenses()
    try:
        r = requests.get(f"{VOICESTUDIO_URL}/profiles", timeout=5)
        if r.status_code == 200:
            profiles = r.json()
            for p in profiles:
                if "Reddy" in p.get("name", ""):
                    return p["id"]

        # Register clean 8.35s reference
        if os.path.exists(REF_WAV_PATH):
            with open(REF_WAV_PATH, "rb") as f:
                files = {"ref_audio": (os.path.basename(REF_WAV_PATH), f, "audio/wav")}
                data = {
                    "name": "P_J_N_Reddy_RealVoice",
                    "language": "Telugu",
                    "ref_text": REF_TRANSCRIPT,
                    "kind": "clone",
                }
                res = requests.post(f"{VOICESTUDIO_URL}/profiles", data=data, files=files, timeout=30)
                if res.status_code == 200:
                    created = res.json()
                    print(f"✅ Registered clean voice profile: {created['name']} ({created['id']})")
                    return created["id"]
    except Exception as e:
        print(f"Notice: Profile register check: {e}")
    return None

def split_text_into_chunks(text: str, max_chars: int = 150) -> list[dict]:
    """Splits text into natural sentences with adaptive pause metadata and emotional tags."""
    paragraphs = text.split("\n\n")
    all_chunks = []

    for p_idx, para in enumerate(paragraphs):
        para = para.strip()
        if not para:
            continue

        # 1. Protect ellipses (...) so they don't fracture sentences into tiny 1-word bursty fragments
        protected = re.sub(r'\.{2,}', ' __ELLIPSIS__ ', para)
        protected = re.sub(r'…', ' __ELLIPSIS__ ', protected)

        # 2. Split on sentence boundaries
        raw_sentences = re.split(r'([.?!।\n]+)', protected)
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

        # 3. Restore ellipses and clean whitespace
        restored = []
        for c in chunks:
            r = c.replace('__ELLIPSIS__', '...').strip()
            r = re.sub(r'\s+', ' ', r)
            if r:
                restored.append(r)

        # 4. Clause breakdown for sentences exceeding max_chars
        refined = []
        for s in restored:
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

        # 5. Merge micro-chunks (<18 chars or <= 2 words) to prevent rapid staccato bursts
        merged = []
        for c in refined:
            clean_c = c.strip()
            if not clean_c:
                continue
            if merged and (len(merged[-1]) + len(clean_c) + 1 <= max_chars) and (len(clean_c.split()) <= 2 or len(clean_c) < 18):
                merged[-1] = merged[-1] + " " + clean_c
            else:
                merged.append(clean_c)

        # 6. Assign adaptive context-aware pause duration for long-form educational videos
        for s_idx, c in enumerate(merged):
            is_last = (s_idx == len(merged) - 1)
            if is_last:
                pause = 0.45  # Paragraph / Major concept transition pause
            elif "?" in c:
                pause = 0.32  # Inquisitive question reflection gap
            elif "!" in c:
                pause = 0.25  # Punchline / affirmation gap
            elif c.endswith("..."):
                pause = 0.40  # Suspenseful reveal pause
            else:
                pause = 0.20  # Standard sentence boundary

            all_chunks.append({
                "text": c,
                "pause": pause,
                "is_question": ("?" in c),
                "is_exclamation": ("!" in c),
            })

    return all_chunks

def auto_accept_model_licenses():
    """Auto-accept all model licenses in VoiceStudio backend so 403 never occurs."""
    try:
        backend_path = os.path.join(ROOT_WORKSPACE, "VoiceStudio", "backend")
        if backend_path not in sys.path and os.path.exists(backend_path):
            sys.path.insert(0, backend_path)
        from services import model_acceptance
        reg = model_acceptance._registry()
        for m in reg.get("models", []):
            repo_id = m.get("id") or m.get("repo_id")
            try:
                st = model_acceptance.status(repo_id)
                if st.get("required") and not st.get("accepted"):
                    model_acceptance.accept(repo_id, st.get("fingerprint"))
            except Exception:
                pass
    except Exception as e:
        print(f"Notice on auto-accepting licenses: {e}")

def synthesize_chunk_request(
    text: str, profile_id: str, language: str, steps: int, speed: float, guidance: float, effect_preset: str = "raw"
) -> bytes:
    data = {
        "text": text,
        "language": language,
        "profile_id": profile_id,
        "num_step": steps,
        "guidance_scale": guidance,
        "speed": speed,
        "effect_preset": effect_preset,
        "wav_bits": "16",
        "stream": "false",
    }
    resp = requests.post(f"{VOICESTUDIO_URL}/generate", data=data, timeout=300)
    if resp.status_code == 403:
        # HTTP 403 model_licence_required: auto-accept and retry immediately
        auto_accept_model_licenses()
        resp = requests.post(f"{VOICESTUDIO_URL}/generate", data=data, timeout=300)

    if resp.status_code != 200:
        log_snippet = ""
        log_path = os.path.join(ROOT_WORKSPACE, "backend.log")
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8", errors="ignore") as lf:
                    log_snippet = "".join(lf.readlines()[-30:])
            except Exception:
                pass
        err_msg = f"HTTP {resp.status_code}: {resp.text}"
        if log_snippet:
            print(f"\n[VoiceStudio Backend Log Output]:\n{log_snippet}\n")
            err_msg += f"\nBackend Details:\n{log_snippet}"
        raise RuntimeError(err_msg)
    return resp.content

def concatenate_and_master(wav_bytes_list: list, base_name: str) -> dict:
    if not wav_bytes_list:
        raise ValueError("No audio chunks to concatenate.")

    wav_path = os.path.join(OUTPUT_DIR, f"{base_name}.wav")
    mp3_path = os.path.join(OUTPUT_DIR, f"{base_name}.mp3")

    first_params = None
    all_frames = []

    for item in wav_bytes_list:
        if isinstance(item, tuple):
            w_bytes, pause_dur = item
        else:
            w_bytes, pause_dur = item, 0.20

        if not w_bytes or len(w_bytes) < 44:
            continue
        try:
            with wave.open(io.BytesIO(w_bytes), "rb") as wf:
                params = wf.getparams()
                if first_params is None:
                    first_params = params
                frames = wf.readframes(params.nframes)
                all_frames.append(frames)
                # Adaptive human breathing and concept transition pause
                silence_samples = int(params.framerate * max(0.12, pause_dur))
                all_frames.append(b'\x00\x00' * silence_samples * params.nchannels)
        except Exception as e:
            print(f"[Warning] Failed to decode audio chunk: {e}")

    if first_params is None:
        raise ValueError("Could not extract valid audio parameters from synthesized chunks.")

    raw_audio_bytes = b"".join(all_frames)

    # Subtle studio presence polish: +1.8dB high-shelf above 4.5kHz to restore natural vocal brilliance
    try:
        import numpy as np
        import scipy.signal as signal
        audio_arr = np.frombuffer(raw_audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
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
        polished = signal.lfilter(b, a, audio_arr)
        polished = np.clip(polished, -0.98, 0.98)
        processed_bytes = (polished * 32767.0).astype(np.int16).tobytes()
    except Exception as e:
        print(f"[Warning] Studio presence polish fallback: {e}")
        processed_bytes = raw_audio_bytes

    with wave.open(wav_path, "wb") as out_wf:
        out_wf.setnchannels(first_params.nchannels)
        out_wf.setsampwidth(first_params.sampwidth)
        out_wf.setframerate(first_params.framerate)
        out_wf.writeframes(processed_bytes)

    # Master to broadcast standard -16 LUFS MP3
    cmd = [
        FFMPEG_BIN, "-y",
        "-i", wav_path,
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        mp3_path
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            shutil.copyfile(wav_path, mp3_path)
    except Exception:
        shutil.copyfile(wav_path, mp3_path)

    # Duration
    duration = 0.0
    try:
        with wave.open(wav_path, "rb") as wf:
            duration = round(wf.getnframes() / float(wf.getframerate()), 2)
    except Exception:
        pass

    return {
        "wav_filename": f"{base_name}.wav",
        "mp3_filename": f"{base_name}.mp3",
        "duration": duration,
        "wav_size": os.path.getsize(wav_path) if os.path.exists(wav_path) else 0,
        "mp3_size": os.path.getsize(mp3_path) if os.path.exists(mp3_path) else 0,
    }

def run_synthesis_job(
    job_id: str, profile_id: str, text: str, language: str, steps: int, speed: float, guidance: float, effect_preset: str = "raw"
):
    jobs[job_id]["status"] = "processing"
    jobs[job_id]["message"] = "Splitting text into natural sentences..."
    try:
        chunks = split_text_into_chunks(text)
        jobs[job_id]["total_chunks"] = len(chunks)
        wav_parts = []

        for idx, chunk_info in enumerate(chunks):
            chunk = chunk_info["text"] if isinstance(chunk_info, dict) else chunk_info
            pause = chunk_info.get("pause", 0.22) if isinstance(chunk_info, dict) else 0.22

            # Context-adaptive guidance & speed modulation
            chunk_guidance = guidance
            chunk_speed = speed
            if isinstance(chunk_info, dict):
                if chunk_info.get("is_question"):
                    chunk_guidance = min(1.6, guidance + 0.15)
                    chunk_speed = speed * 0.96
                elif chunk_info.get("is_exclamation"):
                    chunk_guidance = min(1.65, guidance + 0.18)
                    chunk_speed = speed * 1.02

            jobs[job_id]["current_chunk"] = idx + 1
            jobs[job_id]["message"] = f"Synthesizing sentence {idx + 1} of {len(chunks)} on GPU..."
            wav_bytes = synthesize_chunk_request(
                text=chunk,
                profile_id=profile_id,
                language=language,
                steps=steps,
                speed=chunk_speed,
                guidance=chunk_guidance,
                effect_preset=effect_preset,
            )
            wav_parts.append((wav_bytes, pause))

        jobs[job_id]["message"] = "Mastering broadcast audio (-16 LUFS)..."
        base_name = f"cloned_{int(time.time())}_{job_id[:6]}"
        result = concatenate_and_master(wav_parts, base_name)

        jobs[job_id]["status"] = "done"
        jobs[job_id]["message"] = "Voiceover synthesis completed successfully!"
        jobs[job_id]["result"] = result
    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["message"] = str(e)

# ── API Routes ─────────────────────────────────────────────────────────────

@app.get("/api/health")
def api_health():
    ensure_voice_profile_registered()
    return {"status": "ok", "backend_online": True}

@app.get("/api/profiles")
def get_profiles():
    ensure_voice_profile_registered()
    try:
        resp = requests.get(f"{VOICESTUDIO_URL}/profiles", timeout=5)
        if resp.status_code == 200:
            profiles = resp.json()
            # Filter out any old uncalibrated long profiles
            clean_profiles = [p for p in profiles if "Reddy" in p.get("name", "") or "P_J_N" in p.get("name", "")]
            return {"profiles": clean_profiles if clean_profiles else profiles}
    except Exception as e:
        return {"profiles": [], "error": str(e)}
    return {"profiles": []}

@app.post("/api/profiles/upload")
async def upload_new_profile(
    name: str = Form(...),
    language: str = Form("Telugu"),
    ref_text: str = Form(""),
    audio: UploadFile = File(...),
):
    temp_path = os.path.join(INPUT_DIR, f"temp_{int(time.time())}_{audio.filename}")
    with open(temp_path, "wb") as f:
        f.write(await audio.read())

    # CRITICAL: Automatically trim to optimal 10.0s so [clone_ref_too_long] CAN NEVER HAPPEN!
    trimmed_path = os.path.join(INPUT_DIR, f"trimmed_{int(time.time())}.wav")
    try:
        cmd = [
            FFMPEG_BIN, "-y",
            "-i", temp_path,
            "-t", "10.0",
            "-ar", "24000",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            trimmed_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        upload_target = trimmed_path if (os.path.exists(trimmed_path) and os.path.getsize(trimmed_path) > 1000) else temp_path
    except Exception:
        upload_target = temp_path

    try:
        with open(upload_target, "rb") as f:
            files = {"ref_audio": (os.path.basename(upload_target), f, "audio/wav")}
            data = {
                "name": name,
                "language": language,
                "ref_text": ref_text,
                "kind": "clone",
            }
            resp = requests.post(f"{VOICESTUDIO_URL}/profiles", data=data, files=files, timeout=30)
            if resp.status_code == 200:
                return {"status": "ok", "profile": resp.json()}
            else:
                raise HTTPException(status_code=resp.status_code, detail=resp.text)
    finally:
        for p in [temp_path, trimmed_path]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass

@app.post("/api/clone")
async def start_clone(
    profile_id: str = Form(...),
    text: str = Form(...),
    language: str = Form("Telugu"),
    steps: int = Form(8),
    speed: float = Form(1.0),
    guidance: float = Form(1.3),
    effect_preset: str = Form("raw"),
):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Script text cannot be empty.")

    job_id = uuid.uuid4().hex[:12]
    jobs[job_id] = {
        "id": job_id,
        "status": "queued",
        "message": "Initializing voice synthesis on T4 GPU...",
        "current_chunk": 0,
        "total_chunks": 1,
        "result": None,
        "created_at": time.time(),
    }

    asyncio.get_event_loop().run_in_executor(
        None,
        run_synthesis_job,
        job_id,
        profile_id,
        text.strip(),
        language,
        steps,
        speed,
        guidance,
        effect_preset,
    )

    return {"job_id": job_id}

@app.get("/api/job/{job_id}")
def get_job_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found.")
    return jobs[job_id]

@app.get("/api/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    media_type = "audio/mpeg" if filename.endswith(".mp3") else "audio/wav"
    return FileResponse(
        file_path,
        media_type=media_type,
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

@app.get("/api/stream/{filename}")
def stream_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    media_type = "audio/mpeg" if filename.endswith(".mp3") else "audio/wav"
    return FileResponse(file_path, media_type=media_type)

@app.get("/api/logs")
def view_backend_logs():
    log_path = os.path.join(ROOT_WORKSPACE, "backend.log")
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8", errors="ignore") as lf:
                return {"logs": "".join(lf.readlines()[-100:])}
        except Exception as e:
            return {"logs": f"Error reading log: {e}"}
    return {"logs": "Log file not found."}

# Mount static files and index
static_dir = os.path.join(BASE_DIR, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
def index_page():
    index_html_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_html_path):
        with open(index_html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Voice Cloning Studio Loading...</h1>"

if __name__ == "__main__":
    ensure_voice_profile_registered()
    print("\n========================================================")
    print("  🚀 Voice Cloning Studio (Colab Edition) Running on Port 5050")
    print("========================================================\n")
    uvicorn.run(app, host="0.0.0.0", port=5050, log_level="warning")
