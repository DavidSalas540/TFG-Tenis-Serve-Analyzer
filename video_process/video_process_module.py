import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter


# Set up Mediapipe
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


""" 
    STEP 1: Getting the dataframe data with the raw landmarks
"""
def process_video(input_video):  
    
    cap = cv2.VideoCapture(str(input_video))
    if not cap.isOpened():
        print(f"CRITIC ERROR: It is not possible to open video in {input_video}")
        return None, 0, 0, 0
    
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    TARGET_WIDTH = 1280
    
    if width > TARGET_WIDTH:
        scale = TARGET_WIDTH / width
        width = int(width * scale)
        height = int(height * scale)

    raw_landmarks = []
    frame_id = 0
    
    detected_frames = 0
                       
    with mp_pose.Pose(
        static_image_mode=False,       # Video mode, this learns from the previous frame
        model_complexity=2,            # The heavy model
        min_detection_confidence=0.5,  # To find the tennis player for the first time
        min_tracking_confidence=0.7    # This is for fast movements
    ) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
                        
            if frame.shape[1] != width:
                frame = cv2.resize(frame, (width, height))
                        
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False # This is for efficiency. With this we don't need to have a copy in RAM
            results = pose.process(image_rgb)
            
            frame_data = {'frame_id': frame_id}
            
            if results.pose_landmarks:
                detected_frames += 1
                
                for i, landmark in enumerate(results.pose_landmarks.landmark):
                    name = mp_pose.PoseLandmark(i).name
                    frame_data[f'{name}_x'] = landmark.x
                    frame_data[f'{name}_y'] = landmark.y
                    frame_data[f'{name}_z'] = landmark.z
                    frame_data[f'{name}_v'] = landmark.visibility
            else:
                for i in range(33):
                    name = mp_pose.PoseLandmark(i).name
                    frame_data[f'{name}_x'] = np.nan
                    frame_data[f'{name}_y'] = np.nan
                    frame_data[f'{name}_z'] = np.nan
                    frame_data[f'{name}_v'] = np.nan
            
            raw_landmarks.append(frame_data)
            frame_id += 1
            
    cap.release()
    
    if frame_id == 0:
        quality_ratio = 0
    else:
        quality_ratio = detected_frames / frame_id
    
    # 2. QUALITY GATE 
    quality_gate = 0.60
    
    if quality_ratio < quality_gate:
        print(f"Discarted video: Not enough quality (<{quality_ratio*100}% detected).")
        return None, 0, 0, 0
    
    df_raw = pd.DataFrame(raw_landmarks)
    return df_raw, fps, width, height


""" 
    STEP 2: Cleaning the dataframe
"""
def cleaning_data(df_raw):
    df_clean = df_raw.copy()
    
    landmarks_columns = [col for col in df_clean.columns if col != 'frame_id']
    
    # INTERPOLATION
    df_clean[landmarks_columns] = df_clean[landmarks_columns].interpolate(method='linear', limit_direction='both')
    
    # NaNs in the borders
    df_clean[landmarks_columns] = df_clean[landmarks_columns].fillna(method='bfill').fillna(method='ffill')
    
    columns_to_smooth = [col for col in landmarks_columns if not col.endswith('_v')]
    
    # Smoothing - Savitzly-Golay Filter
    for col in columns_to_smooth:
        try:
            if len(df_clean)>5:
                df_clean[col] = savgol_filter(df_clean[col], window_length=5, polyorder=2)
        except Exception as e:
            pass
    
    return df_clean


""" 
    STEP 3: create a comparision between the df_raw and the df_clean to see if there is an improvment
"""
def create_comparision_video(input_video, df_raw, fps, width, height, df_clean, output_video_path):
    
    cap = cv2.VideoCapture(str(input_video))
    if not cap.isOpened(): return
    
    orig_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    
    output_path_str = str(output_video_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path_str, fourcc, fps, (width, height))
    
    frame_idx = 0
    max_frames = len(df_raw)
    connections = mp_pose.POSE_CONNECTIONS    

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        if width != orig_width:
            frame = cv2.resize(frame, (width, height))
            
        if frame_idx < max_frames:
            
            # 1. We draw with red the raw dataframe, and we select a bigeer radius (5) in order to seen it behind the green one (df_clean)
            try:
                row_raw = df_raw.iloc[frame_idx]    # With these we select row by row (frame by frame)
                for i in range(33):
                    name = mp_pose.PoseLandmark(i).name
                    if f'{name}_x' in row_raw and not np.isnan(row_raw[f'{name}_x']):
                        x = int(row_raw[f'{name}_x'] * width)
                        y = int(row_raw[f'{name}_y'] * height)
                        
                        cv2.circle(frame, (x, y), 5, (0, 0, 255), -1) # We paint the point
            except: pass

            # 2. We draw with green the clean dataframe, and we select a smaller radius(2) in order to see better the precicion
            try:
                row_clean = df_clean.iloc[frame_idx]
                clean_points = {} 
                
                for i in range(33):
                    name = mp_pose.PoseLandmark(i).name
                    if f'{name}_x' in row_clean and not np.isnan(row_clean[f'{name}_x']):
                        x = int(row_clean[f'{name}_x'] * width)
                        y = int(row_clean[f'{name}_y'] * height)
                        clean_points[i] = (x, y)

                # Drawing the connection lines between points
                for connection in connections:
                    start_idx, end_idx = connection
                    if start_idx in clean_points and end_idx in clean_points:
                        cv2.line(frame, clean_points[start_idx], clean_points[end_idx], (0, 255, 0), 2)

                for point in clean_points.values():
                    cv2.circle(frame, point, 2, (0, 255, 0), -1) # We paint the point
                        
            except Exception as e:
                print(f"Error frame {frame_idx}: {e}")
 
        
        cv2.putText(frame, "RAW (Rojo - Grande)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(frame, "CLEAN (Verde - Pequeno)", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        out.write(frame)
        frame_idx += 1

    cap.release()
    out.release()
    print(f"Video saved in: {output_video_path.name}")


""" 
    STEP 4: create a csv with the clean dataframe
"""
def save_csv(df_clean, output_csv_path):
    if df_clean is not None and not df_clean.empty:
        df_clean.to_csv(output_csv_path, index = False)
        print(f"CSV saved in: {output_csv_path.name}")


"""
    PIPELINE
"""
def pipeline(input_video, output_video_path, output_csv_path):
    df_raw, f, w, h = process_video(input_video)
    df_clean = cleaning_data(df_raw)
    create_comparision_video(input_video, df_raw, f, w, h, df_clean, output_video_path)
    save_csv(df_clean, output_csv_path)

        