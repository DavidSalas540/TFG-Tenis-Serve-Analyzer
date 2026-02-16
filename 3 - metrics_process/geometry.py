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
