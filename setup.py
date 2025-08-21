#!/usr/bin/env python3
"""Setup script for installing dependencies and configuring server as a systemd service.

Run this script with sudo to install Python requirements and create a service
that starts ``server.py`` on boot and restarts automatically if it crashes.
"""

import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SERVICE_NAME = "heatmap.service"
SERVICE_PATH = Path("/etc/systemd/system") / SERVICE_NAME
SERVER_PATH = BASE_DIR / "server.py"
REQUIREMENTS = BASE_DIR / "requirements.txt"


def install_requirements():
    """Install Python dependencies if ``requirements.txt`` exists."""
    if REQUIREMENTS.exists():
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS)])


def create_service():
    """Create and enable the systemd service for ``server.py``."""
    user = os.environ.get("SUDO_USER") or "pi"
    service_contents = f"""
[Unit]
Description=Heatmap server
After=network.target

[Service]
ExecStart={sys.executable} {SERVER_PATH}
WorkingDirectory={BASE_DIR}
Restart=always
RestartSec=5
User={user}

[Install]
WantedBy=multi-user.target
""".strip()
    SERVICE_PATH.write_text(service_contents)
    subprocess.check_call(["systemctl", "daemon-reload"])
    subprocess.check_call(["systemctl", "enable", SERVICE_NAME])
    subprocess.check_call(["systemctl", "restart", SERVICE_NAME])


def main():
    if os.geteuid() != 0:
        print("This script must be run as root (use sudo).", file=sys.stderr)
        sys.exit(1)

    install_requirements()
    create_service()
    print("Setup complete. Service installed as 'heatmap'.")


if __name__ == "__main__":
    main()
