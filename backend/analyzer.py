# analyzer.py

# ===================
# Imports 
# ===================
import sys
import uuid
import shutil
import tempfile
from pathlib import Path
import pandas as pd 
import numpy as np 
import joblib 
import ffmpeg 

# ===================
# Setup paths
# ===================

# With this we get the TFG root
TFG_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(TFG_DIR / 'video_process_2'))
sys.path.append(str(TFG_DIR / 'metrics_process_3'))
sys.path.append(str(TFG_DIR / 'test_process_5'))

from video_processor import process_video, mask_low_visibility, cleaning_data, create_output_video
from features_extractor import (
    calculate_knee_frames,
    get_hip_width,
    calculate_stance_metrics,
    calculate_effect_metrics,
    get_non_dominant_arm_angle,
    get_hip_drive,
    get_shoulder_rotation,
    get_trunk_arch,
)
from quality_checks import validate_knee_integrity
from feedback_classifier import classify_serve

# ================================
# CONSTANTS AND MODELS LOAD
# ================================
ACCEPTED_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.3gp', '.m4v', '.wmv', '.mpeg', '.mpg'}

STANCE_FEATURES = [
    'knee_start', 'knee_min', 'knee_target',
    'ankle_drag', 'ankle_min_dist', 'hip_tilt',
]
EFFECT_FEATURES = [
    'jump', 'lateral_offset', 'arm_extension',
    'non_dominant_arm_angle', 'hip_drive',
]

STANCE_MAP = {0: 'Pinpoint', 1: 'Platform'}
EFFECT_MAP = {0: 'Flat', 1: 'Kick', 2: 'Slice'}

MODELS_DIR = TFG_DIR / 'model_ai_process_4'

_model_stance = joblib.load(MODELS_DIR / 'model_stance.pkl')
_scaler_stance = joblib.load(MODELS_DIR / 'scaler_stance.pkl')
_model_effect = joblib.load(MODELS_DIR / 'model_effect.pkl')
_scaler_effect = joblib.load(MODELS_DIR / 'scaler_effect.pkl')


# ================================
# FUNCTIONS
# ================================

def _convert_to_mp4(input_path: Path, output_path: Path):
    (
        ffmpeg
        .input(str(input_path))
        .output(str(output_path), vcodec='libx264', acodec='aac', loglevel='error')
        .overwrite_output()
        .run()
    )

def analyze(video_path: Path, nivel: int = 5) -> dict:

    suffix = video_path.suffix.lower()
    if suffix not in ACCEPTED_EXTENSIONS:
        raise ValueError(f'Formato no aceptado: {suffix}')

    tmp_dir = Path(tempfile.mkdtemp(prefix='bioserve_'))

    try:

        if suffix != '.mp4':
            mp4_path = tmp_dir / f'{video_path.stem}.mp4'
            _convert_to_mp4(video_path, mp4_path)
        else:
            mp4_path = video_path

        df_raw, fps, width, height = process_video(mp4_path)
        if df_raw is None or df_raw.empty:
            raise ValueError('No se detectó el cuerpo en el vídeo. Verifica la calidad y el encuadre.')

        df_masked = mask_low_visibility(df_raw)
        df_clean  = cleaning_data(df_masked)
        landmark_cols = [c for c in df_clean.columns if c != 'frame_id']
        df_clean[landmark_cols] = (
            df_clean[landmark_cols]
            .interpolate(method='linear', limit=30, limit_direction='both')
            .bfill(limit=30)
            .ffill(limit=30)
        )

        skeleton_path = tmp_dir / f'{mp4_path.stem}_skeleton.mp4'
        create_output_video(mp4_path, df_clean, fps, width, height, skeleton_path)

        # --- Métricas biomecánicas ---
        start_f, min_f, max_f, target_f, knee_angles = calculate_knee_frames(df_clean)

        if not validate_knee_integrity(knee_angles, min_f, mp4_path):
            raise ValueError('El saque no supera el control de calidad de rodilla.')
        if any(np.isnan(knee_angles[f]) for f in [start_f, min_f, target_f]):
            raise ValueError('Pérdida de seguimiento en fotogramas clave.')

        hip_width   = get_hip_width(df_clean, start_f)
        stance_data = calculate_stance_metrics(df_clean, start_f, target_f)
        effect_data = calculate_effect_metrics(df_clean, start_f, max_f, hip_width, mp4_path, validate=False)

        metrics = {
            'knee_start':             round(knee_angles[start_f],  2),
            'knee_min':               round(knee_angles[min_f],    2),
            'knee_target':            round(knee_angles[target_f], 2),
            **stance_data,
            **(effect_data or {}),
            'non_dominant_arm_angle': get_non_dominant_arm_angle(df_clean, min_f, target_f),
            'hip_drive':              get_hip_drive(df_clean, start_f, min_f, hip_width),
            'shoulder_rotation':      get_shoulder_rotation(df_clean, min_f),
            'trunk_arch':             get_trunk_arch(df_clean, target_f, hip_width),
        }

        # --- Predicción IA ---
        df_m        = pd.DataFrame([metrics])
        stance_pred = _model_stance.predict(_scaler_stance.transform(df_m[STANCE_FEATURES]))[0]
        effect_pred = _model_effect.predict(_scaler_effect.transform(df_m[EFFECT_FEATURES]))[0]

        # --- Score y feedback ---
        feedback = classify_serve(
            knee_min               = metrics['knee_min'],
            hip_drive              = metrics['hip_drive'],
            jump                   = metrics.get('jump', 0),
            shoulder_rotation      = metrics['shoulder_rotation'],
            arm_extension          = metrics.get('arm_extension', 0),
            non_dominant_arm_angle = metrics['non_dominant_arm_angle'],
            trunk_arch             = metrics['trunk_arch'],
            nivel                  = nivel,
        )

        # Re-encodar con H.264 (OpenCV usa mp4v que los navegadores no soportan)
        final_name = f'{uuid.uuid4().hex}_skeleton.mp4'
        final_path = Path(tempfile.gettempdir()) / final_name
        _convert_to_mp4(skeleton_path, final_path)

        return {
            'stance':    STANCE_MAP.get(stance_pred, 'Unknown'),
            'effect':    EFFECT_MAP.get(effect_pred, 'Unknown'),
            'score':     feedback['total_score'],
            'grade':     feedback['grade'],
            'breakdown': feedback['breakdown'],
            'video_url': f'/api/video/{final_name}',
            'nivel':     nivel,
        }

        

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


    