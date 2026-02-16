import pandas as pd
import numpy as np
import joblib  # Para guardar los modelos
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, f1_score, confusion_matrix

# --- CONFIGURACIÓN ---
CSV_FILE = Path("train_dataset.csv")
MODEL_DIR = Path("models_output")
MODEL_DIR.mkdir(exist_ok=True)

# 1. CARGAR DATOS
print(f"Cargando {CSV_FILE}...")
df = pd.read_csv(CSV_FILE)

# Confirmamos distribución
print("Distribución Stance:", df['stance_label'].value_counts().to_dict())
print("Distribución Effect:", df['effect_label'].value_counts().to_dict())

# --- DEFINICIÓN DE LOS DOS EXPERTOS (FEATURE SELECTION) ---
# Aquí es donde ocurre la magia: cada modelo ve solo lo que necesita.

# Experto 1: STANCE (Solo mira pies y cadera)
# Nota: ankle_min_dist es clave para Pinpoint
FEATURES_STANCE = ['ankle_drag', 'ankle_min_dist', 'hip_tilt']

# Experto 2: EFECTO (Solo mira salto y golpeo)
# Nota: lateral_offset es clave para Kick vs Slice
FEATURES_EFFECT = ['jump', 'lateral_offset', 'arm_extension']

# --- MOTOR DE ENTRENAMIENTO ---
def entrenar_torneo(target_name, target_col, feature_cols, class_names):
    print(f"\n{'='*60}")
    print(f"🎾 ENTRENANDO EXPERTO EN: {target_name.upper()}")
    print(f"{'='*60}")
    print(f"Variables de entrada: {feature_cols}")
    
    # 1. Preparar datos
    X = df[feature_cols]
    y = df[target_col]
    
    # 2. Dividir (80% entrenar, 20% examen)
    # Stratify asegura que haya el mismo % de Kicks en train y test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 3. Escalar (Normalizar datos)
    # FUNDAMENTAL: El SVM falla si no escalas (porque 170 grados es > 0.5 distancia)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 4. Definir concursantes
    modelos = {
        "SVM": SVC(kernel='rbf', C=1.0, class_weight='balanced', probability=True, random_state=42),
        "RandomForest": RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42),
        "KNN (Vecinos)": KNeighborsClassifier(n_neighbors=5)
    }
    
    best_score = 0
    best_model = None
    best_name = ""
    
    print("\n--- Resultados del Torneo ---")
    for nombre, modelo in modelos.items():
        # Entrenar
        modelo.fit(X_train_scaled, y_train)
        
        # Predecir examen
        y_pred = modelo.predict(X_test_scaled)
        
        # Evaluar (Usamos F1-Score Weighted porque tus clases están desbalanceadas)
        score = f1_score(y_test, y_pred, average='weighted')
        print(f"--> {nombre}: F1 Score = {score:.4f}")
        
        if score > best_score:
            best_score = score
            best_model = modelo
            best_name = nombre

    print(f"\n🏆 GANADOR: {best_name} (F1={best_score:.4f})")
    
    # 5. Reporte final del ganador
    y_final_pred = best_model.predict(X_test_scaled)
    print("\nReporte Detallado:")
    print(classification_report(y_test, y_final_pred, target_names=class_names))
    
    # 6. Guardar Modelo y Scaler (Importante guardar el scaler también!)
    # Guardamos con nombres claros para la app final
    joblib.dump(best_model, MODEL_DIR / f"model_{target_name}.pkl")
    joblib.dump(scaler, MODEL_DIR / f"scaler_{target_name}.pkl")
    print(f"💾 Guardado en: model_{target_name}.pkl y scaler_{target_name}.pkl")

# --- EJECUCIÓN ---

# 1. Entrenar Stance
entrenar_torneo(
    target_name="stance",
    target_col="stance_label",
    feature_cols=FEATURES_STANCE,
    class_names=["Pinpoint", "Platform"] # 0, 1
)

# 2. Entrenar Efecto
entrenar_torneo(
    target_name="effect",
    target_col="effect_label",
    feature_cols=FEATURES_EFFECT,
    class_names=["Flat", "Kick", "Slice"] # 0, 1, 2
)