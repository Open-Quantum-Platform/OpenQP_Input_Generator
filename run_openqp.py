import os
import webbrowser
import subprocess
import time

BACKEND_SCRIPT = "Backend.py"
FRONTEND_PORT = 8000
FRONTEND_URL = f"http://127.0.0.1:{FRONTEND_PORT}/index.html"

def start_backend():
    """Start the backend server."""
    print("Starting Backend...")
    backend_process = subprocess.Popen(["python3", BACKEND_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return backend_process

def start_frontend():
    """Start the frontend server."""
    print("Starting Frontend...")
    frontend_process = subprocess.Popen(["python3", "-m", "http.server", str(FRONTEND_PORT)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return frontend_process

def open_browser():
    """Open the web interface in the default browser."""
    print("Opening browser...")
    time.sleep(2) 
    webbrowser.open(FRONTEND_URL)

def main():
    """Main script to run Backend, Frontend, and open the browser."""
    try:
        backend_process = start_backend()
        frontend_process = start_frontend()
        
        open_browser()
        
        print("Backend and Frontend are running.")
        print("Press Ctrl+C to stop.")
        
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Stopping servers...")
        backend_process.terminate()
        frontend_process.terminate()
        print("All services stopped.")

if __name__ == "__main__":
    main()

