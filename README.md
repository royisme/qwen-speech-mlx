**English** | [中文](README_zh.md)

# Qwen Speech MLX

Local TTS (text-to-speech) and ASR (speech-to-text) services for Apple Silicon, powered by [Qwen3](https://github.com/QwenLM/Qwen3) models and the [MLX](https://github.com/ml-explore/mlx) framework.

## Features

- **TTS (Text-to-Speech)** -- Qwen3-TTS-0.6B 8bit model with voice cloning support
- **ASR (Speech-to-Text)** -- Qwen3-ASR-0.6B 8bit model, supports Chinese, English, Japanese, Korean, German, Spanish, French, Italian, Portuguese, Russian, and Cantonese
- Pure MLX inference, no PyTorch required, low memory footprint
- FastAPI service architecture with models kept in memory for fast responses
- Independent processes: start TTS and ASR separately as needed

## Requirements

- macOS (Apple Silicon M1/M2/M3/M4)
- Python >= 3.13
- [uv](https://docs.astral.sh/uv/) package manager

## Quick Start

```bash
# 1. Clone and install
git clone <repo-url> && cd qwen-speech
uv sync

# 2. Start services
uv run qwen-tts    # Start TTS service on :9955
uv run qwen-asr    # Start ASR service on :9956
# Or start both in background:
make start-all

# 3. Call the APIs
# TTS: text -> speech
curl -X POST http://127.0.0.1:9955/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test."}'

# ASR: speech -> text
curl -X POST http://127.0.0.1:9956/v1/asr \
  -F "audio=@audio.wav" \
  -F "language=English"
```

## CLI Commands

After installation, the following commands are available:

```bash
uv run qwen-tts [--host HOST] [--port PORT]   # default 127.0.0.1:9955
uv run qwen-asr [--host HOST] [--port PORT]   # default 127.0.0.1:9956
```

## API Reference

### TTS -- Text-to-Speech

**`POST /v1/tts`** -- port 9955

Request body (JSON):

| Field  | Type   | Required | Description              |
|--------|--------|----------|--------------------------|
| `text` | string | yes      | Text to synthesize       |

Example:

```bash
curl -X POST http://127.0.0.1:9955/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "The quick brown fox jumps over the lazy dog."}'
```

Response:

```json
{
  "audio_path": "output/tts_xxx.wav",
  "duration": 11.6,
  "audio_duration": 23.04,
  "model": "mlx-community/Qwen3-TTS-12Hz-0.6B-Base-8bit",
  "audio_stats": {"min": -0.8, "max": 0.8, "rms": 0.12}
}
```

### ASR -- Speech-to-Text

**`POST /v1/asr`** -- port 9956

Request body (multipart/form-data):

| Field      | Type   | Required | Description                        |
|------------|--------|----------|------------------------------------|
| `audio`    | file   | yes      | Audio file (WAV, MP3, etc.)        |
| `language` | string | no       | Language, default `Chinese`        |

Supported languages: Chinese, English, Japanese, Korean, German, Spanish, French, Italian, Portuguese, Russian, Cantonese

Example:

```bash
curl -X POST http://127.0.0.1:9956/v1/asr \
  -F "audio=@recording.wav" \
  -F "language=English"
```

Response:

```json
{
  "text": "Hello, this is a test.",
  "language": "English",
  "duration": 0.75,
  "peak_memory_gb": 1.72,
  "model": "mlx-community/Qwen3-ASR-0.6B-8bit",
  "segments": [{"text": "Hello, this is a test.", "start": 0.0, "end": 3.0}]
}
```

### Health Check

```bash
curl http://127.0.0.1:9955/health   # TTS
curl http://127.0.0.1:9956/health   # ASR
```

## Voice Cloning

The TTS service uses built-in reference audio for voice cloning. To use your own voice:

1. Record 3-10 seconds of clear speech and save it as a WAV file
2. Replace `qwen_speech/prompts/default.wav` with your recording
3. Update `REF_TEXT` in `qwen_speech/tts.py` to match the transcript of your recording
4. Restart the service: `make restart-tts`

## Make Commands

| Command              | Description                                    |
|----------------------|------------------------------------------------|
| `make install`       | Install dependencies                           |
| `make start-all`     | Start TTS + ASR in background                  |
| `make stop-all`      | Stop all services                              |
| `make restart-all`   | Restart all services                           |
| `make status-all`    | Check status of all services                   |
| `make start-tts`     | Start TTS in background (:9955)                |
| `make start-asr`     | Start ASR in background (:9956)                |
| `make stop-tts`      | Stop TTS                                       |
| `make stop-asr`      | Stop ASR                                       |
| `make logs-tts`      | View TTS logs                                  |
| `make logs-asr`      | View ASR logs                                  |
| `make test-tts`      | Direct TTS inference test                      |
| `make test-asr`      | ASR service test (requires running service)    |
| `make clean`         | Clean PID and log files                        |

## Models

| Service | Model                                          | Size    |
|---------|-------------------------------------------------|---------|
| TTS     | `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-8bit`  | ~600MB  |
| ASR     | `mlx-community/Qwen3-ASR-0.6B-8bit`             | ~1GB    |

Models are automatically downloaded from HuggingFace and cached on first launch.

## Project Structure

```
├── qwen_speech/             # Python package
│   ├── __init__.py
│   ├── tts.py               # TTS service (FastAPI)
│   ├── asr.py               # ASR service (FastAPI)
│   └── prompts/             # Voice cloning reference audio
│       ├── default.wav
│       └── short.wav
├── examples/
│   ├── test_tts.py
│   └── test_asr.py
├── launch.sh                # Background service management
├── Makefile
├── pyproject.toml
└── uv.lock
```

## Performance (M4 Max)

| Task                          | Time    | Memory  |
|-------------------------------|---------|---------|
| TTS: ~50 Chinese characters   | ~11s    | ~9GB    |
| ASR: 3s audio                 | ~0.75s  | ~1.7GB  |
| ASR: 57s audio                | ~1.2s   | ~2.6GB  |
