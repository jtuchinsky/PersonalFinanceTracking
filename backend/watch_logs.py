#!/usr/bin/env python3
"""
Simple log watcher for the Finance Tracker backend
Shows verification codes and important events in real-time
"""
import time
import subprocess
import re
import os
from datetime import datetime

def watch_backend_logs():
    """Watch admin server for 2FA verification codes and important events"""
    print("🔍 Watching backend logs for 2FA codes and events...")
    print("=" * 60)

    # Start the admin server process if not running
    try:
        # Check if admin server is running
        result = subprocess.run(['pgrep', '-f', 'admin_server.py'],
                              capture_output=True, text=True)
        if not result.stdout.strip():
            print("⚠️  Admin server not running. Starting it...")
            # Start admin server in background
            subprocess.Popen(['python', 'admin_server.py'],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
            time.sleep(3)
    except Exception as e:
        print(f"Error checking/starting admin server: {e}")

    # Monitor logs by following the process output
    try:
        # Get the PID of admin_server.py
        result = subprocess.run(['pgrep', '-f', 'admin_server.py'],
                              capture_output=True, text=True)
        if result.stdout.strip():
            pid = result.stdout.strip().split('\n')[0]
            print(f"📡 Monitoring admin server process (PID: {pid})")
            print("💡 Look for verification codes in the output below:")
            print("-" * 60)

            # Use script to follow logs (alternative approach)
            proc = subprocess.Popen(['python', 'admin_server.py'],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  universal_newlines=True,
                                  bufsize=1)

            verification_code_pattern = r'verification code is: (\d{6})'

            for line in iter(proc.stdout.readline, ''):
                line = line.strip()
                if line:
                    timestamp = datetime.now().strftime("%H:%M:%S")

                    # Highlight verification codes
                    if 'verification code is:' in line:
                        match = re.search(verification_code_pattern, line)
                        if match:
                            code = match.group(1)
                            print(f"🔑 [{timestamp}] VERIFICATION CODE: {code}")
                    elif 'MOCK EMAIL SENT' in line:
                        print(f"📧 [{timestamp}] Email sent")
                    elif 'POST /api/auth/login-enhanced' in line:
                        print(f"🔐 [{timestamp}] 2FA login attempt")
                    elif 'INFO:' in line and ('POST' in line or 'GET' in line):
                        # Show only relevant API calls
                        if any(endpoint in line for endpoint in ['/auth/', '/admin/']):
                            print(f"🌐 [{timestamp}] {line}")

        else:
            print("❌ Admin server not found running")

    except KeyboardInterrupt:
        print("\n👋 Stopping log monitor...")
    except Exception as e:
        print(f"❌ Error monitoring logs: {e}")

if __name__ == "__main__":
    watch_backend_logs()