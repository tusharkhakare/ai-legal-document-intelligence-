"""
Single-command launcher for Tata AI Legal Document Intelligence.
Runs both the FastAPI backend and Streamlit frontend together.
"""

import os
import sys
import time
import subprocess
import webbrowser

def check_keys():
    from dotenv import load_dotenv
    load_dotenv()

    has_gemini = bool(os.getenv("GEMINI_API_KEY"))
    has_groq = bool(os.getenv("GROQ_API_KEY"))
    has_openrouter = bool(os.getenv("OPENROUTER_API_KEY"))

    if not (has_gemini or has_groq or has_openrouter):
        print("\n" + "=" * 60)
        print("⚠️  NOTICE: No LLM API Key detected!")
        print("Please create a .env file or set your API key:")
        print("   GEMINI_API_KEY=your_key_here  (Recommended)")
        print("   or GROQ_API_KEY=your_key_here")
        print("See .env.example for reference.")
        print("=" * 60 + "\n")

def main():
    print("\n⚖️  Starting Tata AI Legal Document Intelligence...")
    check_keys()

    # Step 1: Start FastAPI backend on port 8000
    print("🚀 [1/2] Launching Backend API (port 8000)...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    # Allow backend to bind port
    time.sleep(2)

    port = os.getenv("PORT", "8501")
    frontend_host = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")

    # Step 2: Start Streamlit Frontend
    print(f"🌟 [2/2] Launching Streamlit UI (port {port})...")
    frontend_proc = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", port,
            "--server.address", frontend_host,
            "--server.headless", "true"
        ],
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    time.sleep(2)
    try:
        webbrowser.open("http://localhost:8501")
    except Exception:
        pass

    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Done!")

if __name__ == "__main__":
    main()
