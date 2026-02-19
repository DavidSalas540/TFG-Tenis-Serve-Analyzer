from pathlib import Path
from video_process_module import *

BASE_FOLDER = Path(r"C:\Users\david\Desktop\FinalData\Slice\Platform")
INPUT_VIDEO = BASE_FOLDER / "53.mp4"
OUTPUT_FOLDER = BASE_FOLDER / "Results"


def main(serve_effect: str, stance: str):
    
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    
    analyzed_name = f"{serve_effect}_{stance}_{INPUT_VIDEO.name}"
    out_video = OUTPUT_FOLDER / analyzed_name
        
    csv_name = f"{serve_effect}_{stance}_{INPUT_VIDEO.stem}_landmarks.csv"
    csv_out = OUTPUT_FOLDER / csv_name 
    
    print(f"--- Procesando {INPUT_VIDEO.name} ---")
    
    print("1. Extrayendo...")
    df_raw, f, w, h = process_video(INPUT_VIDEO)
    if df_raw is not None:
        print("2. Limpiando...")
        df_clean = cleaning_data(df_raw)
        print("3. Creando video...")
        create_comparision_video(INPUT_VIDEO, df_raw, f, w, h, df_clean, out_video)
        print("4. Guardando CSV...")
        save_csv(df_clean, csv_out)
        print("¡Prueba finalizada!")
    else:
       print("Error: No se pudo procesar el video.")

if __name__ == "__main__":
    
    main("kick", "pinpoint")
   