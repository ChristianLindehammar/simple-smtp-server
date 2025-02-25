from email.mime.text import MIMEText
import smtplib
import socket

def send_test_email(host='host.docker.internal', port=2525):
    # Create the message
    msg = MIMEText('This is a test message from the test script')
    msg['Subject'] = 'Test Email'
    msg['From'] = 'sender@example.com'
    msg['To'] = 'recipient@example.com'

    print(f"Attempting to connect to SMTP server at {host}:{port}")
    
    try:
        with smtplib.SMTP(host, port, timeout=10) as server:
            print("Connected to SMTP server")
            server.send_message(msg)
            print("Test email sent successfully!")
    except ConnectionRefusedError:
        print(f"Connection refused to {host}:{port}. Make sure the SMTP server is running.")
    except socket.gaierror:
        print(f"Cannot resolve hostname {host}. Try using 'localhost' if running locally or the container IP.")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

if __name__ == "__main__":
    send_test_email(host='localhost')
