import cv2
import mediapipe as mp
import os
import sys
from pathlib import Path
import geometry

VIDEO_INPUT = Path(r"C:\Users\david\Desktop\Descargador\downloads\Novak_Djokovic_vs_Andy_Murray_Full_Match_Australian_Open_2016_Final [Ys28qDiLLAQ].mp4")
OUTPUT_DIR = Path(r"C:\Users\david\Desktop\serves")

def auto_extract_serves(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Error: No se puede abrir {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5, model_complexity=1)

    found_serves = 0
    frame_idx = 0
    skip_frames = 10 # Escaneo rápido cada 10 frames

    print(f"🚀 Procesando {total_frames} frames ({round(total_frames/(fps*3600), 2)} horas)...")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        # Solo procesamos si estamos en el frame que toca (salto temporal)
        if frame_idx % skip_frames == 0:
            # Redimensión para velocidad
            frame_rgb = cv2.cvtColor(cv2.resize(frame, (640, 480)), cv2.COLOR_BGR2RGB)
            results = pose.process(frame_rgb)

            if results.pose_landmarks:
                lm = results.pose_landmarks.landmark
                
                # FILTRO 1: Proximidad (Cámara trasera)
                shoulder_dist = geometry.calculate_distance([lm[11].x, lm[11].y], [lm[12].x, lm[12].y])
                
                if shoulder_dist > 0.12: # El jugador está cerca
                    
                    # FILTRO 2: Trigger de saque
                    knee_angle = geometry.calculate_angles(
                        [lm[23].x, lm[23].y], [lm[25].x, lm[25].y], [lm[27].x, lm[27].y]
                    )
                    
                    # Lanzamiento de bola (muñeca sobre hombro)
                    if knee_angle < 145 and lm[15].y < lm[11].y:
                        found_serves += 1
                        print(f"🎾 Saque detectado en min {round(frame_idx/(fps*60), 2)}")
                        
                        start_f = max(0, frame_idx - int(fps * 2))
                        end_f = frame_idx + int(fps * 3.5)
                        
                        save_clip(video_path, start_f, end_f, found_serves, width, height, fps)
                        
                        # Adelantar el puntero para no repetir el mismo saque
                        for _ in range(int(fps * 7)): 
                            cap.grab()
                            frame_idx += 1
                        continue

            # Progreso cada 10.000 frames
            if frame_idx % 10000 == 0:
                print(f"Progress: {round((frame_idx/total_frames)*100, 1)}%")

        frame_idx += 1

    cap.release()
    print(f"✅ Finalizado. Saques extraídos: {found_serves}")

def save_clip(video_path, start_f, end_f, serve_id, w, h, fps):
    # Abrimos una captura secundaria solo para el recorte
    c = cv2.VideoCapture(video_path)
    c.set(cv2.CAP_PROP_POS_FRAMES, start_f)
    
    out = cv2.VideoWriter(str(OUTPUT_DIR / f"saque_{serve_id}.mp4"), 
                         cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
    
    for _ in range(end_f - start_f):
        r, f = c.read()
        if not r: break
        out.write(f)
        
    out.release()
    c.release()

if __name__ == "__main__":
    auto_extract_serves(VIDEO_INPUT)