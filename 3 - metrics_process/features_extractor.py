from geometry import *
from event_detector import *
from tennis_metrics import *

def get_stance_label(video_id):
    video = video_id.name.lower()
    if "pinpoint" in video: return 0
    if "platform" in video: return 1
    return -1    


def get_effect_label(video_id):
    video = str(video_id).lower()
    if 'flat' in video: return 0
    if 'kick' in video: return 1
    if 'slice' in video: return 2
    return -1
   

def calculate_stance_metrics(df, start_f, target_f):
    hip_width = get_hip_width(df, target_f)
    ankle_drag = get_ankle_drag(df, start_f, target_f, hip_width)

    min_dist_val = float('inf')
    for i in range(start_f, target_f + 1):
        d = get_ankles_distance(df, i)
        if d < min_dist_val:
            min_dist_val = d
    
    ankle_min_dist = min_dist_val / hip_width if hip_width > 0 else 0
    
    hip_tilt = abs(df.loc[target_f, 'LEFT_HIP_y'] - df.loc[target_f, 'RIGHT_HIP_y']) / hip_width if hip_width > 0 else 0

    return {
        "ankle_drag": round(ankle_drag, 4),
        "ankle_min_dist": round(ankle_min_dist, 4),
        "hip_tilt": round(hip_tilt, 4)
    }

def calculate_effect_metrics(df, start_f, min_f, max_f, target_f, hip_width):

    # Metric 1: JUMP
    jump = calculate_max_jump(df, start_f, max_f, hip_width)

    # Metric 2: 
    metrics_impact = extract_impact_metrics(df, start_f, max_f)
    
    if metrics_impact:
        impact_frame = metrics_impact['impact_frame']
        lateral_offset = metrics_impact['lateral_offset']
        arm_extension = metrics_impact['arm_extension']
    else:
        impact_frame, lateral_offset, arm_extension = None, None, None

    return {
        "jump": round(jump, 4),
        "impact_frame": impact_frame,
        "lateral_offset": lateral_offset,
        "arm_extension": arm_extension,
    }