import os
import subprocess

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '3'
os.environ['ABSL_LOG_LEVEL'] = '3'

import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter


mp_pose = mp.solutions.pose

TARGET_WIDTH    = 1280
QUALITY_GATE    = 0.60
MAX_INTERP_GAP  = 10
LANDMARK_NAMES  = [mp_pose.PoseLandmark(i).name for i in range(33)]

SKELETON_COLOR       = (255, 0, 200)   # electric purple (BGR)
SKELETON_POINT_COLOR = (255, 80, 230)  # lighter purple for joints (BGR)


"""
    Opens a video, runs MediaPipe Pose frame by frame and returns a raw DataFrame
    with 33 landmarks (x, y, z, visibility) per frame.
    Discards the video if fewer than QUALITY_GATE (60%) of frames detect a pose.

    Returns: (df_raw, fps, width, height) or (None, 0, 0, 0) on failure.
"""

def process_video(input_video):

    cap = cv2.VideoCapture(str(input_video))
    if not cap.isOpened():
        print(f"ERROR: Cannot open video {input_video}")
        return None, 0, 0, 0

    fps    = int(cap.get(cv2.CAP_PROP_FPS))
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if width > TARGET_WIDTH:
        scale  = TARGET_WIDTH / width
        width  = int(width * scale)
        height = int(height * scale)

    raw_landmarks   = []
    frame_id        = 0
    detected_frames = 0

    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.7
    ) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame.shape[1] != width:
                frame = cv2.resize(frame, (width, height))

            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            results = pose.process(image_rgb)

            frame_data: dict[str, int | float] = {'frame_id': frame_id}

            if results.pose_landmarks:
                detected_frames += 1
                for i, landmark in enumerate(results.pose_landmarks.landmark):
                    name = LANDMARK_NAMES[i]
                    frame_data[f'{name}_x'] = landmark.x
                    frame_data[f'{name}_y'] = landmark.y
                    frame_data[f'{name}_z'] = landmark.z
                    frame_data[f'{name}_v'] = landmark.visibility
            else:
                for name in LANDMARK_NAMES:
                    frame_data[f'{name}_x'] = np.nan
                    frame_data[f'{name}_y'] = np.nan
                    frame_data[f'{name}_z'] = np.nan
                    frame_data[f'{name}_v'] = np.nan

            raw_landmarks.append(frame_data)
            frame_id += 1

    cap.release()

    quality_ratio = detected_frames / frame_id if frame_id > 0 else 0
    if quality_ratio < QUALITY_GATE:
        print(f"Discarded: {quality_ratio*100:.1f}% frames detected (min {QUALITY_GATE*100:.0f}%).")
        return None, 0, 0, 0

    return pd.DataFrame(raw_landmarks), fps, width, height


"""
    Sets x and y to NaN for any landmark that MediaPipe flagged as unreliable
    (visibility < min_visibility). Those NaNs are later repaired by cleaning_data().
"""

def mask_low_visibility(df_raw, min_visibility=0.5):
   
    df = df_raw.copy()
    for name in LANDMARK_NAMES:
        low_vis = df[f'{name}_v'] < min_visibility
        df.loc[low_vis, f'{name}_x'] = np.nan
        df.loc[low_vis, f'{name}_y'] = np.nan
    return df


"""
    Repairs NaN values via linear interpolation (capped at MAX_INTERP_GAP frames),
    then smooths x/y/z coordinates with a Savitzky-Golay filter to remove jitter.
    Gaps larger than MAX_INTERP_GAP are left as NaN to avoid flat plateaus
    caused by tracking failure (e.g. landmark lost for many consecutive frames).
    Visibility columns are left untouched.
"""

def cleaning_data(df_masked):

    df_clean = df_masked.copy()

    landmark_cols    = [col for col in df_clean.columns if col != 'frame_id']
    cols_to_smooth   = [col for col in landmark_cols if not col.endswith('_v')]

    df_clean[landmark_cols] = df_clean[landmark_cols].interpolate(
        method='linear', limit=MAX_INTERP_GAP, limit_direction='both'
    )
    df_clean[landmark_cols] = (
        df_clean[landmark_cols]
        .bfill(limit=MAX_INTERP_GAP)
        .ffill(limit=MAX_INTERP_GAP)
    )

    for col in cols_to_smooth:
        try:
            if len(df_clean) > 5 and not df_clean[col].isna().any():
                df_clean[col] = savgol_filter(df_clean[col], window_length=5, polyorder=2)
        except Exception as e:
            print(f"Smoothing skipped for {col}: {e}")

    return df_clean


"""
    Renders the clean skeleton (joints + connections) over the original video frames
    in electric purple. No overlays or debug text — production output only.
"""

def create_output_video(input_video, df_clean, fps, width, height, output_video_path):
        
    cap = cv2.VideoCapture(str(input_video))
    if not cap.isOpened():
        print(f"ERROR: Cannot open video {input_video}")
        return

    orig_width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    tmp_avi     = output_video_path.with_suffix('.tmp.avi')
    out         = cv2.VideoWriter(str(tmp_avi), cv2.VideoWriter_fourcc(*'XVID'), fps, (width, height))  # type: ignore[attr-defined]
    connections = mp_pose.POSE_CONNECTIONS
    max_frames  = len(df_clean)
    frame_idx   = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if orig_width != width:
            frame = cv2.resize(frame, (width, height))

        if frame_idx < max_frames:
            try:
                row    = df_clean.iloc[frame_idx]
                points = {}

                for i, name in enumerate(LANDMARK_NAMES):
                    x_val = row.get(f'{name}_x', np.nan)
                    y_val = row.get(f'{name}_y', np.nan)
                    if not np.isnan(x_val) and not np.isnan(y_val):
                        points[i] = (int(x_val * width), int(y_val * height))

                for start_idx, end_idx in connections:
                    if start_idx in points and end_idx in points:
                        cv2.line(frame, points[start_idx], points[end_idx], SKELETON_COLOR, 2, cv2.LINE_AA)

                for pt in points.values():
                    cv2.circle(frame, pt, 4, SKELETON_POINT_COLOR, -1, cv2.LINE_AA)

            except Exception as e:
                print(f"Error drawing frame {frame_idx}: {e}")

        out.write(frame)
        frame_idx += 1

    cap.release()
    out.release()

    subprocess.run(
        ['ffmpeg', '-y', '-i', str(tmp_avi), '-vcodec', 'libx264', '-acodec', 'aac', str(output_video_path)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
    )
    tmp_avi.unlink()
    print(f"Output video saved: {output_video_path.name}")


def save_csv(df_clean, output_csv_path):
    """Saves the clean landmark DataFrame to CSV."""
    if df_clean is not None and not df_clean.empty:
        df_clean.to_csv(output_csv_path, index=False)
        print(f"CSV saved: {output_csv_path.name}")


"""
    Full extraction pipeline for a single video:
      1. Extract raw landmarks (MediaPipe)
      2. Mask low-visibility landmarks
      3. Interpolate and smooth
      4. Render output video with clean skeleton
      5. Save CSV
"""

def pipeline(input_video, output_video_path, output_csv_path):
    
    df_raw, fps, width, height = process_video(input_video)
    if df_raw is None or df_raw.empty:
        print(f"Pipeline aborted for {input_video.name}")
        return

    df_masked = mask_low_visibility(df_raw)
    df_clean  = cleaning_data(df_masked)
    if df_clean is None:
        return

    create_output_video(input_video, df_clean, fps, width, height, output_video_path)
    save_csv(df_clean, output_csv_path)
