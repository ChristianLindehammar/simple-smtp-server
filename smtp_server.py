import asyncio
import logging
import signal
import sys

from aiosmtpd.controller import Controller

class SMTPHandler:
    async def handle_DATA(self, server, session, envelope):
        print('Message from:', envelope.mail_from)
        print('Message to:', envelope.rcpt_tos)
        print('Message data:')
        print(envelope.content.decode('utf8', errors='replace'))
        print('End of message')
        return '250 OK'

    async def handle_EHLO(self, server, session, envelope, hostname):
        session.host_name = hostname
        return '250 OK'

async def shutdown(signal, loop, controller):
    print(f'Received exit signal {signal.name}...')
    controller.stop()
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

async def main():
    handler = SMTPHandler()
    try:
        controller = Controller(handler, hostname='0.0.0.0', port=2525)
        controller.start()
        print(f"SMTP Server started successfully and listening on 0.0.0.0:2525")
    except Exception as e:
        print(f"Failed to start SMTP server: {e}")
        sys.exit(1)
    
    print("SMTP Server running on port 2525")
    
    # Setup signal handlers
    loop = asyncio.get_running_loop()
    signals = (signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(shutdown(s, loop, controller))
        )
    
    try:
        # Keep the server running
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        controller.stop()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
