import subprocess
import sys
import time
import webbrowser
import os
import signal
import logging
from pathlib import Path

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    filename=log_dir / "launcher.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_dependencies():
    """Check if all required packages are installed"""
    try:
        import flask
        import flask_cors
        import requests
        import gtts
        import pygame
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Installing dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            return True
        except subprocess.CalledProcessError:
            print("Failed to install dependencies. Please run: pip install -r requirements.txt")
            return False

def start_backend():
    """Start the Flask backend server"""
    try:
        # Check if port 5000 is already in use
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 5000))
        sock.close()
        
        if result == 0:
            logging.error("Port 5000 is already in use. Please close any other applications using this port.")
            print("Error: Port 5000 is already in use. Please close any other applications using this port.")
            return None
            
        process = subprocess.Popen(
            [sys.executable, "Backend.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Wait briefly and check if process is still running
        time.sleep(2)
        if process.poll() is not None:
            out, err = process.communicate()
            logging.error(f"Backend failed to start. Error: {err}")
            print(f"Error starting backend: {err}")
            return None
            
        logging.info("Backend server started successfully")
        return process
    except Exception as e:
        logging.error(f"Failed to start backend: {e}")
        print(f"Error starting backend: {e}")
        return None

def start_frontend():
    """Start the Tkinter frontend application"""
    try:
        process = subprocess.Popen(
            [sys.executable, "FrontEndAudio4.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Wait briefly and check if process is still running
        time.sleep(2)
        if process.poll() is not None:
            out, err = process.communicate()
            logging.error(f"Frontend failed to start. Error: {err}")
            print(f"Error starting frontend: {err}")
            return None
            
        logging.info("Frontend application started successfully")
        return process
    except Exception as e:
        logging.error(f"Failed to start frontend: {e}")
        print(f"Error starting frontend: {e}")
        return None

def cleanup(processes):
    """Clean up processes on exit"""
    for process in processes:
        if process:
            try:
                if sys.platform == 'win32':
                    subprocess.call(['taskkill', '/F', '/T', '/PID', str(process.pid)])
                else:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            except Exception as e:
                logging.error(f"Error during cleanup: {e}")

def main():
    """Main function to start the application"""
    print("Starting Spanish Learning Quiz Application...")
    logging.info("Application startup initiated")

    # Check dependencies
    if not check_dependencies():
        return

    try:
        # Start backend
        print("Starting backend server...")
        backend_process = start_backend()
        if not backend_process:
            return

        # Wait for backend to initialize
        time.sleep(2)

        # Start frontend
        print("Starting frontend application...")
        frontend_process = start_frontend()
        if not frontend_process:
            cleanup([backend_process])
            return

        # Monitor processes
        processes = [backend_process, frontend_process]
        try:
            while all(p.poll() is None for p in processes):
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            cleanup(processes)

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"An error occurred: {e}")
        cleanup([backend_process, frontend_process])

if __name__ == "__main__":
    main()
