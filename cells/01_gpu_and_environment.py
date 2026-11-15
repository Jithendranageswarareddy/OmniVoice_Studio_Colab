# ==============================================================================
# 🚀 CELL 1: GPU & Environment Check
# Run this cell first. It verifies that a GPU (e.g. Tesla T4) is active.
# ==============================================================================
import os, sys, subprocess

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

# Base workspace directory
DATA_DIR = "/content/omnivoice_data"
os.makedirs(DATA_DIR, exist_ok=True)
os.environ["OMNIVOICE_DATA_DIR"] = DATA_DIR
os.environ["OMNIVOICE_SERVER_MODE"] = "1"
os.environ["PYTHONUNBUFFERED"] = "1"

print(f"📁 Workspace initialized at {DATA_DIR}")
