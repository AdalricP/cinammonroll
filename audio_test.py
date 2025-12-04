import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

def record_audio(duration=5, fs=44100, filename='output.wav'):
    print(f"Recording for {duration} seconds...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished
    print("Recording finished")
    write(filename, fs, recording)  # Save as WAV file
    print(f"Saved to {filename}")

if __name__ == "__main__":
    record_audio()
