"""Example: Test ASR service (service must be running)."""

import sys
import time

import requests

from qwen_speech import PROMPTS_DIR

ASR_URL = "http://127.0.0.1:9956/v1/asr"
TEST_AUDIO = str(PROMPTS_DIR / "default.wav")


def main():
    print(f"Sending {TEST_AUDIO} to ASR service at {ASR_URL}")
    start = time.perf_counter()

    with open(TEST_AUDIO, "rb") as f:
        resp = requests.post(ASR_URL, files={"audio": ("test.wav", f, "audio/wav")})

    elapsed = time.perf_counter() - start

    if resp.status_code != 200:
        print(f"Error {resp.status_code}: {resp.text}")
        sys.exit(1)

    data = resp.json()
    print(f"Transcription: {data['text']}")
    print(f"Language: {data.get('language', 'N/A')}")
    print(f"Server processing: {data['duration']:.2f}s")
    print(f"Total round-trip: {elapsed:.2f}s")
    print(f"Peak memory: {data.get('peak_memory_gb', 'N/A')}GB")

    if "segments" in data:
        print(f"Segments: {len(data['segments'])}")
        for seg in data["segments"]:
            print(f"  [{seg.get('start', '?'):.2f}s - {seg.get('end', '?'):.2f}s] {seg.get('text', '')}")


if __name__ == "__main__":
    main()
