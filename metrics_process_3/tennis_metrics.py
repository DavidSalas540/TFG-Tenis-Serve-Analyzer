import numpy as np
from geometry import calculate_angle, calculate_distance


def get_hip_width(df, frame):
    """Euclidean distance between left and right hip joints at a given frame."""
    return calculate_distance(
        [df.loc[frame, 'LEFT_HIP_x'],  df.loc[frame, 'LEFT_HIP_y']],
        [df.loc[frame, 'RIGHT_HIP_x'], df.loc[frame, 'RIGHT_HIP_y']]
    )


def get_ankles_distance(df, frame):
    """Euclidean distance between left and right ankle joints at a given frame."""
    return calculate_distance(
        [df.loc[frame, 'LEFT_ANKLE_x'],  df.loc[frame, 'LEFT_ANKLE_y']],
        [df.loc[frame, 'RIGHT_ANKLE_x'], df.loc[frame, 'RIGHT_ANKLE_y']]
    )


def get_ankle_drag(df, start_f, target_f, hip_width):
    """
    Cumulative distance traveled by the right ankle from start_f to target_f,
    normalized by hip_width.
    """
    drag = 0
    for i in range(start_f, target_f):
        current  = np.array([df.loc[i,   'RIGHT_ANKLE_x'], df.loc[i,   'RIGHT_ANKLE_y']])
        next_pos = np.array([df.loc[i+1, 'RIGHT_ANKLE_x'], df.loc[i+1, 'RIGHT_ANKLE_y']])
        drag += np.linalg.norm(next_pos - current)
    return drag / hip_width if hip_width > 0 else 0


def calculate_max_jump(df, start_f, max_f, hip_width):
    """
    Maximum upward displacement of the hip center between start_f and max_f+10,
    normalized by hip_width. In image coordinates Y increases downward, so a jump
    is a decrease in Y.
    """
    if start_f is None or max_f is None:
        return None
    df = df.copy()
    df['hip_center_y'] = (df['LEFT_HIP_y'] + df['RIGHT_HIP_y']) / 2
    y_initial  = df.loc[start_f, 'hip_center_y']
    y_min      = df.loc[start_f:max_f + 10, 'hip_center_y'].min()
    return (y_initial - y_min) / hip_width


def extract_impact_metrics(df, start_f, max_f):
    """
    Finds the impact frame (lowest RIGHT_WRIST_y) and computes:
      - lateral_offset: (wrist_x - shoulder_x) / hip_width
        negative = kick (hand left of shoulder), positive = slice (hand right)
      - arm_extension: angle at the elbow joint
    Returns a dict, or None if hip_width is zero.
    """
    impact_window = df.loc[start_f:max_f + 5, 'RIGHT_WRIST_y']
    if impact_window.isna().all():
        return None
    impact_frame = impact_window.idxmin()

    hip_width = get_hip_width(df, impact_frame)
    if hip_width == 0:
        return None

    wrist_x    = df.loc[impact_frame, 'RIGHT_WRIST_x']
    shoulder_x = df.loc[impact_frame, 'RIGHT_SHOULDER_x']
    lateral_offset = (wrist_x - shoulder_x) / hip_width

    shoulder = [df.loc[impact_frame, 'RIGHT_SHOULDER_x'], df.loc[impact_frame, 'RIGHT_SHOULDER_y']]
    elbow    = [df.loc[impact_frame, 'RIGHT_ELBOW_x'],    df.loc[impact_frame, 'RIGHT_ELBOW_y']]
    wrist    = [df.loc[impact_frame, 'RIGHT_WRIST_x'],    df.loc[impact_frame, 'RIGHT_WRIST_y']]
    arm_extension = calculate_angle(shoulder, elbow, wrist)

    return {
        "lateral_offset": round(lateral_offset, 4),
        "arm_extension":  round(arm_extension,  4),
    }


def get_hip_tilt_data(df, target_f):
    """
    Vertical difference between hips at target_f divided by hip width.
    Measures lateral tilt of the pelvis.
    """
    hip_width = calculate_distance(
        [df.loc[target_f, 'LEFT_HIP_x'],  df.loc[target_f, 'LEFT_HIP_y']],
        [df.loc[target_f, 'RIGHT_HIP_x'], df.loc[target_f, 'RIGHT_HIP_y']]
    )
    return abs(df.loc[target_f, 'LEFT_HIP_y'] - df.loc[target_f, 'RIGHT_HIP_y']) / hip_width


def get_non_dominant_arm_angles(df):
    """Computes the left wrist-shoulder-hip angle for every frame in the DataFrame."""
    angles = []
    for i in range(len(df)):
        wrist    = [df.loc[i, 'LEFT_WRIST_x'],    df.loc[i, 'LEFT_WRIST_y']]
        shoulder = [df.loc[i, 'LEFT_SHOULDER_x'],  df.loc[i, 'LEFT_SHOULDER_y']]
        hip      = [df.loc[i, 'LEFT_HIP_x'],       df.loc[i, 'LEFT_HIP_y']]
        angles.append(calculate_angle(wrist, shoulder, hip))
    return angles

def calculate_shoulder_rotation(df, min_f):
    """
    Angle difference between the shoulder axis and the hip axis at min_f
    (trophy position). Measures the X-factor: how much the shoulders are
    'coiled' relative to the hips. Larger value = more stored rotational energy.
    Both axes are measured as the angle of the LEFT→RIGHT vector relative to horizontal.
    """
    shoulder_dx = df.loc[min_f, 'RIGHT_SHOULDER_x'] - df.loc[min_f, 'LEFT_SHOULDER_x']
    shoulder_dy = df.loc[min_f, 'RIGHT_SHOULDER_y'] - df.loc[min_f, 'LEFT_SHOULDER_y']
    shoulder_angle = np.degrees(np.arctan2(shoulder_dy, shoulder_dx))

    hip_dx = df.loc[min_f, 'RIGHT_HIP_x'] - df.loc[min_f, 'LEFT_HIP_x']
    hip_dy = df.loc[min_f, 'RIGHT_HIP_y'] - df.loc[min_f, 'LEFT_HIP_y']
    hip_angle = np.degrees(np.arctan2(hip_dy, hip_dx))

    return round(shoulder_angle - hip_angle, 4)


def calculate_trunk_arch(df, target_f, hip_width):
    """
    Horizontal displacement of the hip center relative to the shoulder center
    at target_f, normalized by hip_width. Measures how much the hips are
    projected forward of the shoulders (bow shape). Larger = more arch.
    """
    hip_center_x      = (df.loc[target_f, 'LEFT_HIP_x'] + df.loc[target_f, 'RIGHT_HIP_x']) / 2
    shoulder_center_x = (df.loc[target_f, 'LEFT_SHOULDER_x'] + df.loc[target_f, 'RIGHT_SHOULDER_x']) / 2
    return round((hip_center_x - shoulder_center_x) / hip_width, 4) if hip_width > 0 else 0.0


def calculate_hip_drive(df, start_f, min_f, hip_width):
    """
    Horizontal displacement of the hip center from start_f to min_f,
    normalized by hip_width. Negative values indicate a tracking error.
    Hip center = average X of left and right hips.
    """
    x_start = (df.loc[start_f, 'LEFT_HIP_x'] + df.loc[start_f, 'RIGHT_HIP_x']) / 2
    x_min   = (df.loc[min_f,   'LEFT_HIP_x'] + df.loc[min_f,   'RIGHT_HIP_x']) / 2
    return (x_min - x_start) / hip_width if hip_width > 0 else 0.0
