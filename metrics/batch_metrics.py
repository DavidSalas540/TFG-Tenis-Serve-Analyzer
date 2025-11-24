import pandas as pd
from pathlib import Path
from metrics_process import metrics_pipeline

CSV_FOLDER = Path(r"C:\Users\david\Desktop\Results\datos_csv")
OUTPUT_METRICS_FILE = Path(r"C:\Users\david\Desktop\Results\Dataset_Final_Metrics\dataset_final_metrics.csv")


"""
    STEP 1: Set up the list to save all the new dataframes 
"""
dataset_list = []

csv_files = list(CSV_FOLDER.glob('*.csv'))
print(f"We are going to process {len(csv_files)} csv files.")



"""
    STEP 2: With a loop obtaining all the metrics from all the videos.
"""
for csv in csv_files:
    print(f"processing: {csv.name}")
    try:
        parts = csv.stem.split("_")
        
        effect = parts[0]
        stance = parts [1]
        video_id = parts[2]
    except:
        print("The name format of the video is not the required.")
    
    df_landmarks = pd.read_csv(csv)
    
    if df_landmarks is not None and not df_landmarks.empty:
        
        video_metrics = metrics_pipeline(df_landmarks)
        
        video_metrics['video_id'] = video_id
        video_metrics['stance'] = stance
        video_metrics['effect'] = effect
        
        dataset_list.append(video_metrics)
    
    else: print("The csv is empty")


"""
    STEP 3: Create the final dataframe with all the metrics
"""
print("Creating the final dataset")
df_final = pd.DataFrame(dataset_list)

cols = ['video_id', 'stance', 'effect'] + [c for c in df_final.columns if c not in ['video_id', 'stance', 'effect', 'filename']]
df_final[cols]

"""
    STEP 4: Save the dataframe in a csv
"""

df_final.to_csv(OUTPUT_METRICS_FILE, index = False)
print(f"Dataset saved it in {OUTPUT_METRICS_FILE}")
