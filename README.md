# ⚡ AI Carbon Footprint Tracker

Measures and compares the real energy cost of running AI models
locally (Ollama) vs cloud APIs (GPT-4o, Claude).

Built by **Bramha Vinayak Gulavani** — CS (AI/ML), VIT Pune.

## What it does
- Reads GPU wattage live using nvidia-smi during LLM inference
- Converts energy → grams of CO₂ using India's grid factor
- Compares local inference cost vs equivalent cloud API cost
- Visualizes results on a real-time D3.js dashboard

## Tech Stack
Python · Flask · Ollama · nvidia-smi · D3.js · SQLite

## Setup
```bash
git clone https://github.com/bramhagulavani/ai-carbon-tracker
cd ai-carbon-tracker
pip install -r requirements.txt
python power_sampler.py
```

## Status
🚧 Active development