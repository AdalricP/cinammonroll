import os
import sys
import asyncio
import argparse
from loguru import logger
from dotenv import load_dotenv


from webrtc_vad import WebRtcVADAnalyzer
from pipecat.frames.frames import EndFrame, LLMMessagesFrame, Frame, OutputAudioRawFrame, InputAudioRawFrame, TranscriptionFrame, TextFrame, InterimTranscriptionFrame, LLMFullResponseStartFrame, LLMFullResponseEndFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask, BaseObserver
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.cartesia import CartesiaTTSService
from pipecat.services.deepgram import DeepgramSTTService
from pipecat.services.groq import GroqLLMService
from pipecat.transports.local.audio import LocalAudioTransport, LocalAudioTransportParams

load_dotenv()

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")

from pipecat.frames.frames import (
    Frame, 
    OutputAudioRawFrame, 
    InputAudioRawFrame, 
    TranscriptionFrame, 
    TextFrame, 
    InterimTranscriptionFrame,
    LLMFullResponseStartFrame,
    LLMFullResponseEndFrame
)
from pipecat.processors.aggregators.llm_response import LLMUserAggregatorParams

class ChatLogger(BaseObserver):
    def __init__(self):
        super().__init__()
        self._bot_speaking = False

    async def on_push_frame(self, data):
        frame = data.frame
        source = data.source
        
        # Handle User Input (Transcription) - Only from STT service
        if isinstance(frame, TranscriptionFrame):
            # Check if source is DeepgramSTTService (by name or type)
            # We can check if the source name contains "Deepgram" or "STT"
            if "Deepgram" in str(source) or "STT" in str(source):
                print(f"\nUser: {frame.text}")
        
        # Handle Bot Output (LLM Streaming) - Only from LLM service
        elif isinstance(frame, LLMFullResponseStartFrame):
            if "Groq" in str(source) or "LLM" in str(source):
                print("Bot: ", end="", flush=True)
                self._bot_speaking = True
        
        elif isinstance(frame, LLMFullResponseEndFrame):
            if "Groq" in str(source) or "LLM" in str(source):
                print() # Newline at end of response
                self._bot_speaking = False
            
        elif isinstance(frame, TextFrame) and not isinstance(frame, (TranscriptionFrame, InterimTranscriptionFrame)):
            # This captures LLM output chunks
            if self._bot_speaking and ("Groq" in str(source) or "LLM" in str(source)):
                print(frame.text, end="", flush=True)

async def main():
    parser = argparse.ArgumentParser(description="Pipecat Voice Agent")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose debug logging")
    args = parser.parse_args()

    if not args.verbose:
        logger.remove()
        logger.add(sys.stderr, level="ERROR") # Hide debug logs
    else:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")

    print("\n--- Pipecat Voice Agent ---")
    print("Tip: Use headphones to avoid the bot hearing itself (echo cancellation is limited).")
    print("---------------------------\n")
    
    # 1. Transport (Local Audio)
    # Reduce buffer size for lower latency
    transport = LocalAudioTransport(
        LocalAudioTransportParams(
            audio_out_sample_rate=44100,
            audio_in_sample_rate=16000,
            audio_out_enabled=True,
            audio_in_enabled=True,
            vad_enabled=True,
            audio_out_10ms_chunks=2, # Reduce output buffer to 10ms
        )
    )

    # 2. VAD (Voice Activity Detection)
    # Using WebRTC VAD as it is compatible with Python 3.14 (unlike Silero/Onnx)
    # Mode 1 is less aggressive (more sensitive) than 3
    vad = WebRtcVADAnalyzer(aggressiveness=1)

    # 3. Services
    
    # STT: Deepgram
    # interim_results=True is CRITICAL for low latency (getting words as they are spoken)
    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        model="nova-2",
        smart_format=True, # Slightly slower but better quality, set to False for max speed
        interim_results=True,
        addons={"echo_cancellation": "true"} # Attempt to use Deepgram's AEC
    )

    # LLM: Groq
    # Llama 3 70b is a good balance of speed and intelligence
    llm = GroqLLMService(
        api_key=os.getenv("GROQ_API_KEY"),
        model="openai/gpt-oss-120b"
    )

    # TTS: Cartesia
    # Sonic English is their fastest model
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="2725ee79-94e8-4348-a0ec-e7ba0c7a16c1", # Updated voice
        model_id="sonic-english" 
    )

    # 4. Context & System Prompt
    messages = [
        {
            "role": "system",
            "content": """You are Aryan (also known as Adalric or Arpa). You are a conversational phone agent with a specific persona. You are extremely technical and good at physics, math and CS.

Style Guide:
- Be casual and technically sharp, but grounded.
- Avoid abbreviations like "tf" or "idk" (say "the fuck" or "I don't know") so the voice sounds natural.
- Keep responses under 2 sentences.
- Do not use emojis.
- Speak out the math, don't slap in the equation, that screws over the TTS.
"""
        }
    ]
    context = OpenAILLMContext(messages)
    context_aggregator = llm.create_context_aggregator(
        context,
        user_params=LLMUserAggregatorParams(enable_emulated_vad_interruptions=True)
    )

    # 5. Pipeline
    pipeline = Pipeline(
        [
            transport.input(),   # Mic input
            stt,                 # Speech to Text
            context_aggregator.user(), # Add user text to context
            llm,                 # LLM generation
            tts,                 # Text to Speech
            transport.output(),  # Speaker output
            context_aggregator.assistant(), # Add assistant response to context
        ]
    )

    # 6. Task
    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True, # Enable barge-in
            enable_metrics=True,
            observers=[ChatLogger()], # Use ChatLogger
        ),
    )

    # 7. Runner
    runner = PipelineRunner()

    print("Starting agent... Press Ctrl+C to exit.")
    
    try:
        await runner.run(task)
    except KeyboardInterrupt:
        print("Exiting...")
        await task.queue_frame(EndFrame())

if __name__ == "__main__":
    asyncio.run(main())
