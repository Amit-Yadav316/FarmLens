import torch
import soundfile as sf
import numpy as np
import subprocess
import os
import uuid
from transformers import AutoModel
from backend.config.settings import get_settings
 
settings = get_settings()
 
# ── Model singleton ────────────────────────────────────────
_model = None
 
 
def get_model():
    """
    Load IndicConformer model once and cache it.
    First call takes 2-3 minutes (downloading ~2GB).
    Every call after that is instant.
    """
    global _model
    if _model is None:
        print("Loading IndicConformer model... (first time takes 2-3 mins)")
        _model = AutoModel.from_pretrained(
            "ai4bharat/indic-conformer-600m-multilingual",
            trust_remote_code=True
        )
        _model.eval()
        print("Model loaded successfully!")
    return _model
 
 
# ── Audio preprocessing ────────────────────────────────────
 
def preprocess_audio(input_path: str) -> str:
    """
    Convert any audio file to 16kHz mono WAV.
    IndicConformer requires exactly this format.
    Returns path to the converted file.
    """
    output_path = f"/tmp/farmlens_{uuid.uuid4().hex}.wav"
 
    result = subprocess.run([
        "ffmpeg",
        "-i", input_path,
        "-ar", "16000",   # 16kHz sample rate
        "-ac", "1",       # mono (1 channel)
        "-y",             # overwrite if exists
        output_path
    ], capture_output=True, text=True)
 
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg error: {result.stderr}")
 
    return output_path
 
 
# ── Main transcribe function ───────────────────────────────
 
def transcribe(audio_path: str, lang: str = "hi") -> str:
    """
    Convert audio file to text in the specified language.
 
    Args:
        audio_path: Path to audio file (.wav, .mp3, .ogg etc.)
        lang: Language code
              hi = Hindi
              mr = Marathi
              pa = Punjabi
              te = Telugu
              bn = Bengali
              kn = Kannada
 
    Returns:
        Transcribed text as string
    """
    # Step 1: preprocess audio to 16kHz mono WAV
    clean_path = preprocess_audio(audio_path)
 
    try:
        # Step 2: load audio as tensor
        audio_data, sample_rate = sf.read(clean_path)
        wav = torch.FloatTensor(audio_data).unsqueeze(0)
 
        # Step 3: run through model
        model = get_model()
        with torch.no_grad():
            result = model(wav, lang, "ctc")
 
        return result.strip()
 
    finally:
        # Step 4: clean up temp file
        if os.path.exists(clean_path):
            os.remove(clean_path)
 
 
