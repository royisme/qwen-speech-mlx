[English](README.md) | **中文**

# Qwen Speech MLX

基于 [Qwen3](https://github.com/QwenLM/Qwen3) 模型和 [MLX](https://github.com/ml-explore/mlx) 框架的 Apple Silicon 本地语音服务，提供 TTS（文本转语音）和 ASR（语音转文字）两项能力。

---

## 目录

- [特性](#特性)
- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [CLI 命令](#cli-命令)
- [API 参考](#api-参考)
  - [TTS — 文本转语音](#tts--文本转语音)
  - [ASR — 语音转文字](#asr--语音转文字)
  - [健康检查](#健康检查)
- [声音克隆](#声音克隆)
- [Make 命令](#make-命令)
- [使用的模型](#使用的模型)
- [项目结构](#项目结构)
- [性能参考](#性能参考m4-max)

---

## 特性

- **TTS（语音合成）** — Qwen3-TTS-0.6B 8bit，支持声音克隆
- **ASR（语音识别）** — Qwen3-ASR-0.6B 8bit，支持中英日韩等多语种
- 纯 MLX 推理，无需 PyTorch，内存占用低
- FastAPI 服务架构，模型常驻内存，请求响应快
- 独立进程：TTS 和 ASR 可按需单独启动

## 系统要求

| 项目       | 要求                                           |
|------------|------------------------------------------------|
| 操作系统   | macOS（Apple Silicon M1 / M2 / M3 / M4）       |
| Python     | >= 3.13                                        |
| 包管理器   | [uv](https://docs.astral.sh/uv/)              |

## 快速开始

```bash
# 1. 克隆并安装
git clone https://github.com/royisme/qwen-speech-mlx.git && cd qwen-speech-mlx
uv sync

# 2. 启动服务（二选一）
uv run qwen-tts                   # 启动 TTS 服务 :9955
uv run qwen-asr                   # 启动 ASR 服务 :9956
# 或后台启动
make start-all                     # 同时后台启动 TTS + ASR

# 3. 调用示例
# TTS: 文字 -> 语音
curl -X POST http://127.0.0.1:9955/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "你好，这是一段测试语音。"}'

# ASR: 语音 -> 文字
curl -X POST http://127.0.0.1:9956/v1/asr \
  -F "audio=@audio.wav" \
  -F "language=Chinese"
```

> 首次启动时，模型会自动从 HuggingFace 下载并缓存到本地，之后启动无需重复下载。

## CLI 命令

安装后可直接使用以下命令：

```bash
uv run qwen-tts [--host HOST] [--port PORT]   # 默认 127.0.0.1:9955
uv run qwen-asr [--host HOST] [--port PORT]   # 默认 127.0.0.1:9956
```

| 参数     | 说明             | 默认值      |
|----------|------------------|-------------|
| `--host` | 监听地址         | `127.0.0.1` |
| `--port` | 监听端口         | TTS: `9955`，ASR: `9956` |

---

## API 参考

### TTS — 文本转语音

**`POST /v1/tts`** — 端口 9955

**请求体**（`application/json`）：

| 字段   | 类型   | 必填 | 说明           |
|--------|--------|------|----------------|
| `text` | string | 是   | 要合成的文本   |

**curl 示例：**

```bash
curl -X POST http://127.0.0.1:9955/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "欢迎使用 Qwen Speech MLX 语音合成服务。"}'
```

**响应示例：**

```json
{
  "audio_path": "output/tts_xxx.wav",
  "duration": 11.6,
  "audio_duration": 23.04,
  "model": "mlx-community/Qwen3-TTS-12Hz-0.6B-Base-8bit",
  "audio_stats": {
    "min": -0.8,
    "max": 0.8,
    "rms": 0.12
  }
}
```

**响应字段说明：**

| 字段             | 类型   | 说明                           |
|------------------|--------|--------------------------------|
| `audio_path`     | string | 生成的音频文件路径             |
| `duration`       | float  | 推理耗时（秒）                 |
| `audio_duration` | float  | 生成音频的时长（秒）           |
| `model`          | string | 使用的模型名称                 |
| `audio_stats`    | object | 音频统计信息（最小值、最大值、RMS） |

---

### ASR — 语音转文字

**`POST /v1/asr`** — 端口 9956

**请求体**（`multipart/form-data`）：

| 字段       | 类型   | 必填 | 说明                           |
|------------|--------|------|--------------------------------|
| `audio`    | file   | 是   | 音频文件（WAV、MP3 等）        |
| `language` | string | 否   | 识别语言，默认 `Chinese`       |

**支持语言：**

| 语言       | 值           |
|------------|--------------|
| 中文       | `Chinese`    |
| 英语       | `English`    |
| 日语       | `Japanese`   |
| 韩语       | `Korean`     |
| 德语       | `German`     |
| 西班牙语   | `Spanish`    |
| 法语       | `French`     |
| 意大利语   | `Italian`    |
| 葡萄牙语   | `Portuguese` |
| 俄语       | `Russian`    |
| 粤语       | `Cantonese`  |

**curl 示例：**

```bash
# 使用默认语言（中文）
curl -X POST http://127.0.0.1:9956/v1/asr \
  -F "audio=@recording.wav"

# 指定语言
curl -X POST http://127.0.0.1:9956/v1/asr \
  -F "audio=@recording.wav" \
  -F "language=English"
```

**响应示例：**

```json
{
  "text": "你好，这是一段测试语音。",
  "language": "Chinese",
  "duration": 0.75,
  "peak_memory_gb": 1.72,
  "model": "mlx-community/Qwen3-ASR-0.6B-8bit",
  "segments": [
    {
      "text": "你好，这是一段测试语音。",
      "start": 0.0,
      "end": 3.0
    }
  ]
}
```

**响应字段说明：**

| 字段             | 类型   | 说明                         |
|------------------|--------|------------------------------|
| `text`           | string | 完整转写文本                 |
| `language`       | string | 识别使用的语言               |
| `duration`       | float  | 推理耗时（秒）               |
| `peak_memory_gb` | float  | 推理峰值内存占用（GB）       |
| `model`          | string | 使用的模型名称               |
| `segments`       | array  | 分段结果，含文本和时间戳     |

---

### 健康检查

两个服务均提供健康检查接口：

```bash
curl http://127.0.0.1:9955/health   # TTS 服务
curl http://127.0.0.1:9956/health   # ASR 服务
```

---

## 声音克隆

TTS 服务内置参考音频用于声音克隆。如果要使用自己的声音：

1. 录制一段 3-10 秒的清晰语音，保存为 WAV 格式
2. 替换 `qwen_speech/prompts/default.wav`
3. 修改 `qwen_speech/tts.py` 中的 `REF_TEXT` 为你录音对应的文字内容
4. 重启服务：`make restart-tts`

> 参考音频质量直接影响克隆效果。建议在安静环境下录制，避免背景噪音。

## Make 命令

| 命令                 | 说明                        |
|----------------------|-----------------------------|
| `make install`       | 安装依赖（等同于 `uv sync`）|
| `make start-all`     | 后台启动 TTS + ASR          |
| `make stop-all`      | 停止所有服务                |
| `make restart-all`   | 重启所有服务                |
| `make status-all`    | 查看所有服务状态            |
| `make start-tts`     | 单独后台启动 TTS (:9955)    |
| `make start-asr`     | 单独后台启动 ASR (:9956)    |
| `make stop-tts`      | 停止 TTS 服务               |
| `make stop-asr`      | 停止 ASR 服务               |
| `make logs-tts`      | 查看 TTS 日志               |
| `make logs-asr`      | 查看 ASR 日志               |
| `make test-tts`      | TTS 直接推理测试            |
| `make test-asr`      | ASR 服务测试（需先启动服务）|
| `make clean`         | 清理 PID 和日志文件         |

## 使用的模型

| 服务 | 模型                                          | 大小    |
|------|-----------------------------------------------|---------|
| TTS  | `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-8bit`| ~600MB  |
| ASR  | `mlx-community/Qwen3-ASR-0.6B-8bit`          | ~1GB    |

模型在首次启动时自动从 HuggingFace 下载并缓存到 `~/.cache/huggingface/` 目录，后续启动无需重复下载。

## 项目结构

```
qwen-speech/
├── qwen_speech/             # Python 包
│   ├── __init__.py
│   ├── tts.py               # TTS 服务 (FastAPI)
│   ├── asr.py               # ASR 服务 (FastAPI)
│   └── prompts/             # 声音克隆参考音频
│       ├── default.wav
│       └── short.wav
├── examples/                # 示例和测试脚本
│   ├── test_tts.py
│   └── test_asr.py
├── launch.sh                # 后台服务管理脚本
├── Makefile                 # 快捷命令
├── pyproject.toml           # 项目配置和依赖
└── uv.lock                 # 锁定的依赖版本
```

## 性能参考（M4 Max）

| 任务                    | 耗时    | 内存占用 |
|-------------------------|---------|----------|
| TTS: 一段中文（约50字） | 约 11s  | 约 9GB   |
| ASR: 3s 音频            | 约 0.75s| 约 1.7GB |
| ASR: 57s 音频           | 约 1.2s | 约 2.6GB |

> 以上数据在 Apple M4 Max 芯片上测得，实际性能因硬件配置和系统负载而异。
