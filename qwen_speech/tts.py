import argparse
import gc
import os
import sys
import time
from contextlib import asynccontextmanager

import numpy as np
import soundfile as sf
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from qwen_speech import PROMPTS_DIR

model = None
ref_audio_cache = None

MODEL_PATH = "mlx-community/Qwen3-TTS-12Hz-0.6B-Base-8bit"
OUTPUT_DIR = os.getenv("QWEN_OUTPUT_DIR", "output")
OUTPUT_SAMPLE_RATE = 24000
REF_AUDIO = str(PROMPTS_DIR / "default.wav")
REF_TEXT = "请告诉我prompt"


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, ref_audio_cache
    print(f"Loading Qwen3-TTS MLX Model: {MODEL_PATH}")
    print(f"Python: {sys.executable}")

    try:
        from mlx_audio.tts.utils import load_model as _load_model

        model = _load_model(MODEL_PATH)
        print("Model loaded.")
    except Exception as e:
        print(f"Critical Error loading MLX model: {e}")
        yield
        return

    try:
        from mlx_audio.tts.generate import load_audio

        ref_audio_cache = load_audio(REF_AUDIO, sample_rate=OUTPUT_SAMPLE_RATE)
        print(f"Reference audio cached: {REF_AUDIO}")
    except Exception as e:
        print(f"Warning: Failed to cache ref audio: {e}")

    print("TTS Service ready.")
    yield
    print("Shutting down TTS service...")


app = FastAPI(lifespan=lifespan)


class TTSRequest(BaseModel):
    text: str


@app.post("/v1/tts")
async def generate_tts(req: TTSRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    if ref_audio_cache is None:
        raise HTTPException(status_code=503, detail="Reference audio not loaded")

    print(f"Generating: {req.text[:40]}...")
    start_time = time.perf_counter()

    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        file_stem = f"tts_{int(time.time() * 1000)}_{os.getpid()}"
        output_file = os.path.join(OUTPUT_DIR, f"{file_stem}.wav")

        results = list(
            model.generate(
                text=req.text,
                ref_audio=ref_audio_cache,
                ref_text=REF_TEXT,
                lang_code="chinese",
                max_tokens=1200,
                temperature=0.7,
                verbose=True,
            )
        )

        if not results:
            raise RuntimeError("No audio generated.")

        audio_np = np.array(results[0].audio)
        sf.write(output_file, audio_np, OUTPUT_SAMPLE_RATE)

        duration = time.perf_counter() - start_time
        audio_duration = len(audio_np) / OUTPUT_SAMPLE_RATE
        audio_stats = {
            "min": float(np.min(audio_np)),
            "max": float(np.max(audio_np)),
            "rms": float(np.sqrt(np.mean(np.square(audio_np)))),
        }

        print(f"Generated in {duration:.2f}s, audio {audio_duration:.2f}s -> {output_file}")

        gc.collect()

        return {
            "audio_path": output_file,
            "duration": duration,
            "audio_duration": audio_duration,
            "model": MODEL_PATH,
            "audio_stats": audio_stats,
        }

    except Exception as e:
        print(f"Generation failed: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_PATH, "backend": "mlx", "type": "tts"}


def main():
    parser = argparse.ArgumentParser(description="Qwen3 TTS Service")
    parser.add_argument("--port", type=int, default=9955)
    parser.add_argument("--host", type=str, default="127.0.0.1")
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
