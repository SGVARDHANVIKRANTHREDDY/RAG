import os
import sys
import time
import subprocess
import webbrowser

def main():
    # Base directory coordinates
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_dir, "chatbot-backend")
    frontend_dir = os.path.join(base_dir, "chatbot-frontend")

    # Locate backend virtual environment python interpreter
    backend_python = os.path.join(backend_dir, "venv", "Scripts", "python.exe")
    if not os.path.exists(backend_python):
        backend_python = "python"

    print("==================================================")
    print("  Starting Multi-User RAG Chatbot Application     ")
    print("==================================================")

    # 1. Start FastAPI Backend
    print(f"\n[1/3] Starting Backend Server on http://localhost:8000...")
    backend_process = subprocess.Popen(
        [backend_python, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=backend_dir,
        shell=True
    )

    # 2. Start Next.js Frontend
    print(f"[2/3] Starting Frontend Client on http://localhost:3000...")
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        shell=True
    )

    # 3. Wait for initialization
    print("\n[3/3] Waiting 4 seconds for services to initialize...")
    time.sleep(4)

    # 4. Open default web browser
    print("\n[OK] Launching browser interface...")
    webbrowser.open("http://localhost:3000")

    print("\n==================================================")
    print("  Application is running live!                    ")
    print("  Press Ctrl+C in this terminal to shut down.     ")
    print("==================================================")

    try:
        while True:
            time.sleep(1)
            # Exit loop if any server process exits unexpectedly
            if backend_process.poll() is not None:
                print("\n[Warning] Backend process exited unexpectedly.")
                break
            if frontend_process.poll() is not None:
                print("\n[Warning] Frontend process exited unexpectedly.")
                break
    except KeyboardInterrupt:
        print("\n[Info] Keyboard interrupt received.")
    finally:
        print("\nShutting down active servers...")
        
        # Terminate backend process
        if backend_process.poll() is None:
            try:
                backend_process.terminate()
                backend_process.wait(timeout=3)
            except Exception:
                pass
                
        # Terminate frontend process
        if frontend_process.poll() is None:
            try:
                frontend_process.terminate()
                frontend_process.wait(timeout=3)
            except Exception:
                pass

        print("[OK] All processes cleaned up successfully. Goodbye!")

if __name__ == "__main__":
    main()
