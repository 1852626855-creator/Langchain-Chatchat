import os
import subprocess
import sys
import time

import requests

ROOT = os.path.dirname(os.path.abspath(__file__))


def check_url(url, timeout=5):
    try:
        r = requests.get(url, timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False


def kill_port(port):
    """Kill process listening on port (Windows)."""
    try:
        out = subprocess.check_output(
            f'netstat -ano | findstr ":{port}"',
            shell=True,
            text=True,
            stderr=subprocess.DEVNULL,
        )
        pids = set()
        for line in out.splitlines():
            if "LISTENING" in line:
                parts = line.split()
                if parts:
                    pids.add(parts[-1])
        for pid in pids:
            if pid.isdigit() and pid != "0":
                subprocess.run(
                    f"taskkill /PID {pid} /F",
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
    except Exception:
        pass


def main():
    print("=" * 50)
    print("Langchain-Chatchat backend launcher")
    print("=" * 50)

    for port in (7861, 8000, 20001, 20002, 21001):
        kill_port(port)
    time.sleep(2)

    print("[1/2] Starting full API stack (startup.py --all-api)...")
    api_process = subprocess.Popen(
        [sys.executable, "startup.py", "--all-api"],
        cwd=ROOT,
    )

    print("Waiting for API on :7861 ...")
    ok = False
    for _ in range(60):
        if check_url("http://127.0.0.1:7861/docs"):
            ok = True
            break
        time.sleep(2)
    if ok:
        print("[OK] API ready: http://localhost:7861/docs")
    else:
        print("[WARN] API not responding yet; check logs in logs/")

    print("[2/2] Starting LangServe on :8000 ...")
    langserve_process = subprocess.Popen(
        [sys.executable, "langserve_chain.py"],
        cwd=ROOT,
    )
    time.sleep(5)
    if check_url("http://127.0.0.1:8000/health"):
        print("[OK] LangServe ready: http://localhost:8000/chat/playground")
    else:
        print("[WARN] LangServe not responding yet")

    print("=" * 50)
    print("Backend:   http://localhost:7861/docs")
    print("LangServe: http://localhost:8000/chat/playground")
    print("Frontend:  cd frontend_vue && npm run dev")
    print("Press Ctrl+C to stop")
    print("=" * 50)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
        api_process.terminate()
        langserve_process.terminate()
        print("Stopped.")


if __name__ == "__main__":
    main()
