import numpy as np
from sqlalchemy import select
from app.db import engine, metadata

quiz_attempts_t = metadata.tables["quiz_attempts"]
quizzes_t = metadata.tables["quizzes"]
student_answers_t = metadata.tables["student_answers"]

IMPROVEMENT_SCALE = 5.0  # a ±5 point swing between quizzes maps to the full 0-1 range


def _fetch_attempts_for_student_course(conn, student_id, course_id):
    stmt = (
        select(
            quiz_attempts_t.c.id,
            quiz_attempts_t.c.total_score,
            quiz_attempts_t.c.created_at,
            quizzes_t.c.total_marks,
        )
        .join(quizzes_t, quizzes_t.c.id == quiz_attempts_t.c.quiz_id)
        .where(
            quiz_attempts_t.c.student_id == student_id,
            quizzes_t.c.course_id == course_id,
        )
        .order_by(quiz_attempts_t.c.created_at)
    )
    rows = conn.execute(stmt).mappings().all()
    return [
        {
            "id": r["id"],
            "total_score": float(r["total_score"]),
            "created_at": r["created_at"],
            "total_marks": float(r["total_marks"]),
        }
        for r in rows
    ]


def _fetch_answer_timings(conn, attempt_ids):
    if not attempt_ids:
        return []
    stmt = select(
        student_answers_t.c.attempt_id,
        student_answers_t.c.is_correct,
        student_answers_t.c.time_taken_seconds,
    ).where(student_answers_t.c.attempt_id.in_(attempt_ids))
    rows = conn.execute(stmt).mappings().all()
    return [
        {
            "attempt_id": r["attempt_id"],
            "is_correct": r["is_correct"],
            "time_taken_seconds": float(r["time_taken_seconds"]),
        }
        for r in rows
    ]


def _compute_accuracy(attempts):
    ratios = [a["total_score"] / a["total_marks"] for a in attempts if a["total_marks"]]
    return float(np.mean(ratios)) if ratios else 0.0


def _compute_improvement(attempts):
    # Last 5 attempts, ordered chronologically — see point 3 above for why
    # this isn't attempt_number.
    recent = attempts[-5:]
    if len(recent) < 2:
        return 0.5  # not enough history yet — neutral
    scores = [a["total_score"] for a in recent]
    x = np.arange(len(scores))
    slope = float(np.polyfit(x, scores, 1)[0])
    normalized = (slope + IMPROVEMENT_SCALE) / (2 * IMPROVEMENT_SCALE)
    return float(np.clip(normalized, 0.0, 1.0))


def _compute_speed_efficiency(conn, attempts):
    # Same fast/slow split M3 will use later (time < 0.8x that attempt's own
    # average), computed inline so M1 doesn't have to wait on M3's table —
    # see point 1 above.
    attempt_ids = [a["id"] for a in attempts]
    answers = _fetch_answer_timings(conn, attempt_ids)
    if not answers:
        return 0.0

    by_attempt = {}
    for ans in answers:
        by_attempt.setdefault(ans["attempt_id"], []).append(ans)

    fast_correct = fast_wrong = slow_wrong = 0
    for group in by_attempt.values():
        times = [a["time_taken_seconds"] for a in group]
        threshold = float(np.mean(times)) * 0.8
        for a in group:
            is_fast = a["time_taken_seconds"] < threshold
            if is_fast and a["is_correct"]:
                fast_correct += 1
            elif is_fast and not a["is_correct"]:
                fast_wrong += 1
            elif not is_fast and not a["is_correct"]:
                slow_wrong += 1
            # slow_correct is deliberately excluded — that's what the
            # implementation plan's denominator specifies

    denom = fast_correct + fast_wrong + slow_wrong
    return fast_correct / denom if denom else 0.0


def _compute_consistency(attempts):
    scores = [a["total_score"] for a in attempts]
    total_marks = attempts[0]["total_marks"] if attempts else 1
    if len(scores) < 2 or not total_marks:
        return 1.0  # not enough attempts to measure volatility yet
    consistency = 1 - (np.std(scores) / total_marks)
    return float(np.clip(consistency, 0.0, 1.0))


def compute_composite_score(conn, student_id, course_id):
    attempts = _fetch_attempts_for_student_course(conn, student_id, course_id)
    if not attempts:
        return None

    accuracy = _compute_accuracy(attempts)
    improvement = _compute_improvement(attempts)
    speed_efficiency = _compute_speed_efficiency(conn, attempts)
    consistency = _compute_consistency(attempts)

    raw = 0.40 * accuracy + 0.25 * improvement + 0.20 * speed_efficiency + 0.15 * consistency
    composite = float(np.clip(raw * 100, 0.0, 100.0))

    return {
        "composite_score": round(composite, 2),
        "accuracy": round(accuracy, 3),
        "improvement": round(improvement, 3),
        "speed_efficiency": round(speed_efficiency, 3),
        "consistency": round(consistency, 3),
    }


def band_label_for(composite_score):  # M2 — straight from the doc's thresholds
    if composite_score <= 30:
        return "Needs Improvement"
    elif composite_score <= 50:
        return "Developing"
    elif composite_score <= 65:
        return "Proficient"
    elif composite_score <= 80:
        return "Strong"
    else:
        return "Excellent"