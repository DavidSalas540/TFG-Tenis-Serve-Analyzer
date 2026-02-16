from pathlib import Path
from video_process_module import pipeline
from config import *

def ensure_output_dirs():
    OUTPUT_VIDEOS_FOLDER.mkdir(parents=True, exist_ok=True)
    OUTPUT_CSVS_FOLDER.mkdir(parents=True, exist_ok=True)


def process_folder(folder: Path, serve_effect: str, stance: str):
    if not folder.exists():
        print(f"Folder not found: {folder}")
        return
        
    print(f"Processing folder: {folder.name}")

    videos = sorted(folder.glob("*.mp4"))
    if not videos:
        print(f"No .mp4 videos found in folder: {folder.name}")
        return

    total_videos = len(videos)

    for i, video_path in enumerate(videos, 1):
        video_id = video_path.stem.split('_')[0]
        
        analyzed_name = f"{serve_effect}_{stance}_{video_id}.mp4"
        out_video = OUTPUT_VIDEOS_FOLDER / analyzed_name
        
        csv_name = f"{serve_effect}_{stance}_{video_id}_landmarks.csv"
        csv_out = OUTPUT_CSVS_FOLDER / csv_name 
        
        if csv_out.exists():
            print(f"[{i}/{total_videos}] Skipping {video_path} (Ya existe)")
            continue
        
        print(f"[{i}/{total_videos}] Processing {video_path.name}")
        
        try:
            pipeline(video_path, out_video, csv_out)
        except Exception as e:
            print(f"ERROR CRÍTICO en el video: {video_path.name}")
            print(f"Cause: {e}")


if __name__ == "__main__":
    ensure_output_dirs()
    process_folder(FLAT_PIN_POINT_FOLDER, "flat", "pinpoint")
    process_folder(FLAT_PLATFORM_FOLDER, "flat", "platform")
    process_folder(KICK_PIN_POINT_FOLDER, "kick","pinpoint")
    process_folder(KICK_PLATFORM_FOLDER, "kick","platform")
    process_folder(SLICE_PIN_POINT_FOLDER, "slice","pinpoint")
    process_folder(SLICE_PLATFORM_FOLDER, "slice","platform")
    
    print("\n BATCH_PROCESS COMPLETED.")
    