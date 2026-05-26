#!/usr/bin/env python3
"""Simple backend startup script"""
import subprocess
import sys
import os

os.chdir(os.path.dirname(__file__))

print("=" * 60)
print("Starting Langchain-Chatchat Backend API")
print("=" * 60)
print()

# Start API server on port 7861
print("[INFO] Starting API server on port 7861...")
try:
    subprocess.run([sys.executable, "server/api.py", "--port", "7861"])
except KeyboardInterrupt:
    print("\n[INFO] Server stopped")
    sys.exit(0)
except Exception as e:
    print(f"[ERROR] Failed to start server: {e}")
    sys.exit(1)
