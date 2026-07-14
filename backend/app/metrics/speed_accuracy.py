import numpy as np


def compute_quadrant_for_answers(answers):
    """answers: list of {is_correct: bool, time_taken_seconds: float}."""
    times = [a["time_taken_seconds"] for a in answers]
    if not times:
        return None
    threshold = float(np.mean(times)) * 0.8

    fast_correct = fast_wrong = slow_correct = slow_wrong = 0
    for a in answers:
        is_fast = a["time_taken_seconds"] < threshold
        if is_fast and a["is_correct"]:
            fast_correct += 1
        elif is_fast and not a["is_correct"]:
            fast_wrong += 1
        elif not is_fast and a["is_correct"]:
            slow_correct += 1
        else:
            slow_wrong += 1

    return {
        "fast_correct": fast_correct, "fast_wrong": fast_wrong,
        "slow_correct": slow_correct, "slow_wrong": slow_wrong,
        "avg_time_seconds": round(float(np.mean(times)), 1),
    }