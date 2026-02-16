def validate_effect_metrics(effect_data):
    # 1. SALTO: Ajustado a la realidad de tus datos (Media ~10)
    # Eliminamos solo si es negativo real o absurdo (> 30)
    if effect_data['jump'] is not None:
        if effect_data['jump'] < -1.0 or effect_data['jump'] > 30.0:
            return None, f"(Irreal jump: {effect_data['jump']})"
    
    # 2. LÁTIGO: Este elimina el vídeo 149 que tiene valor 16.9
    if effect_data['lateral_offset'] is not None:
        if abs(effect_data['lateral_offset']) > 4.0:
            return None, f"(Offset without sense: {effect_data['lateral_offset']})"
    
    # 3. BRAZO: Elimina los 3 vídeos con ángulos < 45º
    if effect_data['arm_extension'] is not None:
        if effect_data['arm_extension'] > 185 or effect_data['arm_extension'] < 45:
            return None, f"(Imposible arm: {effect_data['arm_extension']})"
        
    return True, ""

def validate_knee_integrity(angles, min_f, csv_path):
    if angles[min_f] < 45:
        print(f"Discard {csv_path.name} Impossible Knee Angle {round(angles[min_f], 2)}º")
        return False

    return True
