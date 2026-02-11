from geometry import *
from scipy.signal import find_peaks

def detectar_fases_saque(angulos, max_dist_frames=200):
   
    data = np.array(angulos)
    
    # 1. Búsqueda de Candidatos (Picos y Valles)
    picos_idx, _ = find_peaks(data, height=150, distance=20)   # Extensión
    valles_idx, _ = find_peaks(-data, height=-165, distance=20) # Flexión
    
    # 2. Selección de la Mejor Pareja (Mayor Rango Ascendente)
    best_score, best_min, best_max = -1, -1, -1
    
    for valle in valles_idx:
        for pico in picos_idx:
            # Lógica temporal: Valle debe ir antes que Pico
            if valle < pico:
                if (pico - valle) < max_dist_frames:
                    recorrido = data[pico] - data[valle]
                    # Maximizamos la subida (ROM)
                    if recorrido > best_score:
                        best_score = recorrido
                        best_min = valle
                        best_max = pico
    
    # Fallback de seguridad
    if best_min == -1: 
        best_min, best_max = np.argmin(data), np.argmax(data)
        
    # 3. Refinamiento del Mínimo (Lupa local)
    ventana = 10
    ini, end = max(0, best_min - ventana), min(len(data), best_min + ventana)
    best_min = ini + np.argmin(data[ini:end])
    
    # 4. Cálculo del Target Frame (Factor 0.325)
    # Punto de máxima inercia antes del despegue
    target = int(best_min + (best_max - best_min) * 0.325)
    
    # 5. Búsqueda del Inicio (Punto Morado)
    # Miramos hacia atrás buscando la posición erguida previa
    s_search = max(0, best_min - 150)
    pre_data = data[s_search:best_min]
    start = s_search + np.argmax(pre_data) if len(pre_data) > 0 else 0
    
    return start, best_min, best_max, target