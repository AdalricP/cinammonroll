# 🎙️ Cinammonroll

A voice agent built with [Pipecat](https://github.com/pipecat-ai/pipecat) that can interact with IVR systems.

## Quick Start

### Prerequisites

- Python 3.8+
- API keys for [Deepgram](https://deepgram.com/), [Groq](https://groq.com/), and [Cartesia](https://cartesia.ai/)

### Installation

1. Clone and install:
```bash
git clone https://github.com/AdalricP/cinammonroll.git
cd cinammonroll
pip install -r requirements.txt
```

2. Create a `.env` file with your API keys:
```env
DEEPGRAM_API_KEY=your_deepgram_api_key
GROQ_API_KEY=your_groq_api_key
CARTESIA_API_KEY=your_cartesia_api_key
```

### Usage

Run with web interface:
```bash
python gym_runner.py
```

Run standalone:
```bash
python main.py
```

---

Built with [Pipecat](https://github.com/pipecat-ai/pipecat)
