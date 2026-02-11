import pandas as pd
from pathlib import Path
from features_extractor import *
from features_extractor import *
from event_detector import *

FOLDER_CSVS = Path(r"C:\Users\david\Documents\TFG\data_csv")


def process_single_csv(csv_path):
    try:
        df = pd.read_csv(csv_path)
    
        # 1. We calculate the angles of knee taking into account the hip and the ankle
        angles = []
        for i in range(len(df)):
            l_hip = [df.loc[i, 'LEFT_HIP_x'], df.loc[i, 'LEFT_HIP_y']]
            l_knee = [df.loc[i, 'LEFT_KNEE_x'], df.loc[i, 'LEFT_KNEE_y']]
            l_ankle = [df.loc[i, 'LEFT_ANKLE_x'], df.loc[i, 'LEFT_ANKLE_y']]
            angles.append(calculate_angles(l_hip, l_knee, l_ankle))
        
        # 2. We calculate the frame of the angles of the knee
        start_p, min_p, max_p, target_p = detectar_fases_saque(angles)
        
        
        # 3. We use a quality filter to know if Mediapipe created an impossible angle
        if angles[min_p] < 45:
            print(f"Descarte: {csv_path.name} (Ángulo de rodilla imposible) {round(angles[min_p], 2)}º")
            return None 
        
        # 4. We Calculate the METRICS
        stance_data = calculate_stance_metrics(df, start_p, target_p)
        #effect_data = calculate_effect_metrics(df, events)
        
        # 5. We name the stance label
        name = csv_path.name.lower()
        if "pinpoint" in name: label = 0
        elif "platform" in name: label = 1
        else: label = -1
        
        # 6. We consolidate the row
        if label != -1:
            row_data = {
            'video_id': csv_path.stem,
            "stance_label": label,
            "knee_start": round(angles[start_p], 2),
            "knee_min": round(angles[min_p], 2),
            "knee_Target": round(angles[target_p], 2),
            **stance_data,
            #**effect_data
            }          
        else: print("ERROR in the label of the CSV.")
        
        return row_data
    
    except Exception as e:
        print(f"Error procesando {csv_path}: {e}")
        return None
    

def main_batch_process():
    final_dataset = []
    
    all_files = list(FOLDER_CSVS.glob("*.csv"))
    
    for csv_file in all_files:
        row = process_single_csv(csv_file)
        if row is not None:
            final_dataset.append(row)
        else: print(f"ERROR during the process of the csv {csv_file}")
    
    if final_dataset:
        pd.DataFrame(final_dataset).to_csv("train_dataset.csv", index=False)
        print(f"Dataset generated with {len(final_dataset)} rows")

if __name__ == "__main__":
    main_batch_process()
    
