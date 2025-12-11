from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import redis

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

VOTES_KEY = "votes"
OPTIONS = ["Cats", "Dogs"]

# ensure keys exist
for opt in OPTIONS:
    if r.hget(VOTES_KEY, opt) is None:
        r.hset(VOTES_KEY, opt, 0)

app = Flask(__name__)

@app.route("/")
def index():
    counts = {opt: int(r.hget(VOTES_KEY, opt) or 0) for opt in OPTIONS}
    return render_template("index.html", options=OPTIONS, counts=counts)

@app.route("/vote", methods=["POST"])
def vote():
    choice = request.form.get("choice") or request.json.get("choice")
    if choice not in OPTIONS:
        return jsonify({"error": "invalid choice"}), 400
    r.hincrby(VOTES_KEY, choice, 1)
    return jsonify({"ok": True})

@app.route("/results")
def results():
    counts = {opt: int(r.hget(VOTES_KEY, opt) or 0) for opt in OPTIONS}
    return jsonify(counts)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
