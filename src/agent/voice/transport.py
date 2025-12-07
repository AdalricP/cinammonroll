import pyaudio
from pipecat.transports.local.audio import LocalAudioTransport, LocalAudioInputTransport, LocalAudioTransportParams
from pipecat.frames.frames import StartFrame

class SystemAudioInputTransport(LocalAudioInputTransport):
    async def start(self, frame: StartFrame):
        """Override start to enable macOS Voice Processing for AEC."""
        # 1. We open the stream ourselves with the special flag
        if not self._in_stream:
            try:
                # Enable macOS Voice Processing I/O (Built-in AEC)
                # The constant might be missing in some PyAudio versions.
                # 0x40 is paMacCoreStreamUsageFlagsVoiceProcessing
                flags_val = getattr(pyaudio.PaMacCoreStreamInfo, 'paMacCoreStreamUsageFlagsVoiceProcessing', 0x40)
                flags = pyaudio.PaMacCoreStreamInfo(flags=flags_val)
                print(f"DEBUG: Enabling macOS Voice Processing (System AEC) with flags={flags_val}...")
                
                self._sample_rate = self._params.audio_in_sample_rate or frame.audio_in_sample_rate
                # Increase buffer size to 50ms to prevent choppiness
                num_frames = int(self._sample_rate / 100) * 5  # 50ms of audio

                self._in_stream = self._py_audio.open(
                    format=self._py_audio.get_format_from_width(2),
                    channels=self._params.audio_in_channels,
                    rate=self._sample_rate,
                    frames_per_buffer=num_frames,
                    stream_callback=self._audio_in_callback,
                    input=True,
                    input_device_index=self._params.input_device_index,
                    input_host_api_specific_stream_info=flags, # Magic flag
                    start=False # Do not start immediately to prevent race
                )
            except Exception as e:
                print(f"ERROR: Failed to enable System AEC: {e}")
                pass

        # 2. Call super().start() 
        # This pushes StartFrame downstream.
        await super().start(frame)
        
        # 3. Now start the stream
        if self._in_stream:
             self._in_stream.start_stream()
             await self.set_transport_ready(frame)


class SystemLocalAudioTransport(LocalAudioTransport):
    def input(self):
        if not self._input:
            self._input = SystemAudioInputTransport(self._pyaudio, self._params)
        return self._input

def create_transport(
    audio_out_sample_rate=44100,
    audio_in_sample_rate=16000,
    audio_out_enabled=True,
    audio_in_enabled=True,
    vad_enabled=True,
    audio_out_10ms_chunks=2
):
    """
    Creates a SystemLocalAudioTransport (enables Hardware AEC on macOS).
    """
    return SystemLocalAudioTransport(
        LocalAudioTransportParams(
            audio_out_sample_rate=audio_out_sample_rate,
            audio_in_sample_rate=audio_in_sample_rate,
            audio_out_enabled=audio_out_enabled,
            audio_in_enabled=audio_in_enabled,
            vad_enabled=vad_enabled,
            audio_out_10ms_chunks=audio_out_10ms_chunks,
        )
    )
