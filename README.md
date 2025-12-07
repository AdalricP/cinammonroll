# Cinammonroll

A voice agent built with [Pipecat](https://github.com/pipecat-ai/pipecat) that can interact with IVR (Interactive Voice Response) systems.

<img width="1680" height="1490" alt="image" src="https://github.com/user-attachments/assets/bfdd8f65-774f-4a42-98b1-641ebf4aeee0" />

## Quick Start

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

3. Create a `.env` file with your API keys:
```env
DEEPGRAM_API_KEY=your_deepgram_api_key
GROQ_API_KEY=your_groq_api_key
CARTESIA_API_KEY=your_cartesia_api_key
```

### Usage

Run the agent with web interface:
```bash
python gym_runner.py
```

Run the agent standalone:
```bash
python main.py
```

Available command-line options:
```bash
python main.py --verbose      # Enable detailed debug logging
python main.py --mute         # Run in silent mode (no TTS output)
python main.py --no-cut       # Disable barge-in (agent completes responses)
```

---

Built with [Pipecat](https://github.com/pipecat-ai/pipecat)
