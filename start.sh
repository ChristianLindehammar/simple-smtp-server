#!/bin/bash
set -e

# Start the SMTP server in the background
echo "Starting SMTP server..."
python smtp_server.py &
SMTP_PID=$!

# Wait briefly to ensure SMTP server is up
sleep 2

# Start the web interface in the foreground
echo "Starting web interface..."
python app.py

# If the web interface stops, also stop the SMTP server
kill $SMTP_PID
