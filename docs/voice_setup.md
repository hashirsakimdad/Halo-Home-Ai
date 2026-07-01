# Voice Setup

Voice mode uses:

- Whisper for STT
- pyttsx3 for TTS
- Vosk for wake word

## Install (when ready)

```powershell
pip install openai-whisper sounddevice soundfile scipy numpy pyttsx3 vosk pyaudio
```

Then run:

```powershell
python main.py --mode voice
```

