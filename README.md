# 🎙️ Permanent Voice Studio Setup (Colab GPU Edition)

This repository contains the complete, dedicated **Telugu & English Voice Cloning Studio** running on Google Colab (Free T4 GPU).

It replicates your exact local laptop studio on the cloud:
* ⚡ **Fast Setup:** Boots in ~60-90 seconds (No Bun/Vite building, no Google Drive authorization popups).
* 🎙️ **Pre-Calibrated:** Voice profile `P_J_N_Reddy_RealVoice` is pre-registered with your clean 8.35s Telugu audio sample.
* 🛡️ **Zero `[clone_ref_too_long]` Errors:** Any newly uploaded audio is automatically trimmed to 10.0 seconds using ffmpeg before processing.
* 🎧 **Studio Presence & Broadcast Audio:** Automatically mastered to `-16 LUFS` broadcast standard with natural 180ms breath pauses.
* 📱 **Mobile & Laptop Friendly:** Access via Cloudflare tunnel on your phone or laptop.

---

## 🚀 1-Click Launch Options

### Option 1: Direct 1-Click GitHub Colab Link (Easiest)
Click the link below to open this exact notebook with all cells pre-loaded:

👉 **[Open Permanent Voice Studio on Google Colab](https://colab.research.google.com/github/Jithendranageswarareddy/OmniVoice_Studio_Colab/blob/main/Permanent_Voice_Studio_Setup.ipynb)**

1. Ensure T4 GPU is active: **Runtime ➔ Change runtime type ➔ T4 GPU ➔ Save**.
2. Click the Play button on **Cell 1**.
3. In ~60-90 seconds, click the **Public Studio Link** (`https://xxxx.trycloudflare.com`) displayed at the bottom of Cell 1!

---

### Option 2: Copy-Paste into Any Open Blank Colab Notebook
If you already have a blank notebook open in Google Drive:
1. Copy the code from [`cells/01_launch_studio.py`](cells/01_launch_studio.py).
2. Paste into the empty code cell.
3. Click the Play button!

---

## 📁 Repository Structure

```
colab-voice-studio/
├── Permanent_Voice_Studio_Setup.ipynb  # Streamlined 2-cell Google Colab notebook
├── README.md                           # Master instructions
├── studio/
│   ├── colab_server.py                 # Standalone FastAPI studio server (port 5050)
│   └── static/
│       └── index.html                  # Dark-mode Studio Web UI
├── cells/
│   ├── 01_launch_studio.py             # 1-Click launcher code (Cell 1)
│   └── 05_direct_voice_cloner.py       # In-notebook direct generator (Cell 2)
├── assets/
│   ├── p_j_n_reddy_ref.wav             # Calibrated 8.35s reference audio
│   ├── reference_transcript.txt        # Telugu reference transcript
│   └── embedded_voice.py               # Portable base64 reference audio
└── scripts/
    └── build_notebook.py               # Notebook builder script
```

---

## ⚙️ Voice Settings & Calibration

| Setting | Default | Purpose |
| :--- | :--- | :--- |
| **Diffusion Steps** | `8` | Optimal studio realism without phase distortion |
| **Guidance Scale** | `1.3` | Crisp Telugu plosives without metallic buzz |
| **Speed** | `1.0` | Natural conversational cadence |
| **Acoustic Timbre** | `raw` | Pure vocal tone (bypasses boxy room effects) |
| **Mastering** | `-16 LUFS` | Broadcast YouTube audio standard |
