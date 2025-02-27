import asyncio
import logging
import signal
import sys
import json
import re
from collections import defaultdict
from datetime import datetime
from email.parser import Parser
from email.policy import default
from aiosmtpd.controller import Controller
import aiohttp
from aiohttp import web
import os

# API key for security (should be a strong, random value in production)
API_KEY = os.environ.get('API_KEY', 'your-secure-api-key-here')

# Global variable to store emails in memory
emails_store = defaultdict(list)

class SMTPHandler:
    async def handle_DATA(self, server, session, envelope):
        print('Message from:', envelope.mail_from)
        print('Message to:', envelope.rcpt_tos)
        print('Message data:')
        raw_content = envelope.content.decode('utf8', errors='replace')
        print(raw_content)
        print('End of message')
        
        # Parse the email content
        email_parser = Parser(policy=default)
        parsed_email = email_parser.parsestr(raw_content)
        
        # Extract email data
        subject = parsed_email.get('Subject', 'No Subject')
        sender = parsed_email.get('From', envelope.mail_from)
        date = parsed_email.get('Date', datetime.now().strftime("%a, %d %b %Y %H:%M:%S"))
        
        # Determine content type and get body
        body = ""
        if parsed_email.is_multipart():
            for part in parsed_email.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain" or content_type == "text/html":
                    body = part.get_payload(decode=True).decode(errors='replace')
                    break
        else:
            body = parsed_email.get_payload(decode=True).decode(errors='replace')
        
        # Store email for each recipient
        for rcpt in envelope.rcpt_tos:
            # Extract the username from the email address (before the @)
            username = rcpt.split('@')[0] if '@' in rcpt else rcpt
            
            email_data = {
                'id': len(emails_store[username]) + 1,
                'from': sender,
                'subject': subject,
                'date': date,
                'body': body,
                'raw': raw_content,
                'timestamp': datetime.now().isoformat()
            }
            
            emails_store[username].append(email_data)
            print(f"Stored email for {username}")
            
        return '250 OK'

    # Add these methods to accept all recipients
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        print(f"Received recipient: {address}")
        envelope.rcpt_tos.append(address)
        return '250 OK'
    
    async def handle_EHLO(self, server, session, envelope, hostname):
        session.host_name = hostname
        return '250 OK'

    async def handle_RSET(self, server, session, envelope):
        session.envelope = None
        return '250 OK'

# Get emails for a specific address
def get_emails_for_address(username):
    return emails_store.get(username, [])

# API routes
async def handle_get_emails(request):
    # Check API key
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f'Bearer {API_KEY}':
        return web.json_response({'error': 'Unauthorized'}, status=401)
    
    username = request.match_info.get('username')
    if not username:
        return web.json_response({'error': 'Username required'}, status=400)
    
    emails = get_emails_for_address(username)
    return web.json_response({'emails': emails})

async def handle_check_health(request):
    return web.json_response({'status': 'ok'})

# Setup API server
async def setup_api_server():
    app = web.Application()
    app.add_routes([
        web.get('/api/emails/{username}', handle_get_emails),
        web.get('/health', handle_check_health)
    ])
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8025)
    await site.start()
    print(f"API Server started successfully and listening on 0.0.0.0:8025")
    return runner

async def shutdown(signal, loop, controller, api_runner):
    print(f'Received exit signal {signal.name}...')
    controller.stop()
    await api_runner.cleanup()
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

async def main():
    # Start the API server
    api_runner = await setup_api_server()
    
    # Start the SMTP server
    handler = SMTPHandler()
    try:
        controller = Controller(handler, hostname='0.0.0.0', port=2525)
        controller.start()
        print(f"SMTP Server started successfully and listening on 0.0.0.0:2525")
    except Exception as e:
        print(f"Failed to start SMTP server: {e}")
        await api_runner.cleanup()
        sys.exit(1)
    
    # Setup signal handlers
    loop = asyncio.get_running_loop()
    signals = (signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(shutdown(s, loop, controller, api_runner))
        )
    
    try:
        # Keep the server running
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        controller.stop()
        await api_runner.cleanup()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
