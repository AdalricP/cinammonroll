import asyncio
import sys
from pipecat.frames.frames import EndFrame
from src.agent.factory import create_react_agent

import argparse

async def main():
    parser = argparse.ArgumentParser(description="Pipecat Voice Agent")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose debug logging")
    parser.add_argument("--mute", action="store_true", help="Mute TTS output (Silent Mode)")
    parser.add_argument("--no-cut", action="store_true", help="Disable barge-in interruption (AI finishes speaking)")
    
    # If run from gym_runner, we might need to handle unknown args or ignore them if gym_runner adds any?
    # But gym_runner doesn't use argparse.
    
    # However, if gym_runner is the entry point, parser.prog might be gym_runner.py
    # That's fine.
    
    args, unknown = parser.parse_known_args() # Use parse_known_args just in case

    runner, task = await create_react_agent(verbose=args.verbose, mute_tts=args.mute, allow_interruptions=not args.no_cut)

    print("Starting agent... Press Ctrl+C to exit.")
    
    try:
        await runner.run(task)
    except KeyboardInterrupt:
        print("Exiting...")
        await task.queue_frame(EndFrame())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
