"""
feedback_classifier.py — Serve quality feedback system
=======================================================
Classifies each biomechanical metric into categories and assigns a score.
The aggregate function produces an overall serve quality score (0-100)
with a per-metric breakdown and improvement tips.

This module is designed for the user-facing backend — it never discards
a video. Every input gets a classification and a tip, regardless of value.

Score scale per metric: 0-10
  10 = optimal / elite
   7 = good
   4 = moderate, room for improvement
   1 = needs significant work

Meta-formula: weighted average of all metric scores → scaled to 0-100.
"""

# ─── Thresholds (derived from the training dataset distribution) ────────────

KNEE_DEEP      = 120.0   # < deep → score 10
KNEE_OPTIMAL   = 135.0   # < optimal → score 7
KNEE_MODERATE  = 145.0   # < moderate → score 4
                          # ≥ 145 → insuficient → score 1

HIP_DRIVE_LOW      = 1.0    # < low → score 1
HIP_DRIVE_MODEST   = 2.0    # < modest → score 4
HIP_DRIVE_GOOD     = 5.0    # < good → score 7
                             # ≥ 5 → aggressive → score 10

JUMP_LOW       = 4.0    # < low  → score 1  (~4% del dataset)
JUMP_MODERATE  = 7.0    # < mod  → score 4  (~20%)
JUMP_OPTIMAL   = 11.0   # < opt  → score 7  (~45%)  |  ≥ 11 → agresivo → score 10 (~30%)

SHOULDER_LOW      = 10.0   # abs < 10 → low X-factor → score 1
SHOULDER_MODERATE = 25.0   # abs < 25 → moderate → score 4
SHOULDER_GOOD     = 40.0   # abs < 40 → good → score 7
                            # abs ≥ 40 → excellent → score 10

ARM_VERY_BENT  = 150.0
ARM_MODERATE   = 165.0
ARM_GOOD       = 175.0

NON_DOM_LOW    = 165.0   # < 165 → malo      → score 1  (~3%)
NON_DOM_MED    = 170.0   # < 170 → moderado  → score 4  (~21%)
NON_DOM_GOOD   = 176.0   # < 176 → bueno     → score 7  (~36%)  |  ≥ 176 → excelente → score 10 (~39%)

TRUNK_LOW      = 1.0
TRUNK_MODERATE = 2.0
TRUNK_GOOD     = 4.0

# ─── Metric weights for the meta-formula ────────────────────────────────────
# Power mechanics weighted higher than supporting metrics.

WEIGHTS = {
    'knee_loading':         2.0,
    'hip_drive':            2.0,
    'jump':                 1.5,
    'shoulder_rotation':    2.0,
    'arm_extension':        1.5,
    'non_dominant_arm':     1.5,
    'trunk_arch':           1.0,
}

# ─── Level-based metric progression ─────────────────────────────────────────

LEVEL_METRICS = {
    1: {'arm_extension', 'non_dominant_arm'},
    2: {'arm_extension', 'non_dominant_arm', 'knee_loading'},
    3: {'arm_extension', 'non_dominant_arm', 'knee_loading', 'hip_drive', 'trunk_arch'},
    4: {'arm_extension', 'non_dominant_arm', 'knee_loading', 'hip_drive', 'trunk_arch', 'shoulder_rotation'},
    5: {'arm_extension', 'non_dominant_arm', 'knee_loading', 'hip_drive', 'trunk_arch', 'shoulder_rotation', 'jump'},
}

LEVEL_NAMES = {
    1: 'Iniciación',
    2: 'Básico',
    3: 'Intermedio',
    4: 'Avanzado',
    5: 'Competición',
}

# Grade thresholds scale with level: beginners reach A/B with lower absolute scores.
# At level 5 (Competition) the bar matches elite standards (A≥80, B≥65, C≥50).
LEVEL_GRADES = {
    1: {'A': 65, 'B': 50, 'C': 35},
    2: {'A': 68, 'B': 53, 'C': 38},
    3: {'A': 72, 'B': 57, 'C': 42},
    4: {'A': 76, 'B': 61, 'C': 46},
    5: {'A': 80, 'B': 65, 'C': 50},
}

_LOCKED = {
    'category': 'No evaluado',
    'score':    0,
    'tip':      'Esta métrica se desbloquea en un nivel superior. ¡Sigue practicando!',
    'active':   False,
}


