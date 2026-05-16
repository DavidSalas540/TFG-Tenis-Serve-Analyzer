import numpy as np
import pandas as pd
from config import FOLDER_CSVS, OUTPUT_DATASET
from features_extractor import (
    calculate_knee_frames,
    calculate_stance_metrics, calculate_effect_metrics,
    get_stance_label, get_effect_label, get_non_dominant_arm_angle,
    get_hip_drive, get_hip_width,
    get_shoulder_rotation, get_trunk_arch,
)
from quality_checks import (
    validate_knee_integrity, validate_non_dominant_arm_angle,
    validate_hip_drive, validate_shoulder_rotation, validate_trunk_arch,
)


def process_single_csv(csv_path):
    """
    Processes a single landmark CSV and returns a dict row for the training dataset.
    Returns None if any validation fails or labels are unknown.
    """
    try:
        stance_label = get_stance_label(csv_path)
        effect_label = get_effect_label(csv_path)
        if stance_label == -1 or effect_label == -1:
            print(f"Skipped {csv_path.name}: unknown label.")
            return None

        df = pd.read_csv(csv_path)

        start_f, min_f, max_f, target_f, knee_angles = calculate_knee_frames(df)
        if not validate_knee_integrity(knee_angles, min_f, csv_path):
            return None
        if any(np.isnan(knee_angles[f]) for f in [start_f, min_f, target_f]):
            print(f"Discarded {csv_path.name}: NaN in key frame angles (tracking gap).")
            return None

        hip_width   = get_hip_width(df, start_f)
        stance_data = calculate_stance_metrics(df, start_f, target_f)
        effect_data = calculate_effect_metrics(df, start_f, max_f, hip_width, csv_path)
        if effect_data is None:
            return None

        non_dominant_arm_angle = get_non_dominant_arm_angle(df, min_f, target_f, csv_path)
        if not validate_non_dominant_arm_angle(non_dominant_arm_angle, csv_path):
            return None
        
        hip_drive         = get_hip_drive(df, start_f, min_f, hip_width)
        if not validate_hip_drive(hip_drive, csv_path):
            return None

        shoulder_rotation = get_shoulder_rotation(df, min_f)
        if not validate_shoulder_rotation(shoulder_rotation, csv_path):
            return None

        trunk_arch = get_trunk_arch(df, target_f, hip_width)
        if not validate_trunk_arch(trunk_arch, csv_path):
            return None

        return {
            'video_id':               csv_path.stem,
            'stance_label':           stance_label,
            'effect_label':           effect_label,
            'knee_start':             round(knee_angles[start_f],  2),
            'knee_min':               round(knee_angles[min_f],    2),
            'knee_target':            round(knee_angles[target_f], 2),
            **stance_data,
            **effect_data,
            'non_dominant_arm_angle': non_dominant_arm_angle,
            'hip_drive':              hip_drive,
            'shoulder_rotation':      shoulder_rotation,
            'trunk_arch':             trunk_arch,
        }

    except Exception as e:
        print(f"Error processing {csv_path.name}: {e}")
        return None


if __name__ == "__main__":
    all_files = sorted(FOLDER_CSVS.glob("*.csv"))
    total     = len(all_files)
    rows      = []
    skipped   = 0

    print(f"Found {total} CSV files in {FOLDER_CSVS.name}\n")

    for i, csv_file in enumerate(all_files, 1):
        print(f"  [{i}/{total}] {csv_file.name}")
        row = process_single_csv(csv_file)
        if row is not None:
            rows.append(row)
        else:
            skipped += 1

    if rows:
        pd.DataFrame(rows).to_csv(OUTPUT_DATASET, index=False)
        print(f"\nDataset saved → {OUTPUT_DATASET}")
        print(f"  {len(rows)} processed, {skipped} skipped.")
    else:
        print("\nNo rows generated — dataset not saved.")
