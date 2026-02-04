from geometry import *

def calculate_stance_metrics(df, start, target):

    hip_width = get_hip_width(df, target)
    ankle_drag = get_ankle_drag(df, start, target, hip_width)
    
    min_dist_val = float('inf')
    
    for i in range(start, target + 1):
        d = get_ankles_distance(df, i)
        if d < min_dist_val:
            min_dist_val = d
    
    ankle_min_dist = min_dist_val / hip_width if hip_width > 0 else 0
    
    hip_tilt = abs(df.loc[target, 'LEFT_HIP_y'] - df.loc[target, 'RIGHT_HIP_y']) / hip_width if hip_width > 0 else 0

    return {
        "ankle_drag": round(ankle_drag, 4),
        "ankle_min_dist": round(ankle_min_dist, 4),
        "hip_tilt": round(hip_tilt, 4)
    }

# def calculate_effect_metrics(df, key_events):
    return