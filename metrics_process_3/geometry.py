import numpy as np


"""
    Angle in degrees at vertex B formed by segments B-A and B-C.
    Returns 0.0 if any segment has zero length.
"""


def calculate_angle(a, b, c):
    
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b

    denom = np.linalg.norm(ba) * np.linalg.norm(bc)
    if denom == 0:
        return 0.0

    cosine = np.dot(ba, bc) / denom
    return np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))


def calculate_distance(a, b):
    return np.linalg.norm(np.array(a) - np.array(b))
