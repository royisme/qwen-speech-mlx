import argparse
import os
import sys
import tempfile
import time
from contextlib import asynccontextmanager

import mlx.core as mx
import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile

model = None

MODEL_PATH = "mlx-community/Qwen3-ASR-0.6B-8bit"


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    print(f"Loading Qwen3-ASR MLX Model: {MODEL_PATH}")
    print(f"Python: {sys.executable}")

    try:
        from mlx_audio.stt.utils import load_model as _load_model

        model = _load_model(MODEL_PATH)
        print("ASR Model loaded.")
    except Exception as e:
        print(f"Critical Error loading ASR model: {e}")
        yield
        return

    print("ASR Service ready.")
    yield
    print("Shutting down ASR service...")


app = FastAPI(lifespan=lifespan)


@app.post("/v1/asr")
async def transcribe(
    audio: UploadFile = File(...),
    language: str = Form("Chinese"),
):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    print(f"Transcribing: {audio.filename}")
    start_time = time.perf_counter()

    tmp_path = None
    try:
        suffix = os.path.splitext(audio.filename or "audio.wav")[1] or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await audio.read())
            tmp_path = tmp.name

        mx.reset_peak_memory()

        result = model.generate(tmp_path, language=language, verbose=True)

        duration = time.perf_counter() - start_time
        peak_mem = mx.get_peak_memory() / 1e9

        response = {
            "text": result.text,
            "language": result.language,
            "duration": duration,
            "peak_memory_gb": round(peak_mem, 2),
            "model": MODEL_PATH,
        }

        if result.segments:
            response["segments"] = result.segments

        print(f"Transcribed in {duration:.2f}s, peak mem {peak_mem:.2f}GB")
        return response

    except Exception as e:
        print(f"Transcription failed: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_PATH, "backend": "mlx", "type": "asr"}


def main():
    parser = argparse.ArgumentParser(description="Qwen3 ASR Service")
    parser.add_argument("--port", type=int, default=9956)
    parser.add_argument("--host", type=str, default="127.0.0.1")
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
