import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
from pynput import keyboard
import pyperclip
import threading

# Initialize the Whisper model
model = WhisperModel("tiny")

# Global variables
is_listening = False
interrupt_threshold = 0.01

def transcribe_audio(audio):
    # Convert to mono if stereo
    if len(audio.shape) > 1:
        audio = audio.mean(axis=1)
    
    # Normalize audio to float32 in range [-1, 1]
    audio = audio.astype(np.float32)
    if np.max(np.abs(audio)) > 1.0:
        audio = audio / np.max(np.abs(audio))
    
    print("Transcribing audio...")
    segments, _ = model.transcribe(audio, language='en', beam_size=5)
    text = " ".join([seg.text for seg in segments])
    print("Transcription:", text)
    return text

def on_activate():
    global is_listening
    
    print("🎙️ Listening...")
    is_listening = True
    
    # Record audio for 5 seconds
    duration = 5
    audio = sd.rec(int(duration * 16000), samplerate=16000, channels=1)
    sd.wait()
    
    if np.max(np.abs(audio)) > interrupt_threshold:
        text = transcribe_audio(audio)
        if text.strip():
            pyperclip.copy(text)  # Copy to clipboard
            print("Text copied to clipboard!")
    
    is_listening = False

def for_canonical(f):
    return lambda k: f(listener.canonical(k))

def on_hotkey():
    if not is_listening:
        threading.Thread(target=on_activate).start()

# Setup the hotkey listener
hotkey = keyboard.HotKey(
    keyboard.HotKey.parse('<cmd>+r'),  # Using cmd+r as Fn might not be directly detectable
    on_hotkey
)

with keyboard.Listener(on_press=for_canonical(hotkey.press),
                      on_release=for_canonical(hotkey.release)) as listener:
    print("Press Cmd+R to start voice recognition...")
    listener.join()
