"""
pipeline_test.py — End-to-end serve analysis pipeline
======================================================
Given a raw video of a tennis serve, this script:
  1. Extracts MediaPipe landmarks and renders the skeleton video
  2. Extracts all biomechanical metrics
  3. Predicts stance (pinpoint / platform) and effect (flat / kick / slice)
  4. Scores the serve quality and prints a full feedback report

Usage:
    python pipeline_test.py "C:/path/to/serve_video.mp4"
    or set INPUT_VIDEO below and run directly.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import joblib

# ─── Path setup ──────────────────────────────────────────────────────────────
TFG_DIR = Path(__file__).parent.parent
for module_dir in ['video_process_2', 'metrics_process_3', 'test_process_5']:
    p = str(TFG_DIR / module_dir)
    if p not in sys.path:
        sys.path.insert(0, p)

# ─── Imports ─────────────────────────────────────────────────────────────────
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
from feedback_classifier import classify_serve, print_report

# ─── Config ──────────────────────────────────────────────────────────────────
INPUT_VIDEO = Path(r"C:\Users\david\Downloads\videoOficial.mp4")
OUTPUT_DIR  = Path(__file__).parent
MODELS_DIR  = TFG_DIR / 'model_ai_process_4'

# Must match the feature lists used when training the saved .pkl models
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


# ─── Step 1: Video processing ────────────────────────────────────────────────

def extract_landmarks(input_video: Path) -> pd.DataFrame | None:
    """
    Runs MediaPipe on the video, cleans the landmark data, renders the
    skeleton output video and returns the clean DataFrame.
    Returns None if the video fails the quality gate.
    """
    print(f"\n[1/4] Processing video: {input_video.name}")

    df_raw, fps, width, height = process_video(input_video)
    if df_raw is None or df_raw.empty:
        print("  ERROR: Could not extract landmarks. Check video quality.")
        return None

    df_masked = mask_low_visibility(df_raw)
    df_clean  = cleaning_data(df_masked)

    # User pipeline: fill remaining NaN gaps more aggressively than training.
    # Training uses MAX_INTERP_GAP=10 to keep data clean; here we prefer
    # giving feedback over aborting, so we allow gaps up to 30 frames.
    landmark_cols = [c for c in df_clean.columns if c != 'frame_id']
    df_clean[landmark_cols] = (
        df_clean[landmark_cols]
        .interpolate(method='linear', limit=30, limit_direction='both')
        .bfill(limit=30)
        .ffill(limit=30)
    )

    out_video = OUTPUT_DIR / f"{input_video.stem}_skeleton.mp4"
    create_output_video(input_video, df_clean, fps, width, height, out_video)

    print(f"  Done. {len(df_clean)} frames extracted.")
    return df_clean


# ─── Step 2: Metric extraction ───────────────────────────────────────────────

def extract_metrics(df: pd.DataFrame, video_path: Path) -> dict | None:
    """
    Extracts all biomechanical metrics from the clean landmark DataFrame.
    Returns None if key frame detection fails or critical metrics are invalid.
    """
    print("\n[2/4] Extracting biomechanical metrics...")

    start_f, min_f, max_f, target_f, knee_angles = calculate_knee_frames(df)

    if not validate_knee_integrity(knee_angles, min_f, video_path):
        return None
    if any(np.isnan(knee_angles[f]) for f in [start_f, min_f, target_f]):
        print("  ERROR: NaN in key frame angles — tracking gap too large.")
        return None

    hip_width   = get_hip_width(df, start_f)
    stance_data = calculate_stance_metrics(df, start_f, target_f)
    effect_data = calculate_effect_metrics(df, start_f, max_f, hip_width, video_path)
    if effect_data is None:
        print("  WARNING: Effect metrics failed validation. Analysis may be incomplete.")

    non_dominant_arm_angle = get_non_dominant_arm_angle(df, min_f, target_f, video_path)
    hip_drive              = get_hip_drive(df, start_f, min_f, hip_width)
    shoulder_rotation      = get_shoulder_rotation(df, min_f)
    trunk_arch             = get_trunk_arch(df, target_f, hip_width)

    metrics = {
        'knee_start':             round(knee_angles[start_f],  2),
        'knee_min':               round(knee_angles[min_f],    2),
        'knee_target':            round(knee_angles[target_f], 2),
        **stance_data,
        **(effect_data or {}),
        'non_dominant_arm_angle': non_dominant_arm_angle,
        'hip_drive':              hip_drive,
        'shoulder_rotation':      shoulder_rotation,
        'trunk_arch':             trunk_arch,
    }

    print(f"  Done. {len(metrics)} metrics extracted.")
    return metrics


# ─── Step 3: AI prediction ───────────────────────────────────────────────────

def predict_serve(metrics: dict) -> dict:
    """
    Loads the trained models and predicts stance and serve effect.
    Returns a dict with 'stance' and 'effect' string labels.
    """
    print("\n[3/4] Running AI classification...")

    model_stance  = joblib.load(MODELS_DIR / 'model_stance.pkl')
    scaler_stance = joblib.load(MODELS_DIR / 'scaler_stance.pkl')
    model_effect  = joblib.load(MODELS_DIR / 'model_effect.pkl')
    scaler_effect = joblib.load(MODELS_DIR / 'scaler_effect.pkl')

    df = pd.DataFrame([metrics])

    stance_input      = scaler_stance.transform(df[STANCE_FEATURES])
    stance_prediction = model_stance.predict(stance_input)[0]

    effect_input      = scaler_effect.transform(df[EFFECT_FEATURES])
    effect_prediction = model_effect.predict(effect_input)[0]

    result = {
        'stance': STANCE_MAP.get(stance_prediction, 'Unknown'),
        'effect': EFFECT_MAP.get(effect_prediction, 'Unknown'),
    }

    print(f"  Stance: {result['stance']}  |  Effect: {result['effect']}")
    return result


# ─── Step 4: Feedback scoring ────────────────────────────────────────────────

def get_feedback(metrics: dict) -> dict:
    """Runs the feedback classifier and returns the full quality report."""
    print("\n[4/4] Computing serve quality score...")

    return classify_serve(
        knee_min               = metrics['knee_min'],
        hip_drive              = metrics['hip_drive'],
        jump                   = metrics.get('jump', 0),
        shoulder_rotation      = metrics['shoulder_rotation'],
        arm_extension          = metrics.get('arm_extension', 0),
        non_dominant_arm_angle = metrics['non_dominant_arm_angle'],
        trunk_arch             = metrics['trunk_arch'],
    )


# ─── Main orchestrator ───────────────────────────────────────────────────────

def analyze_video(input_video: Path):
    """Full pipeline: video → landmarks → metrics → AI → feedback report."""
    print(f"\n{'='*55}")
    print(f"  SERVE ANALYSIS: {input_video.name}")
    print(f"{'='*55}")

    df_clean = extract_landmarks(input_video)
    if df_clean is None:
        return

    metrics = extract_metrics(df_clean, input_video)
    if metrics is None:
        print("\nERROR: Could not extract metrics. Aborting.")
        return

    prediction = predict_serve(metrics)
    feedback   = get_feedback(metrics)

    # ─── Final output ─────────────────────────────────────────────────────
    print(f"\n{'='*55}")
    print(f"  SERVE TYPE: {prediction['effect']}  ({prediction['stance']})")
    print_report(feedback)


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    video_path = Path(sys.argv[1]) if len(sys.argv) > 1 else INPUT_VIDEO

    if not video_path.exists():
        print(f"ERROR: Video not found — {video_path}")
        sys.exit(1)

    analyze_video(video_path)
