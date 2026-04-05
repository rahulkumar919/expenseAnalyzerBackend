from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Simple test working!"})

@app.route('/test')
def test():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("Starting simple Flask app...")
    app.run(host='0.0.0.0', port=5001, debug=True)
