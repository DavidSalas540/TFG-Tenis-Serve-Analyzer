"""
quality_checks.py — Training pipeline filters
==============================================
Validates that extracted biomechanical metrics are within plausible ranges
before adding a video to the training dataset. Videos that fail any check
are discarded entirely — they contain either impossible values or MediaPipe
tracking errors that would corrupt the model.

IMPORTANT: These filters are for training only.
In the backend (user-facing product), never discard — classify instead.
Use a separate feedback_classifier module for that purpose.

Return convention
-----------------
- validate_effect_metrics  → (bool, str)  — tuple with reason on failure
- All other validators     → bool         — False = discard, True = keep

Thresholds
----------
JUMP_MIN / JUMP_MAX         : jump height in hip-width units. Values outside
                              this range indicate detection errors (e.g. body
                              not detected during takeoff).
LATERAL_OFFSET_MAX          : wrist-to-shoulder horizontal offset at impact.
                              Values > 4 HW are physically unreachable.
ARM_EXTENSION_MIN/MAX       : elbow angle at impact. < 45° or > 185° means
                              MediaPipe placed a joint in an impossible position.
KNEE_ANGLE_MIN              : knee angle at maximum flexion. < 45° is anatomically
                              impossible and indicates tracking failure.
NON_DOM_ARM_MIN / MAX       : non-dominant arm wrist-shoulder-hip angle at trophy
                              position. < 160° means poor technique or detection
                              error — excluded from training to avoid noise.
HIP_DRIVE_MIN               : horizontal hip displacement from start to loading.
                              Negative = hip moved backwards, which is physically
                              impossible and signals a tracking glitch.
SHOULDER_ROTATION_MAX       : absolute angle difference between shoulder and hip
                              axes. > 90° is anatomically impossible in a serve
                              and indicates a joint was misplaced by MediaPipe.
TRUNK_ARCH_MAX              : hip-center to shoulder-center horizontal offset
                              normalized by hip_width. > 8 HW is physically
                              impossible and indicates a tracking error.
"""

JUMP_MIN               = -1.0
JUMP_MAX               = 30.0
LATERAL_OFFSET_MAX     = 4.0
ARM_EXTENSION_MIN      = 45.0
ARM_EXTENSION_MAX      = 185.0
KNEE_ANGLE_MIN         = 45.0
NON_DOM_ARM_MIN        = 160.0
NON_DOM_ARM_MAX        = 190.0
HIP_DRIVE_MIN          = 0.0
SHOULDER_ROTATION_MAX  = 90.0
TRUNK_ARCH_MAX         = 8.0


def validate_effect_metrics(effect_data):

    if effect_data['jump'] is not None:
        if not (JUMP_MIN <= effect_data['jump'] <= JUMP_MAX):
            return False, f"Unrealistic jump: {effect_data['jump']}"

    if effect_data['lateral_offset'] is not None:
        if abs(effect_data['lateral_offset']) > LATERAL_OFFSET_MAX:
            return False, f"Unrealistic lateral offset: {effect_data['lateral_offset']}"

    if effect_data['arm_extension'] is not None:
        if not (ARM_EXTENSION_MIN <= effect_data['arm_extension'] <= ARM_EXTENSION_MAX):
            return False, f"Impossible arm extension: {effect_data['arm_extension']}"

    return True, ""


def validate_knee_integrity(angles, min_f, csv_path):

    if angles[min_f] < KNEE_ANGLE_MIN:
        print(f"Discarded {csv_path.name}: impossible knee angle {round(angles[min_f], 2)}°")
        return False
    return True


def validate_non_dominant_arm_angle(angle, csv_path):

    if not (NON_DOM_ARM_MIN <= angle <= NON_DOM_ARM_MAX):
        print(f"Discarded {csv_path.name}: non-dominant arm angle {angle}° "
              f"out of range [{NON_DOM_ARM_MIN}, {NON_DOM_ARM_MAX}]")
        return False
    return True


def validate_hip_drive(hip_drive, csv_path):

    if hip_drive < HIP_DRIVE_MIN:
        print(f"Discarded {csv_path.name}: negative hip drive ({hip_drive})")
        return False
    return True


def validate_shoulder_rotation(rotation, csv_path):

    if abs(rotation) > SHOULDER_ROTATION_MAX:
        print(f"Discarded {csv_path.name}: impossible shoulder rotation ({rotation}°)")
        return False
    return True


def validate_trunk_arch(arch, csv_path):

    if arch > TRUNK_ARCH_MAX:
        print(f"Discarded {csv_path.name}: impossible trunk arch ({arch} HW)")
        return False
    return True
