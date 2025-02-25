# Simple SMTP Server

This is a simple SMTP server that receives emails and prints them to the console. It's packaged in a Docker container for easy deployment.

## Usage

### Build and run with Docker

```bash
docker build -t simple-smtp-server .
docker run -p 25:25 simple-smtp-server
```

### Or use Docker Compose

```bash
docker-compose up -d
```

## Testing the Server

### Method 1: Using the test script
```bash
# If running locally (outside Docker)
python test_smtp.py

# Or specify the Docker container IP directly
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' simple-smtp-server-smtp-1
python test_smtp.py <container-ip> 2525
```

### Method 2: Using telnet
```bash
# First get the container IP
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' simple-smtp-server-smtp-1

# Then connect using the container IP
telnet <container-ip> 2525
# Then enter these commands:
EHLO example.com
MAIL FROM: <sender@example.com>
RCPT TO: <recipient@example.com>
DATA
Subject: Test Email
This is a test email.
.
QUIT
```

### Method 3: Using curl
```bash
curl smtp://localhost:2525 --mail-from sender@example.com --mail-rcpt recipient@example.com --upload-file - <<EOF
Subject: Test Email
From: sender@example.com
To: recipient@example.com

This is a test email body.
EOF
```

### Troubleshooting
- If you get "Connection refused", make sure the container is running:
  ```bash
  docker compose ps
  docker compose logs -f
  ```
- Check the container IP and ensure it's reachable:
  ```bash
  docker network inspect simple-smtp-server_default
  ```
