# 🎙️ Permanent Voice Studio Setup (Google Colab Replica)

This folder contains the complete, battle-tested replica of the **VoiceStudio GPU Voice Cloning setup**.

It is designed to run on **Google Colab (Free T4 GPU)** from **ANY Google/Gmail account**, providing:
* ⚡ **Ultra-Fast Generation:** ~30–45 seconds per voiceover (25x faster than laptop CPU).
* 🔄 **100% Account Portability:** Works across any Gmail account without re-calibrating or re-uploading your voice sample.
* 🎧 **Studio Natural Sound:** Removes the metallic/boxy robotic room coloration with calibrated defaults (`raw` timbre, 8 diffusion steps, guidance 1.3, broadcast `-16 LUFS` mastering).

---

## 📁 Folder Structure

```
colab-voice-studio/
├── Permanent_Voice_Studio_Setup.ipynb  # Complete Jupyter Notebook (Ready to upload to Colab)
├── README.md                           # This step-by-step master guide
├── cells/                              # Individual code cells (for easy 1-click copy-pasting)
│   ├── 01_gpu_and_environment.py       # Cell 1: Check T4 GPU & set paths
│   ├── 02_install_voicestudio.py       # Cell 2: Fast install, pre-accept licenses & de-robotic patch
│   ├── 03_setup_voice_profile.py       # Cell 3: Auto-register P_J_N_Reddy_RealVoice profile
│   ├── 04_launch_studio_ui.py          # Cell 4: Start backend & launch Web UI (Colab + Cloudflare)
│   └── 05_direct_voice_cloner.py       # Cell 5: (Optional) Direct in-notebook voice generator
└── assets/
    ├── p_j_n_reddy_ref.wav             # Calibrated 8.35s reference audio
    ├── reference_transcript.txt        # Exact Telugu reference transcript
    └── embedded_voice.py               # Self-restoring base64 voice sample (portable across accounts)
```

---

## 🚀 Step-by-Step Instructions: From Scratch to Full Web UI

### Option 0: Control Directly Inside VS Code via Colab Extension (Recommended & Most Powerful)
Since you have the **Google Colab extension** installed in VS Code:
1. In your VS Code file explorer (left sidebar), click to open:
   `colab-voice-studio/Permanent_Voice_Studio_Setup.ipynb`
2. At the top-right corner of the notebook editor, click **Select Kernel**.
3. Choose **Colab** ➔ **Auto Connect** (sign in with your Google account when prompted).
4. If prompted for runtime type, select **T4 GPU**.
5. Click **Run All** (or press the Play button on each cell):
   - The code executes on Google Colab's cloud T4 GPU.
   - All logs, progress, and audio players display **right inside your laptop VS Code**!
   - In Cell 5, the mastered MP3 automatically downloads directly to your laptop!

---

### Option 1: One-Click Upload to Browser Colab
1. In your browser, open [Google Colab](https://colab.research.google.com/).
2. Click **File ➔ Upload notebook**.
3. Select `Permanent_Voice_Studio_Setup.ipynb` from this folder:
   `C:\Users\jithendra\my-video-editor-setup\colab-voice-studio\Permanent_Voice_Studio_Setup.ipynb`
4. The entire configured studio loads instantly!

---

### Option 2: Copy-Paste into Your Open Blank Notebook
If you already have your empty notebook open (like `Permanent voice studio clone setup.ipynb`):
1. **Cell 1:** Copy code from `cells/01_gpu_and_environment.py` ➔ Paste into Colab ➔ Click Run.
2. **Cell 2:** Click **+ Code**, copy from `cells/02_install_voicestudio.py` ➔ Paste ➔ Click Run (~3-4 mins on fresh VM).
3. **Cell 3:** Click **+ Code**, copy from `cells/03_setup_voice_profile.py` ➔ Paste ➔ Click Run.
4. **Cell 4:** Click **+ Code**, copy from `cells/04_launch_studio_ui.py` ➔ Paste ➔ Click Run.
5. **Cell 5 (Optional):** Click **+ Code**, copy from `cells/05_direct_voice_cloner.py` for direct in-cell generation.

---

## ⚙️ Everyday 4-Step Production Routine

Every time you want to clone your voice for a new video:

1. **Verify GPU Accelerator:**
   * Go to **Runtime ➔ Change runtime type**.
   * Hardware accelerator: **T4 GPU** ➔ Click **Save**.
2. **Run the Notebook:**
   * Click **Runtime ➔ Run all** (or run Cells 1 to 4).
3. **Open the Web UI:**
   * In Cell 4, click the **Colab Window link** or the **Public Cloudflare link** (`https://*.trycloudflare.com`).
   * The VoiceStudio web app opens in a new tab.
4. **Generate Your Voiceover:**
   * Select voice profile: **`P_J_N_Reddy_RealVoice (Telugu)`**.
   * Paste your Telugu or English script.
   * Ensure **Steps = 8** and **Preset = Raw** (set by default).
   * Click **Generate** ➔ In **30–45s**, your audio is ready to download!

---

## 🔄 Backup Plan: Switching to Another Gmail Account

If your primary Google account ever reaches its daily free T4 GPU limit:
1. Open an incognito browser window or switch Google profiles to your backup Gmail account.
2. Go to [colab.research.google.com](https://colab.research.google.com/).
3. Upload `Permanent_Voice_Studio_Setup.ipynb`.
4. Click **Runtime ➔ Run all**.
5. Because your voice sample is embedded in the setup code, your **`P_J_N_Reddy_RealVoice`** profile will be registered automatically on the new account with zero setup hassle!
