import numpy as np
from geometry import calculate_angles, calculate_distance


# --- UTILS ---
def get_hip_width(df, frame):
    return calculate_distance(
        [df.loc[frame, 'LEFT_HIP_x'], df.loc[frame, 'LEFT_HIP_y']],
        [df.loc[frame, 'RIGHT_HIP_x'], df.loc[frame, 'RIGHT_HIP_y']]
    )


def get_ankles_distance(df, frame):
    return calculate_distance(
        [df.loc[frame, 'LEFT_ANKLE_x'], df.loc[frame, 'LEFT_ANKLE_y']],
        [df.loc[frame, 'RIGHT_ANKLE_x'], df.loc[frame, 'RIGHT_ANKLE_y']]
    )
 
 
# --- SERIES ---
def get_knee_angles_series(df):
    return [calculate_angles(
      [df.loc[i, 'LEFT_HIP_x'], df.loc[i, 'LEFT_HIP_y']],
      [df.loc[i, 'LEFT_KNEE_x'], df.loc[i, 'LEFT_KNEE_y']],
      [df.loc[i, 'LEFT_ANKLE_x'], df.loc[i, 'LEFT_ANKLE_y']] 
    ) for i in range(len(df))]
    
    
# --- SPECIFIC METRICS ---

# METRIC 1 (STANCE): ankle_drag
def get_ankle_drag(df, start_f, target_f, hip_width):
    drag = 0
    
    for i in range(start_f, target_f):
        current = np.array([df.loc[i, 'RIGHT_ANKLE_x'], df.loc[i, 'RIGHT_ANKLE_y']])
        next = np.array([df.loc[i+1, 'RIGHT_ANKLE_x'], df.loc[i+1, 'RIGHT_ANKLE_y']])
        drag += np.linalg.norm(next-current)
    
    return drag / hip_width if hip_width > 0 else 0


# METRIC 1: EFFECT
def calculate_max_jump(df, start_f, max_f, hip_width):
    if start_f is None or max_f is None: return None
    
    df['hip_center_y'] = (df['LEFT_HIP_y'] + df['RIGHT_HIP_y']) / 2
    
    y_initial = df.loc[start_f, 'hip_center_y']
    window_jump = df.loc[start_f:max_f+10, 'hip_center_y']
    y_max = window_jump.min()
       
    return (y_initial - y_max) / hip_width


# METRIC 2: EFFECT
def extract_impact_metrics(df, start_f, max_f):
    # 1. Search for the real impact  
    impact_window = df.loc[start_f : max_f + 5, 'RIGHT_WRIST_y']
    impact_frame = impact_window.idxmin()
    
    # We calculte the hip_width for the impact frame
    hip_width = get_hip_width(df, impact_frame)
    if hip_width == 0: return None
    
    # 2. WRIST OFFSET (Lateral position respective to the shoulder)
    # If the value is negative, the hand is on the left side of the shoulder (Kick)
    # If the value is really positive (slice)
    wrist_x = df.loc[impact_frame, 'RIGHT_WRIST_x']
    shoulder_x = df.loc[impact_frame, 'RIGHT_SHOULDER_x']
    lateral_offset = (wrist_x - shoulder_x) / hip_width
    
    # 3. ELBOW ANGLE 
    shoulder = [df.loc[impact_frame, 'RIGHT_SHOULDER_x'], df.loc[impact_frame, 'RIGHT_SHOULDER_y']]
    elbow = [df.loc[impact_frame, 'RIGHT_ELBOW_x'], df.loc[impact_frame, 'RIGHT_ELBOW_y']]
    wrist = [df.loc[impact_frame, 'RIGHT_WRIST_x'], df.loc[impact_frame, 'RIGHT_WRIST_y']]
    
    arm_extension = calculate_angles(shoulder, elbow, wrist)
    
    return {
        "impact_frame": impact_frame,
        "lateral_offset": round(lateral_offset, 4),
        "arm_extension": round(arm_extension, 4)
    }
    
# METRIC 3 (EFFECT): HIP ANGLE IN THE MAX EXTENSION OF THE KNEE
def get_hip_tilt_data(df, target_f):
    hip_width_min_f = calculate_distance(
        [df.loc[target_f, 'LEFT_HIP_x'], df.loc[target_f, 'LEFT_HIP_y']], 
        [df.loc[target_f, 'RIGHT_HIP_x'], df.loc[target_f, 'RIGHT_HIP_y']]
    )
    return abs(df.loc[target_f, 'LEFT_HIP_y'] - df.loc[target_f, 'RIGHT_HIP_y']) / hip_width_min_f
    
