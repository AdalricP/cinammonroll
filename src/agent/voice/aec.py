import numpy as np
import scipy.signal
from pipecat.frames.frames import AudioRawFrame, Frame
from pipecat.processors.frame_processor import FrameProcessor
from loguru import logger
import collections

from pipecat.frames.frames import AudioRawFrame, Frame, StartFrame, EndFrame, CancelFrame

class AECInputProcessor(FrameProcessor):
    def __init__(self, aec_manager: 'AECManager'):
        super().__init__()
        self.manager = aec_manager
        self._input_started = False

    async def process_frame(self, frame: Frame, direction="input"):
        if isinstance(frame, StartFrame):
            self._input_started = True
            await super().process_frame(frame, direction)
            await self.push_frame(frame, direction)
        elif isinstance(frame, (EndFrame, CancelFrame)):
            self._input_started = False
            await super().process_frame(frame, direction)
            await self.push_frame(frame, direction)
        elif isinstance(frame, AudioRawFrame):
            if self._input_started:
                # print("DEBUG: Input frame received")
                clean_audio = self.manager.process_input(frame.audio, frame.num_channels, frame.sample_rate)
                # Use current frame class to preserve type (InputAudioRawFrame vs OutputAudioRawFrame) and metadata capabilities
                new_frame = frame.__class__(audio=clean_audio, sample_rate=frame.sample_rate, num_channels=frame.num_channels)
                await self.push_frame(new_frame, direction)
        else:
            await self.push_frame(frame, direction)

class AECOutputProcessor(FrameProcessor):
    def __init__(self, aec_manager: 'AECManager'):
        super().__init__()
        self.manager = aec_manager
        self._output_started = False

    async def process_frame(self, frame: Frame, direction="output"):
        if isinstance(frame, StartFrame):
            self._output_started = True
            await super().process_frame(frame, direction)
            await self.push_frame(frame, direction)
        elif isinstance(frame, (EndFrame, CancelFrame)):
            self._output_started = False
            await super().process_frame(frame, direction)
            await self.push_frame(frame, direction)
        elif isinstance(frame, AudioRawFrame):
            if self._output_started:
                # print("DEBUG: Output frame received")
                self.manager.buffer_output(frame.audio)
            # Pass output audio through
            await self.push_frame(frame, direction)
        else:
            await self.push_frame(frame, direction)

class AECManager:
    def __init__(self, sample_rate=16000, buffer_ms=400):
        self.sample_rate = sample_rate
        # Keep ~400ms of reference audio
        self.buffer_size = int(sample_rate * buffer_ms / 1000)
        self.reference_buffer = np.zeros(self.buffer_size, dtype=np.float32)
        
    def buffer_output(self, audio: bytes):
        """Called when audio is about to be sent to speakers."""
        # Convert bytes to float32
        audio_int16 = np.frombuffer(audio, dtype=np.int16)
        audio_float = audio_int16.astype(np.float32) / 32768.0
        
        # Roll buffer and add new data
        # If new data is larger than buffer, take last part
        if len(audio_float) >= self.buffer_size:
            self.reference_buffer = audio_float[-self.buffer_size:]
        else:
            self.reference_buffer = np.roll(self.reference_buffer, -len(audio_float))
            self.reference_buffer[-len(audio_float):] = audio_float

    def process_input(self, audio: bytes, num_channels: int, sample_rate: int) -> bytes:
        """Called when audio is received from mic. Performs echo subtraction via Ducking."""
        if len(self.reference_buffer) == 0:
             return audio
             
        # Convert input to float32
        audio_int16 = np.frombuffer(audio, dtype=np.int16)
        input_float = audio_int16.astype(np.float32) / 32768.0
        
        # Check Reference Energy (what the bot is saying)
        # We look at the ENTIRE reference buffer (last ~400ms) to account for system latency.
        # If the bot sent loud audio recently, it's likely playing now or echoing.
        ref_peak = np.max(np.abs(self.reference_buffer))
        
        # Threshold for "Bot is speaking"
        # 0.01 is ~327 amplitude (approx -40dB)
        is_bot_speaking = ref_peak > 0.01
        
        if is_bot_speaking:
            self._hangover_counter = 16 # Keep ducking for ~16 frames (320ms) after speech ends
        elif hasattr(self, '_hangover_counter') and self._hangover_counter > 0:
            self._hangover_counter -= 1
        else:
            self._hangover_counter = 0

        if self._hangover_counter > 0:
             # Apply COMPLETE attenuation (Mute)
             # This prevents any echo leakage.
             clean_float = np.zeros_like(input_float)
        else:
             clean_float = input_float
             
        # Convert back to bytes
        clean_int16 = (clean_float * 32768.0).astype(np.int16)
        return clean_int16.tobytes()
