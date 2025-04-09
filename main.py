import sounddevice as sd
import numpy as np
import requests
from faster_whisper import WhisperModel
import sys
from TTS.api import TTS
import json
import threading
import queue
import time
import re

# Test available input devices
print("Available input devices:")
print(sd.query_devices())

# Initialize components
model = WhisperModel("tiny")
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)

# Global variables for speech control
speech_queue = queue.Queue()
is_speaking = False
stop_speaking = False
interrupt_threshold = 0.01  # Adjust this value to change sensitivity

def search_web(query):
    try:
        # Using DuckDuckGo API for web search
        response = requests.get(
            'https://api.duckduckgo.com/',
            params={
                'q': query,
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1
            }
        )
        data = response.json()
        
        # Extract relevant information
        abstract = data.get('Abstract', '')
        related_topics = [topic.get('Text', '') for topic in data.get('RelatedTopics', [])[:3]]
        
        return {
            'abstract': abstract,
            'related_topics': related_topics
        }
    except Exception as e:
        print(f"Error in web search: {e}")
        return None

def should_search_web(text):
    # Keywords that indicate need for current information
    search_keywords = [
        'what is', 'who is', 'when', 'where', 'how', 'latest', 'current',
        'news', 'weather', 'time', 'date', 'price', 'stock', 'market',
        'search', 'find', 'look up', 'tell me about'
    ]
    
    return any(keyword in text.lower() for keyword in search_keywords)

def speak(text):
    global is_speaking, stop_speaking
    try:
        if stop_speaking:
            stop_speaking = False
            return
            
        is_speaking = True
        # Generate audio
        audio = tts.tts(text)
        # Play the audio using sounddevice
        sd.play(audio, tts.synthesizer.output_sample_rate)
        sd.wait()
        is_speaking = False
    except Exception as e:
        print(f"Error in speech: {e}")
        is_speaking = False

def stop_current_speech():
    global stop_speaking
    stop_speaking = True
    sd.stop()
    time.sleep(0.1)  # Small delay to ensure audio stops

def check_for_interrupt():
    global is_speaking, stop_speaking
    while is_speaking:
        try:
            # Record a very short sample to check for user input
            audio = sd.rec(int(0.1 * 16000), samplerate=16000, channels=1)
            sd.wait()
            
            if np.max(np.abs(audio)) > interrupt_threshold:
                print("User started speaking, stopping current response...")
                stop_current_speech()
                return True
                
        except Exception as e:
            print(f"Error checking for interrupt: {e}")
            return False
    return False

def transcribe_audio(audio, samplerate):
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

def stream_mistral_response(prompt):
    try:
        # Check if we need to search the web
        web_info = None
        if should_search_web(prompt):
            print("Searching the web for relevant information...")
            web_info = search_web(prompt)
            
            if web_info:
                # Construct a prompt that includes web search results
                context = f"Based on the following web search results:\n"
                if web_info['abstract']:
                    context += f"Main information: {web_info['abstract']}\n"
                if web_info['related_topics']:
                    context += f"Related information: {' '.join(web_info['related_topics'])}\n"
                context += f"\nNow, please answer this question: {prompt}"
                prompt = context

        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'mistral',
                'prompt': prompt,
                'stream': True,
                'options': {
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'max_tokens': 500
                }
            },
            stream=True
        )
        response.raise_for_status()
        
        current_sentence = ""
        full_response = ""
        
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if 'response' in data:
                        chunk = data['response']
                        full_response += chunk
                        current_sentence += chunk
                        
                        # Check if we have a complete sentence
                        if any(current_sentence.endswith(end) for end in ['.', '!', '?', ':', ';']):
                            print(f"Assistant: {current_sentence}")
                            speak(current_sentence)
                            # Check for interruption after each sentence
                            if check_for_interrupt():
                                return full_response
                            current_sentence = ""
                            
                except json.JSONDecodeError:
                    continue
                    
        # Speak any remaining text
        if current_sentence:
            print(f"Assistant: {current_sentence}")
            speak(current_sentence)
            
        return full_response
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Mistral: {e}")
        error_msg = "I apologize, but I'm having trouble connecting to my brain right now. Could you try again?"
        print(f"Assistant: {error_msg}")
        speak(error_msg)
        return error_msg
    except Exception as e:
        print(f"Unexpected error with Mistral: {e}")
        error_msg = "I encountered an unexpected error. Could you rephrase that?"
        print(f"Assistant: {error_msg}")
        speak(error_msg)
        return error_msg

def is_wake_word(text):
    wake_words = ["hey mistral", "hi mistral", "hello mistral", "mistral","arise"]
    return any(word in text.lower() for word in wake_words)

def main_loop():
    print("🎙️ Voice Assistant Ready!")
    print("Say 'Hey Mistral' to start, or 'exit' to quit")
    speak("Hello! I'm your voice assistant. Say 'Hey Mistral' to start, or 'exit' to quit.")
    
    duration = 5  # seconds of listening per chunk
    is_active = False

    while True:
        try:
            audio = sd.rec(int(duration * 16000), samplerate=16000, channels=1)
            sd.wait()
            
            if np.max(np.abs(audio)) < interrupt_threshold:
                continue
                
            text = transcribe_audio(audio, 16000)
            
            if not text.strip():
                continue
                
            print(f"You said: {text}")
            
            if "exit" in text.lower():
                speak("Goodbye! Have a great day!")
                sys.exit(0)
                
            if not is_active and is_wake_word(text):
                is_active = True
                speak("Yes, I'm listening. How can I help you?")
                continue
                
            if is_active:
                stream_mistral_response(text)
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"Error in main loop: {e}")
            speak("I encountered an error. Please try again.")
            is_active = False

if __name__ == "__main__":
    main_loop()