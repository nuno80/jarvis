import sys
from pathlib import Path
from piper import PiperVoice

model = "it_IT-paola-medium.onnx"
engine = PiperVoice.load(model, config_path=model + ".json")

import io
import wave
audio_buffer = io.BytesIO()
with wave.open(audio_buffer, "wb") as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)   # 16-bit
    wav_file.setframerate(engine.config.sample_rate)
    engine.synthesize("Test vocale uno due tre.", wav_file)

audio_buffer.seek(0)
print(f"Dimensione buffer wav: {len(audio_buffer.read())}")
