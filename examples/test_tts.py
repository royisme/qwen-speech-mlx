"""Example: TTS direct inference (no service needed)."""

import gc
import os
import subprocess
import time

from mlx_audio.tts.generate import generate_audio
from mlx_audio.tts.utils import load_model

from qwen_speech import PROMPTS_DIR

MODEL_PATH = "mlx-community/Qwen3-TTS-12Hz-0.6B-Base-8bit"
REF_AUDIO = str(PROMPTS_DIR / "short.wav")
REF_TEXT = "Here is a prompt."
TEXT_TO_SPEAK = "\u201c到今年年底，我们甚至不再需要编程。\u201d 日前，马斯克在一段发布的视频中如是说，人工智能 AI 将直接编写二进制代码，且AI生成的二进制代码将比任何编译器生成的都要高效。"
OUTPUT_DIR = "output"
FILE_PREFIX = "test_generate_audio"


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Loading model: {MODEL_PATH}...")
    model_start = time.perf_counter()
    model = load_model(MODEL_PATH)
    print(f"Model loaded in {time.perf_counter() - model_start:.3f}s.")

    print(f"Generating TTS with voice cloning...")
    print(f"   Text: {TEXT_TO_SPEAK[:60]}...")
    print(f"   Ref Audio: {REF_AUDIO}")

    gen_start = time.perf_counter()

    generate_audio(
        model=model,
        text=TEXT_TO_SPEAK,
        ref_audio=REF_AUDIO,
        ref_text=REF_TEXT,
        lang_code="chinese",
        output_path=OUTPUT_DIR,
        file_prefix=FILE_PREFIX,
        max_tokens=1200,
        temperature=0.7,
        verbose=True,
    )

    print(f"Total generation time: {time.perf_counter() - gen_start:.3f}s")

    output_file = os.path.join(OUTPUT_DIR, f"{FILE_PREFIX}_000.wav")
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file)
        print(f"Output: {output_file} ({file_size / 1024:.1f} KB)")
        subprocess.run(["afplay", output_file], check=False)

    gc.collect()


if __name__ == "__main__":
    main()
