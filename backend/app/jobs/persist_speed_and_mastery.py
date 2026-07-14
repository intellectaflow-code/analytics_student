import time
from collections import defaultdict
import numpy as np
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.db import engine, metadata
from app.metrics.speed_accuracy import compute_quadrant_for_answers

quiz_attempts_t = metadata.tables["quiz_attempts"]
student_answers_t = metadata.tables["student_answers"]
question_bank_t = metadata.tables["question_bank"]
quizzes_t = metadata.tables["quizzes"]
speed_matrix_t = metadata.tables["speed_accuracy_matrix"]
topic_mastery_t = metadata.tables["topic_mastery"]
perf_summary_t = metadata.tables["student_performance_summary"]


def _load_all():
    with engine.connect() as conn:
        attempts = conn.execute(select(quiz_attempts_t)).mappings().all()
        answers = conn.execute(select(student_answers_t)).mappings().all()
        questions = conn.execute(select(question_bank_t)).mappings().all()
        quizzes = conn.execute(select(quizzes_t)).mappings().all()
    return attempts, answers, questions, quizzes


def persist_speed_accuracy_and_avg_time():
    print("Loading raw data...")
    attempts, answers, questions, quizzes = _load_all()
    quiz_by_id = {q["id"]: q for q in quizzes}

    # Convert Decimal -> float immediately on load, same fix as the
    # composite_score crash a few sessions back — don't let it bite twice.
    answers_by_attempt = defaultdict(list)
    for a in answers:
        answers_by_attempt[a["attempt_id"]].append({
            "is_correct": a["is_correct"],
            "time_taken_seconds": float(a["time_taken_seconds"]),
        })

    print(f"Computing M3/M4 quadrant for {len(attempts)} attempts...")
    start = time.time()
    time_acc = defaultdict(list)

    with engine.begin() as conn:
        for i, att in enumerate(attempts, start=1):
            quiz = quiz_by_id.get(att["quiz_id"])
            if not quiz:
                continue
            quadrant = compute_quadrant_for_answers(answers_by_attempt.get(att["id"], []))
            if quadrant is None:
                continue

            stmt = pg_insert(speed_matrix_t).values(
                student_id=att["student_id"], quiz_id=att["quiz_id"], course_id=quiz["course_id"], **quadrant,
            ).on_conflict_do_update(index_elements=["student_id", "quiz_id"], set_=quadrant)
            conn.execute(stmt)

            time_acc[(att["student_id"], quiz["course_id"])].append(quadrant["avg_time_seconds"])
            if i % 1000 == 0:
                print(f"  {i}/{len(attempts)}...")

    print(f"M3/M4 done in {time.time() - start:.1f}s")

    print(f"Persisting M16 for {len(time_acc)} student-course pairs...")
    with engine.begin() as conn:
        for (student_id, course_id), times in time_acc.items():
            avg_time = round(float(np.mean(times)), 1)
            stmt = pg_insert(perf_summary_t).values(
                student_id=student_id, course_id=course_id, avg_time_per_question=avg_time,
            ).on_conflict_do_update(index_elements=["student_id", "course_id"], set_={"avg_time_per_question": avg_time})
            conn.execute(stmt)
    print("Done.")


def persist_topic_mastery():
    """M8 — trend_direction is computed from observed early-half vs late-half
    correctness, NOT from the generator's hidden ability_trend. Using the
    hidden ground truth here would mean the metric isn't actually measuring
    anything — it'd just be echoing back the answer key."""
    print("Loading raw data for topic mastery...")
    attempts, answers, questions, quizzes = _load_all()
    quiz_by_id = {q["id"]: q for q in quizzes}
    question_by_id = {q["id"]: q for q in questions}
    attempt_by_id = {a["id"]: a for a in attempts}

    buckets = defaultdict(list)
    for ans in answers:
        att = attempt_by_id.get(ans["attempt_id"])
        question = question_by_id.get(ans["question_id"])
        if not att or not question:
            continue
        quiz = quiz_by_id.get(att["quiz_id"])
        if not quiz:
            continue
        key = (att["student_id"], quiz["course_id"], question["topic"])
        buckets[key].append((att["created_at"], ans["is_correct"]))

    print(f"Computing + persisting M8 for {len(buckets)} combos...")
    with engine.begin() as conn:
        for i, (key, records) in enumerate(buckets.items(), start=1):
            student_id, course_id, topic = key
            records.sort(key=lambda r: r[0])
            correct_count = sum(1 for _, c in records if c)
            attempt_count = len(records)
            mastery_pct = round(100 * correct_count / attempt_count, 1)

            mid = max(1, attempt_count // 2)
            early, late = records[:mid], records[mid:]
            early_pct = 100 * sum(1 for _, c in early if c) / len(early) if early else mastery_pct
            late_pct = 100 * sum(1 for _, c in late if c) / len(late) if late else mastery_pct
            diff = late_pct - early_pct
            trend = "up" if diff > 8 else "down" if diff < -8 else "stable"

            stmt = pg_insert(topic_mastery_t).values(
                student_id=student_id, course_id=course_id, topic=topic,
                mastery_pct=mastery_pct, trend_direction=trend,
                attempt_count=attempt_count, correct_count=correct_count,
            ).on_conflict_do_update(
                index_elements=["student_id", "course_id", "topic"],
                set_={"mastery_pct": mastery_pct, "trend_direction": trend,
                      "attempt_count": attempt_count, "correct_count": correct_count},
            )
            conn.execute(stmt)
            if i % 500 == 0:
                print(f"  {i}/{len(buckets)}...")
    print("Done.")


if __name__ == "__main__":
    persist_speed_accuracy_and_avg_time()
    persist_topic_mastery()