from flask import Flask, jsonify
import os
import redis

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
app = Flask(__name__)

@app.route("/results")
def results():
    counts = {opt: int(r.hget("votes", opt) or 0) for opt in ["Cats", "Dogs"]}
    return jsonify(counts)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
