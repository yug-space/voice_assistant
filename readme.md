# Voice Assistant with Mistral AI

A powerful voice assistant that uses Mistral AI for natural language processing, Whisper for speech recognition, and text-to-speech capabilities. The assistant can understand voice commands, search the web, and provide natural conversational responses.

## Features

- 🎙️ Voice activation with wake word detection ("Hey Mistral")
- 🗣️ Natural speech recognition using Whisper
- 🤖 AI-powered responses using Mistral
- 🌐 Web search integration for real-time information
- 🔊 High-quality text-to-speech synthesis
- ⚡ Interrupt capability during responses
- 🎯 Context-aware conversations

## Prerequisites

- Python 3.8 or higher
- Mistral AI running locally (via Ollama)
- Audio input device (microphone)
- Audio output device (speakers)

## Installation

1. Clone this repository:
```bash
git clone [your-repository-url]
cd voice_assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Make sure you have Ollama installed and the Mistral model running locally:
```bash
ollama run mistral
```

## Usage

1. Activate your virtual environment if not already activated:
```bash
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

2. Run the voice assistant:
```bash
python main.py
```

3. Wake up the assistant by saying "Hey Mistral" or any of the following wake words:
   - "Hi Mistral"
   - "Hello Mistral"
   - "Mistral"
   - "Arise"

4. Ask your question or give a command after the assistant acknowledges you

5. To exit, simply say "exit" or press Ctrl+C

## Key Components

- `main.py`: Core application logic and voice assistant implementation
- `stt.py`: Speech-to-text functionality
- `requirements.txt`: Project dependencies

## Features in Detail

### Voice Activation
The assistant listens for wake words and becomes active only when called upon, preserving system resources and privacy.

### Intelligent Responses
- Uses Mistral AI for generating contextual and intelligent responses
- Integrates web search capabilities for real-time information
- Streams responses sentence by sentence for natural conversation flow

### Interruption Handling
- Users can interrupt the assistant's response by speaking
- Smart detection of user input during response playback
- Graceful handling of interruptions and conversation flow

### Web Search Integration
- Automatic detection of queries requiring current information
- Integration with DuckDuckGo for web searches
- Contextual responses incorporating web search results

## Dependencies

- sounddevice==0.4.6: Audio input/output handling
- numpy==1.22.0: Numerical operations and audio processing
- requests==2.31.0: HTTP requests for web integration
- faster-whisper==0.10.0: Speech recognition
- TTS==0.22.0: Text-to-speech synthesis

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Your chosen license]

## Acknowledgments

- Mistral AI for the language model
- Whisper for speech recognition
- Mozilla TTS for speech synthesis
- DuckDuckGo for web search capabilities
