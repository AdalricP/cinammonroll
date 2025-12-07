import asyncio
import multiprocessing
import time
import webbrowser
import sys
import os

from src.gym.server import start_server
from main import main as run_agent

def run_server_process():
    """Runs the Gym Server in a separate process."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    print("Starting Gym Server...")
    runner = loop.run_until_complete(start_server())
    loop.run_forever()

async def main():
    # Start Server Process
    server_process = multiprocessing.Process(target=run_server_process)
    server_process.start()
    
    # Wait for server to boot
    time.sleep(2)
    
    # Open Browser
    webbrowser.open("http://localhost:8000")
    
    print("\nStarting Agent... (Press Ctrl+C to stop everything)\n")
    try:
        # Run Agent (it's async)
        await run_agent()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Agent error: {e}")
    finally:
        print("\nShutting down...")
        server_process.terminate()
        server_process.join()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