# CLASIFIERS
def classify_knee_loading(knee_min):
    """Classifies knee flexion depth at maximum loading phase."""
    if knee_min <= KNEE_DEEP:
        return {
            'category': 'Flexión profunda',
            'score': 10,
            'tip': 'Flexión de rodillas excelente! máxima energía elástica disponible, ¡buen trabajo!.',
        }
    if knee_min <= KNEE_OPTIMAL:
        return {
            'category': 'Flexión óptima',
            'score': 7,
            'tip': '¡Buena flexión de rodillas!. ¡Aún se puede flexionar un poco más! Si por problemas de rodillas o tu propia técnica no quieres/puedes, la flexión sigue siendo correcta.',
        }
    if knee_min <= KNEE_MODERATE:
        return {
            'category': 'Flexión moderada',
            'score': 4,
            'tip': 'Flexión de rodillas insuficiente. ¡Una mayor flexión de rodillas durante la fase de carga, generará mayor potencia!.',
        }
    return {
        'category': 'Flexión insuficiente',
        'score': 1,
        'tip': 'Apenas existe flexión de Rodillas. ¡Si flexionas durante la fase de carga, lograrás más impulso!.',
    }

def classify_jump(jump):
    """Classifies vertical jump height normalized by hip width."""
    if jump < JUMP_LOW:
        return {
            'category': 'Salto nulo',
            'score': 1,
            'tip': 'El salto es prácticamente inexistente. Un pequeño salto te ayudaría a mejorar la explosividad del saque.',
        }
    if jump < JUMP_MODERATE:
        return {
            'category': 'Salto aceptable',
            'score': 4,
            'tip': 'Salto por debajo de la media. Intenta saltar un poco más sin perder la coordinación.',
        }
    if jump < JUMP_OPTIMAL:
        return {
            'category': 'Salto óptimo',
            'score': 7,
            'tip': '¡Buen salto!. Estás aprovechando bien la energía del salto.',
        }
    return {
        'category': 'Salto agresivo',
        'score': 10,
        'tip': '¡Salto excelente! Buena coordinación. CUIDADO: Si no coordinas el resto de las articulaciones y saltas de manera agresiva, aumentará el riesgo de lesión.',
    }

def classify_arm_extension(arm_extension):
    """Classifies dominant arm extension at ball impact."""
    if arm_extension < ARM_VERY_BENT:
        return {
            'category': 'Codo muy cerrado',
            'score': 1,
            'tip': 'El codo está muy doblado en el golpe. ¡Debes estirar el brazo al impactar la pelota!',
        }
    if arm_extension < ARM_MODERATE:
        return {
            'category': 'Extensión moderada',
            'score': 4,
            'tip': 'El brazo no llega a estirarse del todo. ¡Trabaja la extensión final al soltar el golpe!',
        }
    if arm_extension < ARM_GOOD:
        return {
            'category': 'Buena extensión',
            'score': 7,
            'tip': '¡Buena extensión de brazo!. Le falta poco para llegar al máximo.',
        }
    return {
        'category': 'Extensión perfecta',
        'score': 10,
        'tip': '¡Extensión perfecta para el impacto!',
    }


def classify_non_dominant_arm(angle):
    """Classifies non-dominant arm elevation at trophy position."""
    if angle < NON_DOM_LOW:
        return {
            'category': 'Posición baja',
            'score': 1,
            'tip': '¡El brazo no dominante de lanzamiento de bola (Toss) está por debajo del ideal! Mantenlo arriba hasta el golpe.',
        }
    if angle < NON_DOM_MED:
        return {
            'category': 'Posición moderada',
            'score': 4,
            'tip': 'El brazo no dominante de lanzamiento de bola (Toss) puede subir bastante más. Intenta mantenerlo elevado durante toda la fase de carga.',
        }
    if angle < NON_DOM_GOOD:
        return {
            'category': 'Buena posición',
            'score': 7,
            'tip': '¡Buena elevación del brazo no dominante! Intenta mantenerlo un poco más arriba hasta el momento del golpe.',
        }
    return {
        'category': 'Posición correcta',
        'score': 10,
        'tip': '¡El brazo no dominante de lanzamiento de bola (Toss) está perfecto!',
    }

def classify_hip_drive(hip_drive):
    """Classifies horizontal hip projection from start to loading phase."""
    if hip_drive < HIP_DRIVE_LOW:
        return {
            'category': 'Impulso insuficiente',
            'score': 1,
            'tip': '¡Proyección inexistente! Las caderas apenas se proyectan hacia adelante.',
        }
    if hip_drive < HIP_DRIVE_MODEST:
        return {
            'category': 'Impulso modesto',
            'score': 4,
            'tip': '¡Proyección de caderas por debajo de la media! Empuja más las caderas al frente.',
        }
    if hip_drive < HIP_DRIVE_GOOD:
        return {
            'category': 'Impulso bueno',
            'score': 7,
            'tip': '¡Buen empuje de caderas! Estás usando bien el cuerpo como palanca.',
        }
    return {
        'category': 'Impulso agresivo',
        'score': 10,
        'tip': '¡Proyección de caderas excelente! estás generando máxima potencia elástica. CUIDADO: Si no coordinas el resto del cuerpo, proyectar asiladamente la cadera puede aumentar el    riesgo de lesión',
    }

