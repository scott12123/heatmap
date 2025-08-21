Run `python3 server.py` and open `http://localhost:8500` in your browser.

To install the server as a service that starts on boot, run:

    sudo python3 setup.py

This installs any required Python modules and configures a systemd service
that restarts automatically if the server stops.
