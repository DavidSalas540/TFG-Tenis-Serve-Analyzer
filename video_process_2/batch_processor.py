from pathlib import Path
from video_processor import pipeline
from config import (
    FLAT_PIN_POINT_FOLDER, FLAT_PLATFORM_FOLDER,
    KICK_PIN_POINT_FOLDER, KICK_PLATFORM_FOLDER,
    SLICE_PIN_POINT_FOLDER, SLICE_PLATFORM_FOLDER,
    OUTPUT_VIDEOS_FOLDER, OUTPUT_CSVS_FOLDER,
)

FOLDERS = [
    (FLAT_PIN_POINT_FOLDER,  "flat",  "pinpoint"),
    (FLAT_PLATFORM_FOLDER,   "flat",  "platform"),
    (KICK_PIN_POINT_FOLDER,  "kick",  "pinpoint"),
    (KICK_PLATFORM_FOLDER,   "kick",  "platform"),
    (SLICE_PIN_POINT_FOLDER, "slice", "pinpoint"),
    (SLICE_PLATFORM_FOLDER,  "slice", "platform"),
]


def ensure_output_dirs():
    """Creates output directories if they don't exist."""
    OUTPUT_VIDEOS_FOLDER.mkdir(parents=True, exist_ok=True)
    OUTPUT_CSVS_FOLDER.mkdir(parents=True, exist_ok=True)


def process_folder(folder: Path, serve_effect: str, stance: str):
    """
    Processes all .mp4 videos in a folder through the extraction pipeline.
    Skips videos whose CSV already exists. Prints a summary at the end.
    """
    if not folder.exists():
        print(f"Folder not found: {folder}")
        return

    videos = sorted(folder.glob("*.mp4"))
    if not videos:
        print(f"No .mp4 videos found in: {folder.name}")
        return

    print(f"\nProcessing folder: {folder.name} ({len(videos)} videos)")

    processed, skipped, failed = 0, 0, 0

    for i, video_path in enumerate(videos, 1):
        video_id  = video_path.stem
        out_video = OUTPUT_VIDEOS_FOLDER / f"{serve_effect}_{stance}_{video_id}.mp4"
        csv_out   = OUTPUT_CSVS_FOLDER   / f"{serve_effect}_{stance}_{video_id}_landmarks.csv"

        if csv_out.exists():
            print(f"  [{i}/{len(videos)}] Skipping {video_path.name} (already exists)")
            skipped += 1
            continue

        print(f"  [{i}/{len(videos)}] Processing {video_path.name}")
        try:
            pipeline(video_path, out_video, csv_out)
            processed += 1
        except Exception as e:
            print(f"  ERROR: {video_path.name} — {e}")
            failed += 1

    print(f"  Done: {processed} processed, {skipped} skipped, {failed} failed.")


if __name__ == "__main__":
    ensure_output_dirs()
    for folder, effect, stance in FOLDERS:
        process_folder(folder, effect, stance)
    print("\nBatch process completed.")
