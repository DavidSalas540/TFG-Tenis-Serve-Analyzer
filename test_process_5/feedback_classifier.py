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

JUMP_LOW       = 4.8    # P10
JUMP_MODERATE  = 6.0    # P25
JUMP_OPTIMAL   = 10.6   # P75

SHOULDER_LOW      = 10.0   # abs < 10 → low X-factor → score 1
SHOULDER_MODERATE = 25.0   # abs < 25 → moderate → score 4
SHOULDER_GOOD     = 40.0   # abs < 40 → good → score 7
                            # abs ≥ 40 → excellent → score 10

ARM_VERY_BENT  = 150.0
ARM_MODERATE   = 165.0
ARM_GOOD       = 175.0

NON_DOM_LOW    = 165.0   # 160-165 transition (already filtered < 160)
NON_DOM_OPT   = 180.0    # 165-180 optimal

TRUNK_LOW      = 1.0
TRUNK_MODERATE = 2.0
TRUNK_GOOD     = 4.0

# ─── Metric weights for the meta-formula ────────────────────────────────────
# Power mechanics weighted higher than supporting metrics.

WEIGHTS = {
    'knee_loading':         2.0,
    'hip_drive':            2.0,
    'jump':                 2.0,
    'shoulder_rotation':    1.5,
    'arm_extension':        1.5,
    'non_dominant_arm':     1.5,
    'trunk_arch':           1.0,
}


# ─── Individual classifiers ──────────────────────────────────────────────────

def classify_knee_loading(knee_min):
    """Classifies knee flexion depth at maximum loading phase."""
    if knee_min < KNEE_DEEP:
        return {
            'category': 'Carga profunda',
            'score': 10,
            'tip': 'Carga de rodillas excelente — máxima energía elástica disponible.',
        }
    if knee_min < KNEE_OPTIMAL:
        return {
            'category': 'Carga óptima',
            'score': 7,
            'tip': 'Buena carga. Intenta profundizar un poco más para ganar potencia vertical.',
        }
    if knee_min < KNEE_MODERATE:
        return {
            'category': 'Carga moderada',
            'score': 4,
            'tip': 'La carga es insuficiente. Flexiona más las rodillas durante la fase de carga.',
        }
    return {
        'category': 'Carga insuficiente',
        'score': 1,
        'tip': 'Rodillas casi rectas durante la carga. Trabaja la flexión para generar impulso.',
    }


def classify_hip_drive(hip_drive):
    """Classifies horizontal hip projection from start to loading phase."""
    if hip_drive < HIP_DRIVE_LOW:
        return {
            'category': 'Impulso insuficiente',
            'score': 1,
            'tip': 'Las caderas apenas se proyectan hacia adelante. Trabaja el arco de cadera.',
        }
    if hip_drive < HIP_DRIVE_MODEST:
        return {
            'category': 'Impulso modesto',
            'score': 4,
            'tip': 'Proyección de caderas por debajo de la media. Empuja más las caderas al frente.',
        }
    if hip_drive < HIP_DRIVE_GOOD:
        return {
            'category': 'Impulso bueno',
            'score': 7,
            'tip': 'Buen empuje de caderas. Estás usando bien el cuerpo como palanca.',
        }
    return {
        'category': 'Impulso agresivo',
        'score': 10,
        'tip': 'Proyección de caderas excelente — estás generando máxima potencia elástica.',
    }


def classify_jump(jump):
    """Classifies vertical jump height normalized by hip width."""
    if jump < JUMP_LOW:
        return {
            'category': 'Despegue bajo',
            'score': 1,
            'tip': 'El salto es muy bajo. Trabaja la extensión de piernas en el impulso.',
        }
    if jump < JUMP_MODERATE:
        return {
            'category': 'Despegue moderado',
            'score': 4,
            'tip': 'Salto por debajo de la media. Intenta coordinar mejor la carga con el despegue.',
        }
    if jump < JUMP_OPTIMAL:
        return {
            'category': 'Despegue óptimo',
            'score': 7,
            'tip': 'Buen despegue. Estás aprovechando bien la energía de la carga.',
        }
    return {
        'category': 'Despegue explosivo',
        'score': 10,
        'tip': 'Despegue excelente — potencia vertical de élite.',
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
            'tip': 'Poca separación entre hombros y caderas. Trabaja la rotación del tronco.',
        }
    if magnitude < SHOULDER_MODERATE:
        return {
            'category': 'Rotación moderada',
            'score': 4,
            'tip': 'X-factor moderado. Intenta mantener los hombros cerrados mientras las caderas rotan.',
        }
    if magnitude < SHOULDER_GOOD:
        return {
            'category': 'Buena rotación',
            'score': 7,
            'tip': 'Buena separación hombros/caderas. Estás acumulando energía rotacional correctamente.',
        }
    return {
        'category': 'Rotación excelente',
        'score': 10,
        'tip': 'X-factor excelente — máxima acumulación de energía rotacional.',
    }


