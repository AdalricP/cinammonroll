import webrtcvad
from pipecat.audio.vad.vad_analyzer import VADAnalyzer

class WebRtcVADAnalyzer(VADAnalyzer):
    def __init__(self, aggressiveness=3, sample_rate=16000):
        super().__init__(sample_rate=sample_rate)
        self._vad = webrtcvad.Vad(aggressiveness)
        self._frame_duration_ms = 30 # 10, 20, or 30ms

    def num_frames_required(self) -> int:
        # Calculate number of samples per frame
        # sample_rate * duration_ms / 1000
        return int(self.sample_rate * self._frame_duration_ms / 1000)

    def voice_confidence(self, buffer) -> float:
        # webrtcvad expects 16-bit PCM audio
        # buffer is bytes
        try:
            is_speech = self._vad.is_speech(buffer, self.sample_rate)
            return 1.0 if is_speech else 0.0
        except Exception as e:
            # print(f"VAD Error: {e}")
            return 0.0
