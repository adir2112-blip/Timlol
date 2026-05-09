from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import subprocess
import tempfile
import os
import uuid

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return jsonify({"status": "ok", "service": "WMV Converter"})

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400
    
    file = request.files['file']
    ext = file.filename.rsplit('.', 1)[-1].lower()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, f"input.{ext}")
        output_path = os.path.join(tmpdir, "output.mp3")
        
        file.save(input_path)
        
        cmd = [
            'ffmpeg', '-i', input_path,
            '-vn', '-ar', '16000', '-ac', '1', '-ab', '64k',
            '-y', output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        
        if result.returncode != 0 or not os.path.exists(output_path):
            return jsonify({"error": result.stderr.decode('utf-8', errors='ignore')[-300:]}), 500
        
        return send_file(output_path, mimetype='audio/mpeg',
                        as_attachment=True,
                        download_name=file.filename.rsplit('.', 1)[0] + '.mp3')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
