import math
import struct
import os

SAMPLE_RATE = 16000
DURATION = 2
FREQUENCY = 440
AMPLITUDE = 10000

output_folder = "fixtures/synthetic_audio"
os.makedirs(output_folder, exist_ok=True)

output_file = os.path.join(output_folder, "sample_audio.pcm")

with open(output_file, "wb") as file:
    for i in range(SAMPLE_RATE * DURATION):
        sample = AMPLITUDE * math.sin(
            2 * math.pi * FREQUENCY * i / SAMPLE_RATE
        )
        file.write(struct.pack("<h", int(sample)))

print("Synthetic audio fixture created successfully!")
print(output_file)