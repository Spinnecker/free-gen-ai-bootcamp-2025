import wave
import struct
import math

# Create a WAV file with a short "incorrect" buzzer sound
sampleRate = 44100
duration = 0.3  # seconds
frequency = 220.0  # Hz - low A note
volume = 0.5

# Create the audio data
wavetable = []
for i in range(int(sampleRate * duration)):
    t = float(i) / sampleRate  # time in seconds
    # Create a descending frequency
    freq = frequency * (1.0 - t/duration)
    # Add some harmonics for a richer sound
    sample = volume * (
        math.sin(2.0 * math.pi * freq * t) * 0.6 +  # fundamental
        math.sin(4.0 * math.pi * freq * t) * 0.3 +  # 2nd harmonic
        math.sin(6.0 * math.pi * freq * t) * 0.1    # 3rd harmonic
    )
    # Convert to 16-bit integer
    wavetable.append(int(sample * 32767))

# Write the WAV file
with wave.open('assets/incorrect.wav', 'w') as wav:
    wav.setnchannels(1)  # mono
    wav.setsampwidth(2)  # 16-bit
    wav.setframerate(sampleRate)
    # Write the frames
    for sample in wavetable:
        wav.writeframes(struct.pack('h', sample))
