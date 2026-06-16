# app.py

# ===================
# Imports
# ===================
from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
from pathlib import Path
import tempfile
import uuid
import os
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
import analyzer

# ===================
# Firebase Admin SDK
# ===================
_cred = credentials.Certificate(
    Path(__file__).parent / 'tennis-tfg-37c99-firebase-adminsdk-fbsvc-9253d4cb2c.json'
)
firebase_admin.initialize_app(_cred)


def get_uid() -> str:
    """
    Extrae y verifica el token Firebase del header Authorization.
    Devuelve el uid del usuario o aborta con 401.
    """
    header = request.headers.get('Authorization', '')
    if not header.startswith('Bearer '):
        abort(401, description='Token no proporcionado.')
    token = header.split(' ', 1)[1]
    try:
        decoded = firebase_auth.verify_id_token(token)
        return decoded['uid']
    except Exception:
        abort(401, description='Token inválido o expirado.')


# ===================
# Set up
# ===================
app = Flask(__name__)
CORS(app)

@app.errorhandler(Exception)
def handle_error(e):
    from werkzeug.exceptions import HTTPException
    if isinstance(e, HTTPException):
        return jsonify(description=e.description), e.code
    return jsonify(description='Error interno del servidor.'), 500


# ===================
# Endpoints
# ===================
@app.route('/api/analyze', methods=['POST'])
def analyze():
    uid = get_uid()

    file = request.files.get('video')
    if file is None:
        abort(400, description='No se ha enviado ningún video.')

    if not file.filename:
        abort(400, description='El fichero no tiene nombre.')

    suffix   = Path(file.filename).suffix.lower()
    tmp_path = Path(tempfile.gettempdir()) / f'{uuid.uuid4().hex}{suffix}'
    file.save(tmp_path)

    try:
        nivel = int(request.form.get('nivel', 5))
        nivel = max(1, min(5, nivel))
        result = analyzer.analyze(tmp_path, nivel=nivel)
        result['uid'] = uid
        return jsonify(result)
    except ValueError as e:
        abort(400, description=str(e))
    except Exception:
        abort(500, description='Error interno del servidor.')
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
