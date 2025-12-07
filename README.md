# 🎙️ Cinammonroll

A sophisticated voice agent built with [Pipecat](https://github.com/pipecat-ai/pipecat) that can interact with IVR (Interactive Voice Response) systems. The project features real-time speech-to-text, text-to-speech, and an interactive web-based testing environment.

📋 **[View Challenge Tracks](opal-chall.pdf)** - Complete information about the challenge and available tracks.

<img width="1680" height="1490" alt="image" src="https://github.com/user-attachments/assets/bfdd8f65-774f-4a42-98b1-641ebf4aeee0" />


## ✨ Features

- **Voice Interaction**: Real-time voice conversation using Deepgram STT and Cartesia TTS
- **IVR Navigation**: Intelligent navigation of phone menu systems using tool-based digit pressing
- **Web-Based Gym Interface**: Visual debugging interface to observe agent interactions
- **Barge-in Support**: Configurable interruption handling (allows users to interrupt the agent)
- **Silent Mode**: Text-only mode for testing without audio output
- **Security Features**: Built-in protection against prompt injection and social engineering
- **Low Latency**: Optimized pipeline for responsive voice interactions
- **WebRTC VAD**: Voice Activity Detection for accurate speech segmentation

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Audio input/output devices (microphone and speakers)
- API keys for:
  - [Deepgram](https://deepgram.com/) (Speech-to-Text)
  - [Groq](https://groq.com/) (LLM)
  - [Cartesia](https://cartesia.ai/) (Text-to-Speech)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/AdalricP/cinammonroll.git
cd cinammonroll
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your API keys:
```env
DEEPGRAM_API_KEY=your_deepgram_api_key
GROQ_API_KEY=your_groq_api_key
CARTESIA_API_KEY=your_cartesia_api_key
```

### Basic Usage

**Run the agent with web interface:**
```bash
python gym_runner.py
```
This will:
- Start the Gym Server on http://localhost:8000
- Open your browser automatically
- Launch the voice agent

**Run the agent standalone:**
```bash
python main.py
```

**Available command-line options:**
```bash
python main.py --verbose      # Enable detailed debug logging
python main.py --mute         # Run in silent mode (no TTS output)
python main.py --no-cut       # Disable barge-in (agent completes responses)
```

## 🏗️ Project Structure

```
cinammonroll/
├── main.py                    # Standalone agent entry point
├── gym_runner.py              # Agent + Web interface launcher
├── requirements.txt           # Python dependencies
└── src/
    ├── agent/                 # Voice agent implementation
    │   ├── factory.py         # Agent pipeline configuration
    │   ├── voice/             # Voice processing components
    │   │   ├── transport.py   # Audio I/O handling
    │   │   ├── vad.py         # Voice Activity Detection
    │   │   └── aec.py         # Acoustic Echo Cancellation
    │   ├── tools/             # Agent tools
    │   │   └── ivr.py         # IVR interaction tools
    │   └── security/          # Security components
    │       └── pressure_guard.py
    ├── gym/                   # Web-based testing interface
    │   ├── server.py          # Flask/Socket.IO server
    │   └── static/            # Web UI assets
    ├── legacy/                # Legacy implementations
    ├── scripts/               # Utility scripts
    └── tests/                 # Test files
```

## 🔧 Configuration

### Agent Configuration

The agent can be configured through parameters in `main.py`:

- **Model**: Default is `"openai/gpt-oss-120b"` (via Groq)
- **Voice ID**: Cartesia voice ID for TTS
- **VAD Aggressiveness**: Adjustable in `factory.py` (0-3, default: 1)

### Environment Variables

Required environment variables in `.env`:
- `DEEPGRAM_API_KEY`: For speech-to-text service
- `GROQ_API_KEY`: For LLM inference
- `CARTESIA_API_KEY`: For text-to-speech service

## 🎯 How It Works

1. **Audio Input**: User speaks into microphone
2. **STT**: Deepgram converts speech to text
3. **VAD**: Voice Activity Detection determines when user stops speaking
4. **LLM**: Groq processes the text and decides on actions
5. **Tools**: Agent can use tools like `press_digit` to interact with IVR
6. **TTS**: Cartesia converts response to speech
7. **Audio Output**: Response is played through speakers

The agent uses a sophisticated pipeline architecture provided by Pipecat, enabling real-time processing with minimal latency.

## 🔐 Security Features

The agent includes security measures against:
- **Prompt Injection**: Input sanitization and security protocols
- **Social Engineering**: Resistance to authority impersonation
- **Untrusted Input Handling**: All user input is treated as potentially hostile

Security rules are defined in the system prompt and enforced at runtime.

## 🧪 Testing

The Gym interface provides a visual way to test agent interactions:
- View real-time transcripts
- See IVR button presses
- Monitor agent behavior
- Test various scenarios

Run tests with:
```bash
python -m pytest src/tests/
```

## 📦 Key Dependencies

- **pipecat-ai**: Framework for building voice agents
- **deepgram-sdk**: Speech-to-text service
- **groq**: Fast LLM inference
- **cartesia**: High-quality text-to-speech
- **Flask/Socket.IO**: Web interface backend
- **webrtcvad**: Voice Activity Detection
- **PyAudio**: Audio I/O handling

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is available for use and modification. Please check with the repository owner for specific licensing terms.

## 🙏 Acknowledgments

Built with [Pipecat](https://github.com/pipecat-ai/pipecat) - A framework for building voice and multimodal AI applications.
