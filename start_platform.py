#!/usr/bin/env python3
"""
Simple platform starter for Crane Intelligence
"""
import subprocess
import sys
import time
import os
import signal
import threading
from pathlib import Path

class PlatformStarter:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = True
        
    def start_backend(self):
        """Start the backend server"""
        print("Starting Backend Server...")
        try:
            self.backend_process = subprocess.Popen(
                [sys.executable, "run_backend.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("Backend server started on port 8003")
            return True
        except Exception as e:
            print(f"Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the frontend server"""
        print("Starting Frontend Server...")
        try:
            frontend_dir = Path("frontend")
            if not frontend_dir.exists():
                print("Frontend directory not found!")
                return False
            
            self.frontend_process = subprocess.Popen(
                [sys.executable, "-m", "http.server", "3000"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("Frontend server started on port 3000")
            return True
        except Exception as e:
            print(f"Failed to start frontend: {e}")
            return False
    
    def test_servers(self):
        """Test if servers are running"""
        import requests
        
        print("\nTesting servers...")
        
        # Test backend
        try:
            response = requests.get("http://localhost:8003/health", timeout=5)
            print(f"Backend: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"Backend: Connection failed - {e}")
        
        # Test frontend
        try:
            response = requests.get("http://localhost:3000/homepage.html", timeout=5)
            print(f"Frontend: {response.status_code} - Content length: {len(response.text)}")
        except Exception as e:
            print(f"Frontend: Connection failed - {e}")
    
    def stop_servers(self):
        """Stop all servers"""
        print("\nStopping servers...")
        if self.backend_process:
            self.backend_process.terminate()
        if self.frontend_process:
            self.frontend_process.terminate()
        print("Servers stopped.")
    
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C"""
        print("\nReceived interrupt signal...")
        self.running = False
        self.stop_servers()
        sys.exit(0)
    
    def run(self):
        """Main run method"""
        print("=" * 50)
        print("Starting Crane Intelligence Platform")
        print("=" * 50)
        
        # Set up signal handler
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Start backend
        if not self.start_backend():
            print("Failed to start backend server")
            return
        
        # Wait for backend to start
        print("Waiting for backend to start...")
        time.sleep(8)
        
        # Start frontend
        if not self.start_frontend():
            print("Failed to start frontend server")
            self.stop_servers()
            return
        
        # Wait for frontend to start
        print("Waiting for frontend to start...")
        time.sleep(5)
        
        # Test servers
        self.test_servers()
        
        print("\n" + "=" * 50)
        print("SUCCESS: Platform Started!")
        print("=" * 50)
        print("Main Website: http://localhost:3000/homepage.html")
        print("Admin Portal: http://localhost:3000/admin/dashboard.html")
        print("Backend API: http://localhost:8003/health")
        print("API Docs: http://localhost:8003/docs")
        print("\nPress Ctrl+C to stop servers")
        
        try:
            # Keep running
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_servers()

if __name__ == "__main__":
    starter = PlatformStarter()
    starter.run()