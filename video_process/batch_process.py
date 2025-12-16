from pathlib import Path
from video_process.video_process_module import pipeline
from video_process.config import (
    FLAT_PIN_POINT_FOLDER, FLAT_PLATFORM_FOLDER,
    KICK_PIN_POINT_FOLDER, KICK_PLATFORM_FOLDER,
    SLICE_PIN_POINT_FOLDER, SLICE_PLATFORM_FOLDER,
    OUTPUT_VIDEOS_FOLDER, OUTPUT_CSVS_FOLDER
)

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

    for video_path in videos:
        analyzed_name = f"{serve_effect}_{stance}_{video_path.name}"
        out_video = OUTPUT_VIDEOS_FOLDER / analyzed_name
        
        csv_name = f"{serve_effect}_{stance}_{video_path.stem}_landmarks.csv"
        csv_out = OUTPUT_CSVS_FOLDER / csv_name 
        
        pipeline(video_path, out_video, csv_out)


if __name__ == "__main__":
    ensure_output_dirs()
    process_folder(FLAT_PIN_POINT_FOLDER, "flat", "pinpoint")
    process_folder(FLAT_PLATFORM_FOLDER, "flat", "platform")
    process_folder(KICK_PIN_POINT_FOLDER, "kick","pinpoint")
    process_folder(KICK_PLATFORM_FOLDER, "kick","platform")
    process_folder(SLICE_PIN_POINT_FOLDER, "slice","pinpoint")
    process_folder(SLICE_PLATFORM_FOLDER, "slice","platform")
    