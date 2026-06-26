# ⚡ AI Carbon Footprint Tracker

> Measures and compares the **real energy cost** of running AI models locally (Ollama + RTX 4050) versus cloud APIs (GPT-4o, Claude, Gemini) — with a live D3.js dashboard.

Built by **Bramha Vinayak Gulavani** — CSE (AI & ML), VIT Pune.

---

## 🌍 Why this exists

Every time you send a prompt to ChatGPT or Claude, a data center somewhere burns electricity and emits CO₂. Nobody tells you how much. Training GPT-3 alone emitted **626,000 kg of CO₂** — and inference (daily use) now dwarfs that at scale.

Local models running on consumer GPUs are the green alternative — but nobody had built a tool to actually **measure, compare, and visualize** that gap in real time.

This project does exactly that.

---

## 📸 Dashboard

![AI Carbon Footprint Tracker Dashboard](dashboard_preview.png)

**Live stats shown:**
- Total queries run, tokens generated, CO₂ produced
- CO₂ saved vs cloud (GPT-4o, Claude, Gemini) — per query and lifetime
- Avg GPU power draw (watts) and tokens/second
- Real-time grouped bar chart — local vs cloud per query
- Donut chart — CO₂ breakdown of the latest query
- Full query history table with timestamps
- Live query runner — type any prompt, hit Run, see results

---

## 🔬 How it works

When you run a prompt, two things happen simultaneously:

```
You type a prompt
       │
       ├──► Ollama runs AI model on RTX 4050 GPU
       │         (DeepSeek / Llama / Mistral)
       │
       └──► Power Sampler reads nvidia-smi every 500ms
                 (GPU watts, temperature, utilization)
                         │
                         ▼
              CO₂ Calculator
              watt-hours × 0.82 = grams CO₂ (India grid factor)
              tokens × cloud rate = grams CO₂ (cloud estimate)
                         │
                         ▼
              SQLite Logger + Flask API + D3.js Dashboard
```

### The core formula

```python
# Energy consumed during query
watt_hours = avg_watts × duration_seconds / 3600

# Local CO₂ (India grid emission factor)
co2_local = watt_hours × 0.82   # grams

# Cloud CO₂ estimate (per token, based on PUE research)
co2_cloud = tokens × 0.0049     # grams (GPT-4o)

# CO₂ saved by running locally
co2_saved = co2_cloud - co2_local
```

---

## 📊 Real results (from my RTX 4050)

| Query type | Avg GPU | Tokens | CO₂ local | CO₂ GPT-4o | Saved |
|---|---|---|---|---|---|
| Simple question (3 sentences) | 23W | 326 | 0.055g | 1.597g | **1.184g** |
| Complex coding question | 55W | 1,980 | 0.205g | 9.702g | **7.319g** |

> **Local AI is ~47× cleaner than cloud AI** for the same output.

---

## 🛠️ Tech stack

| Layer | Technology |
|---|---|
| AI inference | Ollama (DeepSeek R1, Llama 3, Mistral) |
| Power measurement | `nvidia-smi` + `psutil` |
| Backend API | Python 3.14 · Flask · Flask-CORS |
| Database | SQLite · SQLAlchemy |
| Frontend | D3.js v7 · HTML/CSS |
| Hardware | NVIDIA GeForce RTX 4050 (6GB VRAM) |

---

## 🚀 Setup & installation

### Prerequisites
- Windows 11 / Linux / macOS
- NVIDIA GPU with drivers installed
- [Ollama](https://ollama.com/download) installed
- Python 3.11+

### 1. Clone the repo

```bash
git clone https://github.com/bramhagulavani/ai-carbon-tracker.git
cd ai-carbon-tracker
```

### 2. Install dependencies

```bash
pip install flask flask-cors requests
```

### 3. Pull an AI model

```bash
ollama pull deepseek-r1:1.5b
```

### 4. Start the Flask API

```bash
python app.py
```

### 5. Open the dashboard

Open `dashboard.html` in your browser. That's it — no build tools, no npm, no config.

---

## 📁 Project structure

```
carbon-tracker/
│
├── power_sampler.py      # Reads GPU watts via nvidia-smi every 500ms
├── ollama_query.py       # Runs Ollama inference + power tracking
├── database.py           # SQLite logger — stores every query
├── app.py                # Flask API — /query /history /stats
├── dashboard.html        # Live D3.js dashboard (single file)
│
├── carbon_tracker.db     # SQLite database (auto-created)
└── README.md
```

---

## 🌐 API endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API status + available routes |
| POST | `/query` | Run a prompt, returns full energy report |
| GET | `/stats` | Lifetime summary stats |
| GET | `/history` | All queries logged, most recent first |

### Example: POST /query

```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain neural networks", "model": "deepseek-r1:1.5b"}'
```

**Response:**
```json
{
  "model": "deepseek-r1:1.5b",
  "tokens": 361,
  "avg_watts": 23.06,
  "watt_hours": 0.032,
  "co2_local_g": 0.026,
  "co2_gpt4o_g": 1.769,
  "co2_saved_g": 1.345,
  "wall_time_s": 5.69,
  "tokens_per_sec": 63.4
}
```

---

## 🗺️ Roadmap

- [x] GPU power sampler (nvidia-smi)
- [x] CO₂ calculator with India grid factor
- [x] Ollama integration (DeepSeek, Llama, Mistral)
- [x] SQLite query logger
- [x] Flask REST API
- [x] Live D3.js dashboard
- [ ] Multi-model benchmark mode (same prompt → all models → ranked leaderboard)
- [ ] Server-Sent Events (SSE) for live wattage graph during inference
- [ ] PDF report export (monthly energy summary)
- [ ] CPU-only mode (for systems without NVIDIA GPU)
- [ ] Deployment guide (Render / Railway)

---

## 📚 Research context

This project contributes real measurement data to the emerging field of **AI sustainability**. Key references:

- Strubell et al. (2019) — *Energy and Policy Considerations for Deep Learning in NLP*
- Patterson et al. (2021) — *Carbon Emissions and Large Neural Network Training* (Google)
- India grid emission factor: **0.82 kg CO₂/kWh** (CEA, Ministry of Power, 2023)
- Cloud PUE assumptions: 1.58 average (Uptime Institute Global Data Center Survey 2023)

---

## 👤 Author

**Bramha Vinayak Gulavani**
- 🎓 CSE (AI & ML) · VIT Pune 
- 💼 [LinkedIn](https://www.linkedin.com/in/bramha-vinayak-gulavani-31302a30b/)
- 🌐 [Portfolio](https://bramhagulavani.vercel.app)
- 🐙 [GitHub](https://github.com/bramhagulavani)

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

<p align="center">
  <i>Built with an RTX 4050, Ollama, and the belief that AI should be measurably sustainable.</i>
</p>