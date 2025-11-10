import subprocess
import signal
import sys
import time
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BACKEND_CMD = [sys.executable, "app.py"]

# On Windows, use shell=True or npm.cmd
if os.name == 'nt':  # Windows
    FRONTEND_CMD = "npm run dev"
    USE_SHELL = True
else:  # Unix/Linux/Mac
    FRONTEND_CMD = ["npm", "run", "dev"]
    USE_SHELL = False

processes = []


def shutdown(signum=None, frame=None):
    for proc in processes:
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    backend = subprocess.Popen(
        BACKEND_CMD,
        cwd=ROOT,
    )
    processes.append(backend)
    print("✅ Flask API started at http://127.0.0.1:5000")

    frontend = subprocess.Popen(
        FRONTEND_CMD,
        cwd=ROOT / "CHCAPP",
        shell=USE_SHELL,
    )
    processes.append(frontend)
    print("✅ Vite frontend starting at http://127.0.0.1:5173")

    try:
        while True:
            exit_codes = [proc.poll() for proc in processes]
            if any(code is not None for code in exit_codes):
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass

    shutdown()


if __name__ == "__main__":
    main()

