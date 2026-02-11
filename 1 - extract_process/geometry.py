import numpy as np

def calculate_angles(a, b, c):   
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    
    denom = np.linalg.norm(ba) * np.linalg.norm(bc)
    if denom == 0: return 0.0
    
    cosine = np.dot(ba, bc) / denom
    angle = np.arccos(np.clip(cosine, -1.0, 1.0))
    return np.degrees(angle)

def calculate_distance(a, b):
    return np.linalg.norm(np.array(a)-np.array(b))

def get_hip_width(df, target):
    hip_r = np.array([df.loc[target, 'RIGHT_HIP_x'], df.loc[target, 'RIGHT_HIP_y']])
    hip_l = np.array([df.loc[target, 'LEFT_HIP_x'], df.loc[target, 'LEFT_HIP_y']])
    return calculate_distance(hip_r, hip_l)

def get_ankle_drag(df, start, target, hip_width):
    drag = 0
    
    for i in range(start, target):
        current = np.array([df.loc[i, 'RIGHT_ANKLE_x'], df.loc[i, 'RIGHT_ANKLE_y']])
        next = np.array([df.loc[i+1, 'RIGHT_ANKLE_x'], df.loc[i+1, 'RIGHT_ANKLE_y']])
        drag += np.linalg.norm(next-current)
    
    return drag/hip_width if hip_width > 0 else 0

def get_ankles_distance(df, frame):
    ankle_l = np.array([df.loc[frame, 'LEFT_ANKLE_x'], df.loc[frame, 'LEFT_ANKLE_y']])
    ankle_r = np.array([df.loc[frame, 'RIGHT_ANKLE_x'], df.loc[frame, 'RIGHT_ANKLE_y']])
    return calculate_distance(ankle_l, ankle_r)