def classify_shoulder_rotation(rotation):
    """
    Classifies X-factor: shoulder/hip angular separation at trophy position.
    Uses absolute value — larger = more coil = more stored energy.
    """
    magnitude = abs(rotation)
    if magnitude < SHOULDER_LOW:
        return {
            'category': 'Rotación insuficiente',
            'score': 1,
            'tip': 'Apenas giras el tronco. Lleva el hombro derecho hacia atrás durante el momento de carga.',
        }
    if magnitude < SHOULDER_MODERATE:
        return {
            'category': 'Rotación moderada',
            'score': 4,
            'tip': 'Falta giro. En la posición de trofeo, el hombro derecho debe quedar más retrasado que la cadera.',
        }
    if magnitude < SHOULDER_GOOD:
        return {
            'category': 'Buena rotación',
            'score': 7,
            'tip': '¡Buen giro!. Abre caderas un poco antes de soltar los hombros para ganar más velocidad.',
        }
    return {
        'category': 'Rotación excelente',
        'score': 10,
        'tip': '¡Excelente giro de tronco!',
    }

def classify_trunk_arch(trunk_arch):
    """Classifies body bow shape (hip center vs shoulder center projection)."""
    if trunk_arch < TRUNK_LOW:
        return {
            'category': 'Arco mínimo',
            'score': 1,
            'tip': 'Las caderas no se adelantan a los hombros. Empuja las caderas hacia la red al subir el brazo.',
        }
    if trunk_arch < TRUNK_MODERATE:
        return {
            'category': 'Arco moderado',
            'score': 4,
            'tip': 'Poca separación entre caderas y hombros. Intenta que las caderas lleguen antes que el brazo.',
        }
    if trunk_arch < TRUNK_GOOD:
        return {
            'category': 'Buen arco',
            'score': 7,
            'tip': 'Buen arco corporal. Las caderas van por delante de los hombros correctamente.',
        }
    return {
        'category': 'Arco pronunciado',
        'score': 10,
        'tip': 'Muy buen arco. Las caderas se proyectan bien hacia adelante. Mantenlo.',
    }


# ─── Aggregate function ──────────────────────────────────────────────────────

def classify_serve(
    knee_min,
    hip_drive,
    jump,
    shoulder_rotation,
    arm_extension,
    non_dominant_arm_angle,
    trunk_arch,
    nivel=5,
):
    """
    Runs all metric classifiers and computes the overall serve quality score.
    Only metrics unlocked at `nivel` contribute to the score; the rest are
    marked as inactive and shown as locked in the UI.

    Returns a dict with:
      - 'total_score'  : float 0-100 (based only on active metrics)
      - 'grade'        : letter grade (A/B/C/D)
      - 'breakdown'    : dict of per-metric results (all 7 metrics)
      - 'nivel'        : the level used for scoring
    """
    active = LEVEL_METRICS.get(nivel, LEVEL_METRICS[5])

    raw = {
        'knee_loading':      classify_knee_loading(knee_min),
        'hip_drive':         classify_hip_drive(hip_drive),
        'jump':              classify_jump(jump),
        'shoulder_rotation': classify_shoulder_rotation(shoulder_rotation),
        'arm_extension':     classify_arm_extension(arm_extension),
        'non_dominant_arm':  classify_non_dominant_arm(non_dominant_arm_angle),
        'trunk_arch':        classify_trunk_arch(trunk_arch),
    }

    breakdown = {
        key: ({**result, 'active': True} if key in active else dict(_LOCKED))
        for key, result in raw.items()
    }

    weighted_sum = sum(
        float(raw[key]['score']) * WEIGHTS[key]
        for key in active if key in WEIGHTS
    )
    max_possible = sum(WEIGHTS[key] for key in active if key in WEIGHTS)
    total_score  = round((weighted_sum / max_possible) * 10, 1) if max_possible else 0.0

    thresholds = LEVEL_GRADES.get(nivel, LEVEL_GRADES[5])
    if total_score >= thresholds['A']:
        grade = 'A'
    elif total_score >= thresholds['B']:
        grade = 'B'
    elif total_score >= thresholds['C']:
        grade = 'C'
    else:
        grade = 'D'

    return {
        'total_score': total_score,
        'grade':       grade,
        'breakdown':   breakdown,
        'nivel':       nivel,
    }


def print_report(result):
    """Prints a human-readable feedback report from classify_serve output."""
    print(f"\n{'='*50}")
    print(f"  SERVE QUALITY SCORE: {result['total_score']}/100  [{result['grade']}]")
    print(f"{'='*50}")
    for key, data in result['breakdown'].items():
        print(f"\n  {key.upper().replace('_', ' ')}")
        print(f"    Category : {data['category']}")
        print(f"    Score    : {data['score']}/10")
        print(f"    Tip      : {data['tip']}")
    print(f"\n{'='*50}\n")
