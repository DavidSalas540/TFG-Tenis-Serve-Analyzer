import pandas as pd
from pathlib import Path
from features_extractor import *
from features_extractor import *
from event_detector import *
from quality_checks import *

FOLDER_CSVS = Path(r"C:\Users\david\Documents\TFG\data_csv")


def process_single_csv(csv_path):
    try:
        df = pd.read_csv(csv_path)
    
        # 1. We calculate the angles of knee taking into account the hip and the ankle
        angles = get_knee_angles_series(df)


        # 2. We calculate the frame of the angles of the knee
        start_f, min_f, max_f, target_f = calculate_knee_frame(df)
        
        
        # 3. We use a quality filter to know if Mediapipe created an impossible angle
        if not validate_knee_integrity(angles, min_f, csv_path):
            return None
       
        
        # 4. We obtain the METRICS
        hip_width = get_hip_width(df, start_f)
        stance_data = calculate_stance_metrics(df, start_f, target_f)
        effect_data = calculate_effect_metrics(df, start_f, min_f, max_f, target_f, hip_width)
        
        
        # 5. Quality assurance of the effect_data
        ok, cause = validate_effect_metrics(effect_data)
        if not ok:
            print(f"Discard {csv_path.name} because {cause}")
            return None
        
 
        # 6. We set the labels of the video
        stance_label = get_stance_label(csv_path)
        effect_label = get_effect_label(csv_path)
        
        
        # 7. We consolidate the row
        if stance_label != -1 and effect_label != -1:
            row_data = {
            'video_id': csv_path.stem,
            "stance_label": stance_label,
            "effect_label": effect_label,
            "knee_start": round(angles[start_f], 2),
            "knee_min": round(angles[min_f], 2),
            "knee_target": round(angles[target_f], 2),
            **stance_data,
            **effect_data
            }          
        else: print(f"ERROR in the label of the CSV {csv_path.name}.")
        
        return row_data
    
    except Exception as e:
        print(f"Error procesando {csv_path}: {e}")
        return None
    

def main_batch_process():
    final_dataset = []
    
    all_files = list(FOLDER_CSVS.glob("*.csv"))
    
    for csv_file in all_files:
        row = process_single_csv(csv_file)
        if row is not None: final_dataset.append(row)
    
    if final_dataset:
        pd.DataFrame(final_dataset).to_csv("train_dataset.csv", index=False)
        print(f"Dataset generated with {len(final_dataset)} rows")

if __name__ == "__main__":
    main_batch_process()
    