def classify_arm_extension(arm_extension):
    """Classifies dominant arm extension at ball impact."""
    if arm_extension < ARM_VERY_BENT:
        return {
            'category': 'Codo muy cerrado',
            'score': 1,
            'tip': 'El codo está demasiado flexionado en el impacto. Extiende más el brazo al golpear.',
        }
    if arm_extension < ARM_MODERATE:
        return {
            'category': 'Extensión moderada',
            'score': 4,
            'tip': 'Brazo no completamente extendido. Trabaja la extensión total en el punto de contacto.',
        }
    if arm_extension < ARM_GOOD:
        return {
            'category': 'Buena extensión',
            'score': 7,
            'tip': 'Buena extensión de brazo. Cerca del óptimo biomecánico.',
        }
    return {
        'category': 'Extensión completa',
        'score': 10,
        'tip': 'Brazo totalmente extendido en el impacto — técnica correcta.',
    }


def classify_non_dominant_arm(angle):
    """Classifies non-dominant arm elevation at trophy position."""
    if angle < NON_DOM_LOW:
        return {
            'category': 'Transición',
            'score': 5,
            'tip': 'El brazo no dominante está por debajo del ideal. Súbelo más hacia la "plomada virtual".',
        }
    return {
        'category': 'Óptimo',
        'score': 10,
        'tip': 'Posición del brazo no dominante correcta — buena referencia de altura de impacto.',
    }


def classify_trunk_arch(trunk_arch):
    """Classifies body bow shape (hip center vs shoulder center projection)."""
    if trunk_arch < TRUNK_LOW:
        return {
            'category': 'Arco mínimo',
            'score': 3,
            'tip': 'Poca proyección de cadera respecto a los hombros. Trabaja el arco corporal.',
        }
    if trunk_arch < TRUNK_MODERATE:
        return {
            'category': 'Arco moderado',
            'score': 5,
            'tip': 'Arco corporal moderado. Hay margen para mejorar la proyección de caderas.',
        }
    if trunk_arch < TRUNK_GOOD:
        return {
            'category': 'Buen arco',
            'score': 8,
            'tip': 'Buen arco corporal. Las caderas están bien proyectadas respecto a los hombros.',
        }
    return {
        'category': 'Arco pronunciado',
        'score': 10,
        'tip': 'Arco corporal excelente — muy buena proyección de caderas.',
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
):
    """
    Runs all metric classifiers and computes the overall serve quality score.

    Returns a dict with:
      - 'total_score'  : float 0-100
      - 'grade'        : letter grade (A/B/C/D)
      - 'breakdown'    : dict of per-metric results
    """
    breakdown = {
        'knee_loading':      classify_knee_loading(knee_min),
        'hip_drive':         classify_hip_drive(hip_drive),
        'jump':              classify_jump(jump),
        'shoulder_rotation': classify_shoulder_rotation(shoulder_rotation),
        'arm_extension':     classify_arm_extension(arm_extension),
        'non_dominant_arm':  classify_non_dominant_arm(non_dominant_arm_angle),
        'trunk_arch':        classify_trunk_arch(trunk_arch),
    }

    weighted_sum = sum(
        breakdown[key]['score'] * WEIGHTS[key]
        for key in WEIGHTS
    )
    max_possible = sum(10 * w for w in WEIGHTS.values())
    total_score  = round((weighted_sum / max_possible) * 100, 1)

    if total_score >= 80:
        grade = 'A'
    elif total_score >= 65:
        grade = 'B'
    elif total_score >= 50:
        grade = 'C'
    else:
        grade = 'D'

    return {
        'total_score': total_score,
        'grade':       grade,
        'breakdown':   breakdown,
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
