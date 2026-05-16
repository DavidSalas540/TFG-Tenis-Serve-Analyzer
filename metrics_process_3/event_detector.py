from geometry import calculate_angle
from scipy.signal import find_peaks
import numpy as np

PEAK_MIN_HEIGHT   = 150    # minimum knee angle (degrees) to consider full extension
VALLEY_MAX_HEIGHT = 165    # maximum knee angle (degrees) to consider a loading valley
PEAK_MIN_DISTANCE = 20     # minimum frames between consecutive peaks/valleys
MAX_PHASE_FRAMES  = 200    # max frames allowed between valley and peak pair
REFINE_WINDOW     = 10     # local window (frames) to refine the minimum frame
START_SEARCH_BACK = 150    # frames to search backwards for the upright start position
TARGET_FACTOR     = 0.325  # 32.5% of min→max arc = maximum inertia point before takeoff


def get_knee_angles_series(df):
    """Computes the left knee angle for every frame in the DataFrame."""
    return [calculate_angle(
        [df.loc[i, 'LEFT_HIP_x'],   df.loc[i, 'LEFT_HIP_y']],
        [df.loc[i, 'LEFT_KNEE_x'],  df.loc[i, 'LEFT_KNEE_y']],
        [df.loc[i, 'LEFT_ANKLE_x'], df.loc[i, 'LEFT_ANKLE_y']]
    ) for i in range(len(df))]


def detect_serve_phases(angles, max_dist_frames=MAX_PHASE_FRAMES):
    """
    Identifies 4 key frames of a tennis serve from the knee angle trajectory:
      start    — upright position before loading
      best_min — maximum knee flexion (loading phase)
      best_max — maximum knee extension (takeoff)
      target   — 32.5% of the min→max arc (maximum inertia point)
    Returns (start, best_min, best_max, target).
    """
    data = np.array(angles)

    peaks,   _ = find_peaks(data,  height=PEAK_MIN_HEIGHT,   distance=PEAK_MIN_DISTANCE)
    valleys, _ = find_peaks(-data, height=-VALLEY_MAX_HEIGHT, distance=PEAK_MIN_DISTANCE)

    best_score, best_min, best_max = -1, -1, -1
    for valley in valleys:
        for peak in peaks:
            if valley < peak and (peak - valley) < max_dist_frames:
                rom = data[peak] - data[valley]
                if rom > best_score:
                    best_score, best_min, best_max = rom, valley, peak

    if best_min == -1:
        best_min, best_max = int(np.argmin(data)), int(np.argmax(data))

    ini = max(0, best_min - REFINE_WINDOW)
    end = min(len(data), best_min + REFINE_WINDOW)
    best_min = ini + int(np.argmin(data[ini:end]))

    target = int(best_min + (best_max - best_min) * TARGET_FACTOR)

    s_search = max(0, best_min - START_SEARCH_BACK)
    pre_data = data[s_search:best_min]
    start = s_search + int(np.argmax(pre_data)) if len(pre_data) > 0 else 0

    return start, best_min, best_max, target


def calculate_knee_frames(df):
    """Extracts knee angles from the DataFrame and detects the 4 serve phases."""
    knee_angles = get_knee_angles_series(df)
    start_f, min_f, max_f, target_f = detect_serve_phases(knee_angles)
    return start_f, min_f, max_f, target_f, knee_angles
