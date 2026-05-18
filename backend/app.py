# app.py

# ===================
# Imports
# ===================
from cv2 import videoio_registry
from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
from pathlib import Path
import tempfile
import uuid
import os
import analyzer


# ===================
# Set up
# ===================
app = Flask(__name__)
CORS(app)

# ===================
# Endpoints
# ===================
@app.route('/api/analyze', methods=['POST'])
def analyze():

    file = request.files.get('video')
    if file is None:
        abort(400, description='No se ha enviado ningún video.')

    if not file.filename:
        abort(400, description='El fichero no tiene nombre.')

    suffix   = Path(file.filename).suffix.lower()
    tmp_path = Path(tempfile.gettempdir()) / f'{uuid.uuid4().hex}{suffix}'
    file.save(tmp_path)

    try:
        result = analyzer.analyze(tmp_path)
        return jsonify(result)
    except ValueError as e:
        abort(400, description=str(e))
    except Exception:
        abort(500, description='Error interno del Servidor.')
    finally:
        if tmp_path.exists():
            os.remove(tmp_path)


@app.route('/api/video/<filename>')
def serve_video(filename):
    video_path = Path(tempfile.gettempdir()) / filename
    if not video_path.exists():
        abort(404)
    return send_file(video_path, mimetype='video/mp4')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
