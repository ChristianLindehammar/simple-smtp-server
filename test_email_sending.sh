#!/bin/bash
set -e

EMAIL_TO=$1
if [ -z "$EMAIL_TO" ]; then
  echo "Usage: $0 <email_address>"
  echo "Example: $0 b76zkeh7w4@tempmail.local"
  exit 1
fi

echo "Sending test email to $EMAIL_TO..."

# Extract username for checking
USERNAME=$(echo $EMAIL_TO | cut -d@ -f1)

cat <<EOF | telnet localhost 2525
EHLO example.com
MAIL FROM:<test@example.com>
RCPT TO:<$EMAIL_TO>
DATA
Subject: Test Email from Command Line

This is a test email sent from the command line.
Testing the SMTP server functionality.

.
QUIT
EOF

echo -e "\nChecking if email was received..."
sleep 1
curl -s -X POST -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\"}" \
  http://localhost:8000/api/check-emails | jq .

echo -e "\nDone! If you see email data above, the sending was successful."
