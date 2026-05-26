#!/usr/bin/env python3
"""Simple frontend startup script"""
import subprocess
import sys
import os

os.chdir(os.path.join(os.path.dirname(__file__), "frontend_vue"))

print("=" * 60)
print("Starting Langchain-Chatchat Frontend")
print("=" * 60)
print()

# Install dependencies if needed
print("[INFO] Installing npm dependencies...")
subprocess.run([sys.executable, "-m", "pip", "install", "npm"], capture_output=True)

# Start frontend dev server
print("[INFO] Starting frontend dev server on port 5173...")
try:
    subprocess.run(["npm", "run", "dev"])
except KeyboardInterrupt:
    print("\n[INFO] Frontend stopped")
    sys.exit(0)
except Exception as e:
    print(f"[ERROR] Failed to start frontend: {e}")
    sys.exit(1)
