# Simple SMTP Server

A simple SMTP server with a web interface for viewing received emails.

## Setup and Running

1. Clone this repository
2. Run with Docker Compose:
   ```
   docker-compose up --build
   ```

## Accessing the Web Interface

### From the host machine:
- Open a web browser and navigate to: `http://localhost:8000`

### From other computers on the same network:
- Find your computer's IP address on the local network
  - Linux/Mac: `ifconfig` or `ip addr show`
  - Windows: `ipconfig`
- Open a web browser on another device and navigate to: `http://YOUR_IP_ADDRESS:8000`
  (replace YOUR_IP_ADDRESS with your actual IP address)

## Testing Email Delivery
telnet localhost 2525
EHLO example.com
MAIL FROM:<test@example.com>
RCPT TO:<username@tempmail.local>
DATA
Subject: Test Email

This is a test email body.
.
QUIT

### Using the provided test script:
# Edit the script to use the correct recipient
python test_smtp.py



## Accessing the Web Interface

### From the host machine:
- Open a web browser and navigate to: `http://localhost:8000`

### From other computers on the same network:
- Find your computer's IP address on the local network
  - Linux/Mac: `ifconfig` or `ip addr show`
  - Windows: `ipconfig`
- Open a web browser on another device and navigate to: `http://YOUR_IP_ADDRESS:8000`
  (replace YOUR_IP_ADDRESS with your actual IP address)

## Testing Email Delivery

### Using the provided test script:
```bash
# Make the script executable
chmod +x test_email_sending.sh

# Send a test email to a generated address
./test_email_sending.sh username@tempmail.local