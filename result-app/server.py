from flask import Flask, render_template, jsonify
import os
import redis

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

app = Flask(__name__, static_folder='static', template_folder='templates')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/results')
def results():
    try:
        counts = client.hgetall('votes') or {}
        # Ensure keys exist
        cats = int(counts.get('Cats', 0))
        dogs = int(counts.get('Dogs', 0))
        return jsonify({'Cats': cats, 'Dogs': dogs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
