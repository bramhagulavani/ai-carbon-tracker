import requests
import time
from power_sampler import PowerSampler
from database import init_db, log_query, get_session_stats
OLLAMA_URL = "http://localhost:11434/api/generate"

# Cloud CO₂ estimates per token (grams)
# Based on published data center PUE + grid emission research
CLOUD_CO2_PER_TOKEN = {
    "gpt-4o":        0.0049,   # OpenAI GPT-4o
    "claude-sonnet": 0.0041,   # Anthropic Claude Sonnet
    "gemini-pro":    0.0038,   # Google Gemini Pro
}

def query_ollama(prompt, model="deepseek-r1:1.5b"):
    """Send a prompt to local Ollama and return response + stats"""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return {
            "success": True,
            "response": data.get("response", ""),
            "tokens_generated": data.get("eval_count", 0),
            "tokens_prompt": data.get("prompt_eval_count", 0),
            "ollama_duration_ms": round(data.get("eval_duration", 0) / 1_000_000, 1)
        }
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Ollama not running. Start it first."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def calculate_cloud_co2(tokens, model_name="gpt-4o"):
    """Estimate CO₂ if the same query ran on a cloud model"""
    rate = CLOUD_CO2_PER_TOKEN.get(model_name, 0.0049)
    return round(tokens * rate, 4)


def run_tracked_query(prompt, local_model="deepseek-r1:1.5b"):
    """
    Core function: run a prompt on Ollama while measuring
    GPU power draw the entire time. Return full stats.
    """
    print("\n" + "="*54)
    print(f"  🤖 Model  : {local_model}")
    print(f"  📝 Prompt : {prompt[:50]}{'...' if len(prompt)>50 else ''}")
    print("="*54)

    # ── Start power sampler BEFORE query ──
    sampler = PowerSampler()
    sampler.start()
    wall_start = time.time()

    # ── Run the actual AI query ──
    print("\n  ⏳ Waiting for AI response...\n")
    result = query_ollama(prompt, local_model)

    # ── Stop sampler AFTER query completes ──
    wall_time = round(time.time() - wall_start, 2)
    power_stats = sampler.stop()

    if not result["success"]:
        print(f"  ❌ Error: {result['error']}")
        return None

    # ── Calculate cloud comparison ──
    tokens = result["tokens_generated"]
    cloud_comparisons = {
        name: calculate_cloud_co2(tokens, name)
        for name in CLOUD_CO2_PER_TOKEN
    }
    local_co2 = power_stats["co2_grams_local"]
    best_cloud_co2 = min(cloud_comparisons.values())
    co2_saved = round(best_cloud_co2 - local_co2, 4)

    # ── Print results ──
    print("  ⚡ ENERGY REPORT")
    print(f"  {'Avg GPU power':<22}: {power_stats['avg_watts']} W")
    print(f"  {'Peak GPU power':<22}: {power_stats['peak_watts']} W")
    print(f"  {'Idle power (before)':<22}: ~3.0 W")
    print(f"  {'Energy consumed':<22}: {power_stats['watt_hours']} Wh")
    print(f"  {'CO₂ — local (yours)':<22}: {local_co2} g")
    print()
    print("  ☁️  CLOUD COMPARISON (same query)")
    for cloud_name, co2 in cloud_comparisons.items():
        bar = "█" * int(co2 / 0.05)
        print(f"  {cloud_name:<18}: {co2} g  {bar}")
    local_bar = "█" * max(1, int(local_co2 / 0.05))
    print(f"  {'local (RTX 4050)':<18}: {local_co2} g  {local_bar}")
    print()
    print(f"  💚 CO₂ saved vs cheapest cloud : {co2_saved} g")
    print()
    print("  🧠 AI STATS")
    print(f"  {'Tokens generated':<22}: {tokens}")
    print(f"  {'Prompt tokens':<22}: {result['tokens_prompt']}")
    print(f"  {'Total wall time':<22}: {wall_time}s")
    print(f"  {'Tokens/second':<22}: {round(tokens/wall_time,1) if wall_time>0 else 'N/A'}")
    print()
    print("  🤖 RESPONSE PREVIEW")
    print("  " + "-"*50)
    preview = result["response"][:400].replace("\n", "\n  ")
    print(f"  {preview}...")
    print("="*54 + "\n")

    # ── Return full data for future database logging ──
    query_data = {
        "prompt": prompt,
        "model": local_model,
        "tokens": tokens,
        "tokens_prompt": result["tokens_prompt"],
        "wall_time_s": wall_time,
        "tokens_per_sec": round(tokens / wall_time, 1) if wall_time > 0 else 0,
        "avg_watts": power_stats["avg_watts"],
        "peak_watts": power_stats["peak_watts"],
        "watt_hours": power_stats["watt_hours"],
        "co2_local_g": local_co2,
        "co2_gpt4o_g": cloud_comparisons["gpt-4o"],
        "co2_claude_g": cloud_comparisons["claude-sonnet"],
        "co2_gemini_g": cloud_comparisons["gemini-pro"],
        "co2_saved_g": co2_saved,
        "response": result["response"]
    }

    # ── Auto-save to database ──
    row_id = log_query(query_data)
    print(f"  💾 Saved to database (ID: {row_id})")

    return query_data


# ── RUN 2 PROMPTS SO YOU SEE THE DIFFERENCE ──────────
# REPLACE WITH
if __name__ == "__main__":

    # Make sure DB is ready before anything runs
    init_db()

    queries = [
        "What is artificial intelligence? Answer in 3 sentences.",
        "Write a Python function to check if a number is prime. Explain each line."
    ]

    for prompt in queries:
        run_tracked_query(prompt)
        time.sleep(2)

    # ── Pull lifetime stats straight from DB ──
    stats = get_session_stats()
    print("="*54)
    print("  📊 LIFETIME STATS (all queries ever run)")
    print(f"  {'Total queries':<22}: {stats['total_queries']}")
    print(f"  {'Total tokens':<22}: {stats['total_tokens']}")
    print(f"  {'Total CO₂ local':<22}: {stats['total_co2_local']} g")
    print(f"  {'Total CO₂ saved':<22}: {stats['total_co2_saved']} g")
    print(f"  {'Avg GPU watts':<22}: {stats['avg_watts']} W")
    print(f"  {'Avg tokens/sec':<22}: {stats['avg_tokens_per_sec']}")
    print("="*54)