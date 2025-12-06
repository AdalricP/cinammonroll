import os
import asyncio
import sounddevice as sd
import numpy as np
from dotenv import load_dotenv
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)

load_dotenv()

API_KEY = os.getenv("DEEPGRAM_API_KEY")

class CallAgent:
    def __init__(self):
        self.deepgram = DeepgramClient(API_KEY)
        self.connection = None
        self.is_running = True

    async def start(self):
        if not API_KEY:
            print("Error: DEEPGRAM_API_KEY not found in environment variables.")
            return

        try:
            # Create a websocket connection to Deepgram
            self.connection = self.deepgram.listen.asyncwebsocket.v("1")

            # Define event handlers
            def on_open(self, open, **kwargs):
                print("Connection Open")

            def on_message(self, result, **kwargs):
                sentence = result.channel.alternatives[0].transcript
                if len(sentence) == 0:
                    return
                
                is_final = result.is_final
                
                if is_final:
                    print(f"Final: {sentence}")
                else:
                    print(f"Interim: {sentence}")
                    # Basic interruption detection logic
                    interrupt_words = ["stop", "wait", "no", "hold on", "cancel"]
                    if any(word in sentence.lower() for word in interrupt_words):
                        print(f"🛑 INTERRUPT DETECTED: User said '{sentence}'")

            def on_metadata(self, metadata, **kwargs):
                pass
                # print(f"Metadata: {metadata}")

            def on_speech_started(self, speech_started, **kwargs):
                print("Speech Started")

            def on_utternace_end(self, utterance_end, **kwargs):
                print("Utterance End")

            def on_close(self, close, **kwargs):
                print("Connection Closed")

            def on_error(self, error, **kwargs):
                print(f"Handled Error: {error}")

            def on_unhandled_error(self, error, **kwargs):
                print(f"Unhandled Error: {error}")

            # Register handlers
            self.connection.on(LiveTranscriptionEvents.Open, on_open)
            self.connection.on(LiveTranscriptionEvents.Transcript, on_message)
            self.connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
            self.connection.on(LiveTranscriptionEvents.SpeechStarted, on_speech_started)
            self.connection.on(LiveTranscriptionEvents.UtteranceEnd, on_utternace_end)
            self.connection.on(LiveTranscriptionEvents.Close, on_close)
            self.connection.on(LiveTranscriptionEvents.Error, on_error)
            self.connection.on(LiveTranscriptionEvents.UnhandledError, on_unhandled_error)

            # Configure Deepgram options
            options = LiveOptions(
                model="nova-2",
                language="en-US",
                smart_format=True,
                interim_results=True,
                utterance_end_ms="1000",
                vad_events=True,
            )

            # Start the connection
            if await self.connection.start(options) is False:
                print("Failed to connect to Deepgram")
                return

            # Open a microphone stream
            microphone = Microphone(self.connection.send)

            # Start microphone
            microphone.start()

            print("Listening... Press Ctrl+C to stop.")
            
            # Keep running until interrupted
            while self.is_running:
                await asyncio.sleep(1)

        except Exception as e:
            print(f"Could not open socket: {e}")
            return

    def stop(self):
        self.is_running = False

async def main():
    agent = CallAgent()
    try:
        await agent.start()
    except KeyboardInterrupt:
        agent.stop()
        print("\nStopping...")

if __name__ == "__main__":
    asyncio.run(main())
