import sys
from pathlib import Path
import pandas as pd
import joblib

TFG_DIR = Path(r"C:\Users\david\Documents\TFG")
sys.path.append(str(TFG_DIR))
for subcarpeta in TFG_DIR.iterdir():
    if subcarpeta.is_dir():
        sys.path.append(str(subcarpeta))
        
from video_process_module import *
from features_extractor import *
from features_extractor import *
from event_detector import *

INPUT_VIDEO = Path(r"C:\Users\david\Desktop\David_serve.mp4")
OUTPUT_DIR = Path(r"C:\Users\david\Documents\TFG\5-test_process")

OUT_VIDEO = OUTPUT_DIR / "video_test_procesado.mp4"
OUT_CSV_RAW = OUTPUT_DIR / "test_mediapipe.csv"
OUT_CSV_STANCE = OUTPUT_DIR / "test_stance_ai.csv"
OUT_CSV_EFFECT = OUTPUT_DIR / "test_effect_ai.csv"

CARPETA_MODELOS = TFG_DIR / "4 - model_ai_process"

model_stance = joblib.load(CARPETA_MODELOS / 'model_stance.pkl')
scaler_stance = joblib.load(CARPETA_MODELOS / 'scaler_stance.pkl')

model_effect = joblib.load(CARPETA_MODELOS / 'model_effect.pkl')
scaler_effect = joblib.load(CARPETA_MODELOS / 'scaler_effect.pkl')



def pipeline_analyze(input_video, output_video_path):
    df_raw, f, w, h = process_video(input_video)
    if df_raw is None or df_raw.empty:
        print(f"CRITICAL ERROR, Pipeline aborted for {input_video.name}")
        return

    df_clean = cleaning_data(df_raw)
    if df_clean is None:
        return
    
    create_comparision_video(input_video, df_raw, f, w, h, df_clean, output_video_path)
       
    return df_clean

def metrics_extractor(df):
    # 1. We calculate the angles of knee taking into account the hip and the ankle
        angles = get_knee_angles_series(df)

        # 2. We calculate the frame of the angles of the knee
        start_f, min_f, max_f, target_f = calculate_knee_frame(df)
              
        # 4. We obtain the METRICS
        hip_width = get_hip_width(df, start_f)
        stance_data = calculate_stance_metrics(df, start_f, target_f)
        effect_data = calculate_effect_metrics(df, start_f, min_f, max_f, target_f, hip_width)
                    
        row_data = {
            "knee_start": round(angles[start_f], 2),
            "knee_min": round(angles[min_f], 2),
            "knee_target": round(angles[target_f], 2),
            **stance_data,
            **effect_data
        }
        
        return row_data


def predict_serve(INPUT_VIDEO):
    
    result = {}
    
    df_clean = pipeline_analyze(INPUT_VIDEO, OUT_VIDEO)
    if df_clean is None:
        return {"error": "It's not possible to process the video."}
    
    video_data = metrics_extractor(df_clean)
    
    features_stance = ['knee_start', 'knee_min', 'knee_target', 'ankle_drag', 'ankle_min_dist', 'hip_tilt']
    features_effect = ['knee_start', 'knee_min', 'knee_target', 'hip_tilt', 'jump', 'impact_frame', 'lateral_offset', 'arm_extension']
    
    df_stance_ai = pd.DataFrame([video_data])[features_stance]
    df_effect_ai = pd.DataFrame([video_data])[features_effect]
    
    df_stance_ai.to_csv(OUT_CSV_STANCE, index=False)
    df_effect_ai.to_csv(OUT_CSV_EFFECT, index=False)
    
    scaled_stance = scaler_stance.transform(df_stance_ai)
    prediction_stance = model_stance.predict(scaled_stance)[0]
    result['stance'] = "Platform" if prediction_stance == 1 else "Pinpoint"
    
    scaled_effect = scaler_effect.transform(df_effect_ai)
    prediction_effect = model_effect.predict(scaled_effect)[0]
    effect_map = {0: "Flat", 1: "Kick", 2: "Slice"}
    result['effect'] = effect_map.get(prediction_effect, " ") 
    
    return result

if __name__ == '__main__':    
    result = predict_serve(INPUT_VIDEO)
    print(f"RESULT OF THE ANALYSIS: ")
    print(f"Stance: {result['stance']} and Effect: {result['effect']}") 