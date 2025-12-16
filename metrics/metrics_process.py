import pandas as pd
from pathlib import Path
import numpy as np
from scipy.signal import find_peaks


def detect_serve_phases(angles, max_dist_frames = 200):
    
    data = np.array(angles)
    
    # Find all the peaks > 150º
    peaks_id = find_peaks(data, height=150, distance = 20)
    
    # Find all throughs
    throughs_id = find_peaks(-data, height=-165, distance=20)

    # Find the best pair (Highest tendency)
    best_score = -1
    best_min_frame = -1
    best_max_frame = -1
    
    for through in throughs_id:
        for peak in peaks_id:
            if through < peak:
                distance = peak-through
                
                if distance < max_dist_frames:
                    recorrido = data[peak] - data[through]

                    if recorrido > best_score:
                        best_score = recorrido
                        best_min_frame = through
                        best_max_frame = peak
    
    if best_min_frame == -1:
        best_min_frame = np.argmin(data)
        best_max_frame = np.argmax(data)
        
    # We seeek for the exact pixel under the detected through
    window = 10
    start = max(0, best_min_frame - window)
    end = min(len(data), best_min_frame + window)
    
    # argmin devuelve índice relativo, sumamos 'inicio' para absoluto
    ajuste_idx = np.argmin(data[start:end])
    best_min_frame = start + ajuste_idx
    
    
    # We calculate the target
    total_distance = best_max_frame - best_min_frame
    target_frame = int(best_min_frame + (total_distance * 0,325) )

    return target_frame

def calculate_angle(a, b, c);



def ankle_speed(df_csv):
    
    df_angles = calculate_angle
    
    max_frame = detect_serve_phases()
    
    
    for i in max_frame:
        difference_x = df_csv['LEFT_ANKLE_x'] - df_csv['RIGHT_ANKLE_x']   
    
    
    
    pass


def max_knee(df_csv):
    pass



def metrics_pipeline(df_csv):
    pass