from event_detector import calculate_knee_frames
from tennis_metrics import (
    get_hip_width, get_ankle_drag, get_ankles_distance,
    calculate_max_jump, extract_impact_metrics, get_non_dominant_arm_angles,
    calculate_hip_drive, calculate_shoulder_rotation, calculate_trunk_arch,
)
from quality_checks import validate_effect_metrics


def get_stance_label(video_id):
    """Returns 0 (pinpoint), 1 (platform), or -1 if unknown."""
    name = str(video_id).lower()
    if "pinpoint" in name: return 0
    if "platform" in name: return 1
    return -1


def get_effect_label(video_id):
    """Returns 0 (flat), 1 (kick), 2 (slice), or -1 if unknown."""
    name = str(video_id).lower()
    if "flat"  in name: return 0
    if "kick"  in name: return 1
    if "slice" in name: return 2
    return -1


def calculate_stance_metrics(df, start_f, target_f):
    """
    Returns a dict with ankle_drag, ankle_min_dist, and hip_tilt,
    all normalized by hip width at target_f.
    """
    hip_width      = get_hip_width(df, target_f)
    ankle_drag     = get_ankle_drag(df, start_f, target_f, hip_width)
    min_dist       = min(get_ankles_distance(df, i) for i in range(start_f, target_f + 1))
    ankle_min_dist = min_dist      / hip_width if hip_width > 0 else 0
    hip_tilt       = abs(df.loc[target_f, 'LEFT_HIP_y'] - df.loc[target_f, 'RIGHT_HIP_y']) / hip_width if hip_width > 0 else 0

    return {
        "ankle_drag":     round(ankle_drag,     4),
        "ankle_min_dist": round(ankle_min_dist, 4),
        "hip_tilt":       round(hip_tilt,       4),
    }


def calculate_effect_metrics(df, start_f, max_f, hip_width, csv_path, validate=True):
    """
    Returns a dict with jump, lateral_offset, and arm_extension.
    validate=True  → training pipeline: returns None if quality checks fail.
    validate=False → backend: always returns the data, never discards.
    """
    jump           = calculate_max_jump(df, start_f, max_f, hip_width)
    metrics_impact = extract_impact_metrics(df, start_f, max_f)

    if metrics_impact:
        lateral_offset = metrics_impact['lateral_offset']
        arm_extension  = metrics_impact['arm_extension']
    else:
        lateral_offset = arm_extension = None

    effect_data = {
        "jump":           round(jump, 4),
        "lateral_offset": lateral_offset,
        "arm_extension":  arm_extension,
    }

    if validate:
        ok, cause = validate_effect_metrics(effect_data)
        if not ok:
            print(f"Discarded {csv_path.name}: {cause}")
            return None

    return effect_data


def get_non_dominant_arm_angle(df, min_f, target_f, csv_path, window_size=5):
    """
    Returns the maximum non-dominant arm angle in a ±window_size frame window
    around min_f, clipped to [0, target_f].
    """
    df_clean     = df.iloc[:target_f + 1].copy().reset_index(drop=True)
    all_angles   = get_non_dominant_arm_angles(df_clean)
    start_win    = max(0, min_f - window_size)
    end_win      = min(len(all_angles) - 1, min_f + window_size)
    neighborhood = all_angles[start_win:end_win + 1]

    return max(neighborhood) if neighborhood else 0.0


def get_hip_drive(df, start_f, min_f, hip_width):
    """
    Returns the hip drive, calculated as the difference between the hip position
    at minimum knee flexion and the hip position at the start of the motion,
    normalized by hip width.
    """
    return round(calculate_hip_drive(df, start_f, min_f, hip_width), 4)


def get_shoulder_rotation(df, min_f):
    """
    X-factor: angle difference between shoulder axis and hip axis at trophy
    position (min_f). Measures rotational energy stored in the upper body.
    """
    return calculate_shoulder_rotation(df, min_f)


def get_trunk_arch(df, target_f, hip_width):
    """
    Horizontal displacement of hip center relative to shoulder center at
    target_f, normalized by hip_width. Measures the bow shape of the body.
    """
    return calculate_trunk_arch(df, target_f, hip_width)
