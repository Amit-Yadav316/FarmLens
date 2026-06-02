"""
Day 2 test script — run this to verify ASR works
Usage: python tests/test_asr.py
"""
from gtts import gTTS
import os


def generate_test_audio(text: str, lang: str, filename: str):
    """Generate a test audio file using gTTS"""
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    print(f"Generated test audio: {filename}")


def test_hindi_transcription():
    from backend.asr.transcriber import transcribe

    # Generate test audio
    test_file = "tests/sample_audio/hi_test.mp3"
    os.makedirs("tests/sample_audio", exist_ok=True)
    generate_test_audio("आज गेहूं का भाव क्या है", "hi", test_file)

    # Transcribe
    print("Transcribing Hindi audio...")
    result = transcribe(test_file, lang="hi")
    print(f"Hindi result: {result}")
    assert result, "Transcription returned empty string"
    print("Hindi test PASSED")


def test_model_loads():
    from backend.asr.transcriber import get_model
    print("Loading model (takes 2-3 mins first time)...")
    model = get_model()
    assert model is not None
    print("Model load test PASSED")


if __name__ == "__main__":
    print("=" * 40)
    print("FarmLens ASR Tests")
    print("=" * 40)
    test_model_loads()
    test_hindi_transcription()
    print("\nAll tests passed!")