---
name: qwen-speech
description: Local TTS (text-to-speech) and ASR (speech-to-text) services for Apple Silicon, powered by Qwen3 + MLX.
metadata: {"clawdbot":{"emoji":"🎙️","requires":{"python":">=3.13","system":["ffmpeg"]},"primaryEnv":null}}
---

# Qwen Speech MLX

Local speech services providing **TTS** (text-to-speech with voice cloning) and **ASR** (speech-to-text) via Qwen3 models on Apple Silicon.

## Prerequisites

1. **uv** package manager installed
2. **FFmpeg** installed (recommended): `brew install ffmpeg`
   - Required for M4A, AAC, OGG audio formats (common in WeChat voice messages, iPhone recordings, etc.)
   - WAV, MP3, FLAC work without FFmpeg
3. Services must be running before tool use:

```bash
cd /Users/royzhu/software/mytools/python/qwen-tts
make start-all    # Start TTS (:9955) + ASR (:9956) in background
```

## Services

| Service | Port | Endpoint      | Description                |
|---------|------|---------------|----------------------------|
| TTS     | 9955 | POST /v1/tts  | Text to speech (voice clone) |
| ASR     | 9956 | POST /v1/asr  | Speech to text (multi-language) |

## Usage Examples

```bash
# TTS: generate speech
curl -s http://127.0.0.1:9955/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "你好"}' | jq .audio_path

# ASR: transcribe audio
curl -s http://127.0.0.1:9956/v1/asr \
  -F "audio=@recording.wav" \
  -F "language=Chinese" | jq .text

# Service management
make status-all   # Check if services are running
make stop-all     # Stop services
```

## Audio Format Support

| Format         | Support     | FFmpeg Required |
|----------------|-------------|-----------------|
| WAV            | Native      | No              |
| MP3            | Native      | No              |
| FLAC           | Native      | No              |
| M4A / AAC      | Via FFmpeg  | Yes             |
| OGG            | Via FFmpeg  | Yes             |

## ASR Supported Languages

Chinese, English, Japanese, Korean, German, Spanish, French, Italian, Portuguese, Russian, Cantonese

[tool]
name: speak
description: Convert text to speech using voice cloning. Returns the path to the generated WAV audio file. The TTS service must be running (make start-tts).
parameters:
  type: object
  properties:
    text:
      type: string
      description: The text to synthesize into speech.
  required:
    - text
command: |
  RESPONSE=$(curl -s -X POST http://127.0.0.1:9955/v1/tts \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"${text}\"}")
  AUDIO_PATH=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['audio_path'])")
  DURATION=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"{d['duration']:.1f}s processing, {d['audio_duration']:.1f}s audio\")")
  echo "Generated: $AUDIO_PATH ($DURATION)"
  afplay "$AUDIO_PATH"

[tool]
name: transcribe
description: Transcribe an audio file to text using ASR. Supports WAV, MP3, FLAC natively; M4A/AAC/OGG require FFmpeg. The ASR service must be running (make start-asr).
parameters:
  type: object
  properties:
    audio:
      type: string
      description: Path to the audio file to transcribe.
    language:
      type: string
      description: "Language of the audio. Options: Chinese (default), English, Japanese, Korean, German, Spanish, French, Italian, Portuguese, Russian, Cantonese."
  required:
    - audio
command: |
  RESPONSE=$(curl -s -X POST http://127.0.0.1:9956/v1/asr \
    -F "audio=@${audio}" \
    -F "language=${language:-Chinese}")
  TEXT=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['text'])")
  DURATION=$(echo "$RESPONSE" | python3 -c "import sys,json; print(f\"{json.load(sys.stdin)['duration']:.2f}s\")")
  echo "Transcription ($DURATION): $TEXT"
