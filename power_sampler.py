import subprocess
import time
import threading

def get_gpu_watts():
    """Read current GPU power draw using nvidia-smi"""
    result = subprocess.run(
        ["nvidia-smi", 
         "--query-gpu=power.draw,temperature.gpu,utilization.gpu",
         "--format=csv,noheader,nounits"],
        capture_output=True, text=True
    )
    parts = result.stdout.strip().split(", ")
    return {
        "watts": float(parts[0]),
        "temp_c": float(parts[1]),
        "gpu_util": float(parts[2])
    }

class PowerSampler:
    """Runs in background, records GPU watts every 500ms"""
    def __init__(self):
        self.readings = []
        self.running = False

    def start(self):
        self.readings = []
        self.running = True
        self._thread = threading.Thread(target=self._sample_loop)
        self._thread.start()
        print("⚡ Power sampler started...")

    def _sample_loop(self):
        while self.running:
            reading = get_gpu_watts()
            self.readings.append(reading)
            time.sleep(0.5)

    def stop(self):
        self.running = False
        self._thread.join()
        return self._calculate_stats()

    def _calculate_stats(self):
        if not self.readings:
            return {}
        watts_list = [r["watts"] for r in self.readings]
        duration_secs = len(self.readings) * 0.5
        avg_watts = sum(watts_list) / len(watts_list)
        watt_hours = (avg_watts * duration_secs) / 3600

        # India grid emission factor: 0.82 kg CO2 per kWh
        co2_grams = watt_hours * 0.82

        return {
            "duration_secs": round(duration_secs, 1),
            "avg_watts": round(avg_watts, 2),
            "peak_watts": round(max(watts_list), 2),
            "watt_hours": round(watt_hours, 6),
            "co2_grams_local": round(co2_grams, 4),
            "readings_count": len(self.readings)
        }


# ── TEST IT ──────────────────────────────────────────
if __name__ == "__main__":
    print("Reading live GPU stats...\n")

    # Single reading test
    data = get_gpu_watts()
    print(f"Right now → {data['watts']}W  |  {data['temp_c']}°C  |  {data['gpu_util']}% GPU util")

    print("\nStarting 5-second power recording...\n")
    sampler = PowerSampler()
    sampler.start()

    # Simulate a 5-second "AI query"
    time.sleep(5)

    stats = sampler.stop()
    print("\n📊 Results:")
    print(f"  Duration     : {stats['duration_secs']} seconds")
    print(f"  Avg power    : {stats['avg_watts']} W")
    print(f"  Peak power   : {stats['peak_watts']} W")
    print(f"  Energy used  : {stats['watt_hours']} Wh")
    print(f"  CO₂ produced : {stats['co2_grams_local']} grams")
    print(f"  Samples taken: {stats['readings_count']}")