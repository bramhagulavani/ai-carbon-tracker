from flask import Flask, request, jsonify
from flask_cors import CORS
from ollama_query import run_tracked_query
from database import init_db, get_all_queries, get_session_stats

app = Flask(__name__)
CORS(app)  # allows the dashboard (browser) to call this API

# Make sure DB exists when server starts
init_db()


@app.route("/")
def home():
    return jsonify({
        "status": "running",
        "service": "AI Carbon Footprint Tracker API",
        "endpoints": ["/query (POST)", "/history (GET)", "/stats (GET)"]
    })


@app.route("/query", methods=["POST"])
def query():
    """
    Send a prompt, get back the full energy + CO2 + response report.
    Body: { "prompt": "...", "model": "deepseek-r1:1.5b" }
    """
    body = request.get_json()

    if not body or "prompt" not in body:
        return jsonify({"error": "Missing 'prompt' in request body"}), 400

    prompt = body["prompt"]
    model = body.get("model", "deepseek-r1:1.5b")

    result = run_tracked_query(prompt, local_model=model)

    if result is None:
        return jsonify({"error": "Ollama query failed. Is Ollama running?"}), 500

    return jsonify(result)


@app.route("/history", methods=["GET"])
def history():
    """Returns every query ever logged, most recent first"""
    rows = get_all_queries()
    return jsonify({"count": len(rows), "queries": rows})


@app.route("/stats", methods=["GET"])
def stats():
    """Returns lifetime summary stats — for dashboard top cards"""
    data = get_session_stats()
    return jsonify(data)


if __name__ == "__main__":
    print("\n🚀 Carbon Tracker API starting...")
    print("   → http://localhost:5000\n")
    app.run(debug=True, port=5000)