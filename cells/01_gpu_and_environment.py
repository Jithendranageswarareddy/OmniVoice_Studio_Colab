# ==============================================================================
# 🚀 CELL 1: GPU Accelerator & Google Drive Model Cache
# Checks GPU and links Google Drive for permanent model & voice caching!
# ==============================================================================
import os, sys, subprocess, importlib

print("🔍 Checking hardware accelerator...")
try:
    import torch
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"✅ GPU Active: {gpu_name} ({vram:.1f} GB VRAM)")
        print("⚡ Voice cloning will run in ultra-fast GPU mode (~30-45s per take)!")
    else:
        print("⚠️ WARNING: No GPU detected! Currently running on CPU.")
        print("👉 Go to: Runtime -> Change runtime type -> Hardware accelerator: T4 GPU -> Save")
except Exception as e:
    print(f"Note: {e}")

# ── Google Drive Persistent Model Caching (Instant Startup on Future Sessions) ──
USE_DRIVE_CACHE = True
cache_linked = False

if USE_DRIVE_CACHE:
    try:
        colab_module = importlib.import_module("google.colab")
        drive = getattr(colab_module, "drive", None)
        if drive is not None:
            drive.mount('/content/drive')
            CACHE_DIR = "/content/drive/MyDrive/VoiceStudio_Cache"
            os.makedirs(CACHE_DIR, exist_ok=True)
            
            # Point all AI model weights, tokenizers and database permanently to Google Drive
            os.environ["HF_HOME"] = os.path.join(CACHE_DIR, "huggingface")
            os.environ["MODELSCOPE_CACHE"] = os.path.join(CACHE_DIR, "modelscope")
            os.environ["TORCH_HOME"] = os.path.join(CACHE_DIR, "torch")
            os.environ["OMNIVOICE_DATA_DIR"] = os.path.join(CACHE_DIR, "omnivoice_data")
            cache_linked = True
            print(f"💾 Google Drive Model Caching ACTIVE: {CACHE_DIR}")
            print("🚀 AI models & voice profiles are saved permanently in your Google Drive!")
            print("⚡ Future sessions will boot in ~10 seconds without re-downloading!")
    except Exception as e:
        print(f"ℹ️ Drive caching fallback ({e})")

if not cache_linked:
    DATA_DIR = "/content/omnivoice_data"
    os.makedirs(DATA_DIR, exist_ok=True)
    os.environ["OMNIVOICE_DATA_DIR"] = DATA_DIR
    print(f"📁 Local VM workspace initialized at {DATA_DIR}")

os.environ["OMNIVOICE_SERVER_MODE"] = "1"
os.environ["PYTHONUNBUFFERED"] = "1"
