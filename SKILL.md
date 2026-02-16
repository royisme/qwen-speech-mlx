---
name: qwen-tts
description: Generate high-quality speech with "Voice Design" (natural language prompts) using Qwen3-TTS locally.
metadata: {"clawdbot":{"emoji":"🗣️","requires":{"python":">=3.10","env":["UV_PYTHON"]},"primaryEnv":null}}
---

# Qwen3-TTS

Generate speech using the Qwen3-TTS model. This skill uses the **1.7B VoiceDesign** model by default, allowing you to "design" the voice using natural language descriptions.

## Usage

```bash
# Basic usage (defaults to a clear voice)
uv run /Users/royzhu/software/mytools/python/qwen-tts/qwen.py "你好，我是 Qwen TTS。"

# With Voice Design (The killer feature!)
uv run /Users/royzhu/software/mytools/python/qwen-tts/qwen.py "你给我听好了，这事没完！" --instruct "一个极其愤怒、咆哮的中年男人，语气急促"

# Specify language
uv run /Users/royzhu/software/mytools/python/qwen-tts/qwen.py "Hello world" --lang English --instruct "A calm British narrator"

# Save to file (no playback)
uv run /Users/royzhu/software/mytools/python/qwen-tts/qwen.py "Test" --output /tmp/test.wav

# Send to Telegram (requires TELEGRAM_CHAT_ID env var)
TELEGRAM_CHAT_ID="1282978471" uv run /Users/royzhu/software/mytools/python/qwen-tts/qwen.py "测试发送"
```

## Setup

1. Ensure `uv` is installed.
2. The service runs on port `9955`. It will auto-start on the first request.
3. **Note**: The first run will download the 1.7B model (~3-4GB), which may take time.

## Voice Design Tips

The `--instruct` parameter is powerful. Try including:
- **Gender/Age**: "Young girl", "Old man", "Middle-aged woman"
- **Emotion**: "Sad", "Happy", "Angry", "Fearful"
- **Tone**: "Sarcastic", "Whispering", "Shouting", "Professional"
- **Accent**: "Beijing accent", "Sichuan dialect" (works best if language is set to Chinese)

Example:
> "一个非常阴阳怪气的年轻女性，说话拖长音，带有嘲讽的笑意"

[tool]
name: speak
description: Speak text using Roy's cloned voice (or others). Use this to reply with voice messages on Telegram. The audio will be automatically sent to the chat.
parameters:
  type: object
  properties:
    text:
      type: string
      description: The text to speak.
    instruct:
      type: string
      description: (Optional) Voice description/instruction (e.g., "Sad", "Excited"). Only works if model is NOT set to BASE (clone).
  required:
    - text
command: |
  cd /Users/royzhu/software/mytools/python/qwen-tts
  TELEGRAM_CHAT_ID="1282978471" uv run /Users/royzhu/software/mytools/python/qwen-tts/qwen.py "${text}" --instruct "${instruct:-A clear voice.}"
