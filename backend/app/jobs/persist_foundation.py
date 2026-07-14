import re
import time
import numpy as np
from collections import defaultdict
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.db import engine, metadata
from app.metrics.composite_score import compute_composite_score, band_label_for
from app.metrics.trends_and_recs import compute_consistency

enrollments_t = metadata.tables["enrollments"]
profiles_t = metadata.tables["profiles"]
courses_t = metadata.tables["courses"]
quizzes_t = metadata.tables["quizzes"]
quiz_attempts_t = metadata.tables["quiz_attempts"]
perf_summary_t = metadata.tables["student_performance_summary"]
rank_summary_t = metadata.tables["student_rank_summary"]
score_trend_t = metadata.tables["score_trend"]
class_summary_t = metadata.tables["class_analytics_summary"]


def _quiz_number(title):
    match = re.search(r"(\d+)$", title)
    return int(match.group(1)) if match else 1


def persist_composite_and_band():
    """M1 + M2 for every enrollment. This is the slow step (one DB round-trip
    per student-course pair) — expect a few minutes, that's fine for a batch job."""
    with engine.connect() as conn:
        enrollments = conn.execute(select(enrollments_t)).mappings().all()

    print(f"Computing + persisting M1/M2 for {len(enrollments)} enrollments...")
    start = time.time()

    with engine.begin() as conn:
        for i, e in enumerate(enrollments, start=1):
            result = compute_composite_score(conn, e["student_id"], e["course_id"])
            if result is None:
                continue
            band = band_label_for(result["composite_score"])

            stmt = pg_insert(perf_summary_t).values(
                student_id=e["student_id"],
                course_id=e["course_id"],
                composite_score=result["composite_score"],
                band_label=band,
            ).on_conflict_do_update(
                index_elements=["student_id", "course_id"],
                set_={"composite_score": result["composite_score"], "band_label": band},
            )
            conn.execute(stmt)

            if i % 100 == 0:
                print(f"  {i}/{len(enrollments)}...")

    print(f"Done in {time.time() - start:.1f}s")


def persist_ranks():
    with engine.connect() as conn:
        rows = conn.execute(
            select(
                perf_summary_t.c.student_id,
                perf_summary_t.c.course_id,
                perf_summary_t.c.composite_score,
                profiles_t.c.section,
                courses_t.c.code,
            )
            .join(profiles_t, profiles_t.c.id == perf_summary_t.c.student_id)
            .join(courses_t, courses_t.c.id == perf_summary_t.c.course_id)
        ).mappings().all()

    def rank_and_percentile(score, peer_scores):
        ranked = sorted(peer_scores, reverse=True)
        rank = ranked.index(score) + 1
        percentile = round(100 * (1 - (rank - 1) / len(ranked)), 1)
        return rank, percentile

    by_class, by_branch, by_platform = defaultdict(list), defaultdict(list), defaultdict(list)
    for r in rows:
        by_class[(r["course_id"], r["section"])].append(r["composite_score"])
        by_branch[r["course_id"]].append(r["composite_score"])
        by_platform[r["code"]].append(r["composite_score"])

    print(f"Computing + persisting M5-M7 for {len(rows)} rows...")
    BATCH_SIZE = 50
    for batch_start in range(0, len(rows), BATCH_SIZE):
        batch = rows[batch_start:batch_start + BATCH_SIZE]
        with engine.begin() as conn:   # fresh transaction per batch, not one giant one
            for r in batch:
                class_rank, class_pct = rank_and_percentile(r["composite_score"], by_class[(r["course_id"], r["section"])])
                branch_rank, branch_pct = rank_and_percentile(r["composite_score"], by_branch[r["course_id"]])
                platform_rank, platform_pct = rank_and_percentile(r["composite_score"], by_platform[r["code"]])

                stmt = pg_insert(rank_summary_t).values(
                    student_id=r["student_id"], course_id=r["course_id"],
                    class_rank=class_rank, class_percentile=class_pct,
                    branch_rank=branch_rank, branch_percentile=branch_pct,
                    platform_rank=platform_rank, platform_percentile=platform_pct,
                ).on_conflict_do_update(
                    index_elements=["student_id", "course_id"],
                    set_={
                        "class_rank": class_rank, "class_percentile": class_pct,
                        "branch_rank": branch_rank, "branch_percentile": branch_pct,
                        "platform_rank": platform_rank, "platform_percentile": platform_pct,
                    },
                )
                conn.execute(stmt)
        print(f"  {min(batch_start + BATCH_SIZE, len(rows))}/{len(rows)}...")
    print("Done.")


def persist_streaks():
    """M15 — consecutive quizzes attempted, walking backward from the most
    recent until the first gap."""
    with engine.connect() as conn:
        quizzes = conn.execute(select(quizzes_t)).mappings().all()
        attempts = conn.execute(
            select(quiz_attempts_t.c.student_id, quiz_attempts_t.c.quiz_id)
        ).mappings().all()

    # Sorting quiz titles as plain strings would put "Quiz 10" before "Quiz 2" —
    # sort by the actual numeric suffix instead, same helper attempts.py uses.
    quiz_order = defaultdict(list)
    for q in quizzes:
        quiz_order[q["course_id"]].append(q)
    for course_id in quiz_order:
        quiz_order[course_id].sort(key=lambda q: _quiz_number(q["title"]))

    quiz_to_course = {q["id"]: q["course_id"] for q in quizzes}
    attempted = defaultdict(set)
    for a in attempts:
        course_id = quiz_to_course.get(a["quiz_id"])
        if course_id:
            attempted[(a["student_id"], course_id)].add(a["quiz_id"])

    print(f"Computing + persisting M15 for {len(attempted)} student-course pairs...")
    with engine.begin() as conn:
        for (student_id, course_id), attempted_ids in attempted.items():
            streak = 0
            for q in reversed(quiz_order[course_id]):
                if q["id"] in attempted_ids:
                    streak += 1
                else:
                    break

            stmt = pg_insert(perf_summary_t).values(
                student_id=student_id, course_id=course_id, streak_count=streak,
            ).on_conflict_do_update(
                index_elements=["student_id", "course_id"],
                set_={"streak_count": streak},
            )
            conn.execute(stmt)
    print("Done.")
    
def persist_consistency():
    """M14 — reuses the same attempt-fetch pattern as composite_score.py."""
    from app.metrics.composite_score import _fetch_attempts_for_student_course

    with engine.connect() as conn:
        enrollments = conn.execute(select(enrollments_t)).mappings().all()

    print(f"Computing + persisting M14 for {len(enrollments)} enrollments...")
    with engine.begin() as conn:
        for e in enrollments:
            attempts = _fetch_attempts_for_student_course(conn, e["student_id"], e["course_id"])
            if not attempts:
                continue
            consistency_pct, _ = compute_consistency(attempts)

            stmt = pg_insert(perf_summary_t).values(
                student_id=e["student_id"], course_id=e["course_id"], consistency_score=consistency_pct,
            ).on_conflict_do_update(index_elements=["student_id", "course_id"], set_={"consistency_score": consistency_pct})
            conn.execute(stmt)
    print("Done.")


def persist_score_trend():
    """M13 — one row per attempt, used to draw the trend line."""
    with engine.connect() as conn:
        attempts = conn.execute(
            select(
                quiz_attempts_t.c.student_id, quiz_attempts_t.c.quiz_id,
                quiz_attempts_t.c.total_score, quiz_attempts_t.c.created_at,
                quizzes_t.c.course_id,
            ).join(quizzes_t, quizzes_t.c.id == quiz_attempts_t.c.quiz_id)
        ).mappings().all()

    print(f"Persisting M13 for {len(attempts)} attempts...")
    with engine.begin() as conn:
        for a in attempts:
            stmt = pg_insert(score_trend_t).values(
                student_id=a["student_id"], course_id=a["course_id"], quiz_id=a["quiz_id"],
                score=float(a["total_score"]), taken_at=a["created_at"],
            ).on_conflict_do_update(
                index_elements=["student_id", "quiz_id"],
                set_={"score": float(a["total_score"]), "taken_at": a["created_at"]},
            )
            conn.execute(stmt)
    print("Done.")
    
def persist_class_summary():
    """One row per course: average score and the topper, across everyone
    enrolled. This is what M10 compares each individual student against."""
    with engine.connect() as conn:
        rows = conn.execute(
            select(
                perf_summary_t.c.course_id,
                perf_summary_t.c.student_id,
                perf_summary_t.c.composite_score,
            )
        ).mappings().all()

    by_course = defaultdict(list)
    for r in rows:
        by_course[r["course_id"]].append(r)

    print(f"Computing + persisting M10 class summaries for {len(by_course)} courses...")
    with engine.begin() as conn:
        for course_id, course_rows in by_course.items():
            scores = [float(r["composite_score"]) for r in course_rows]
            topper = max(course_rows, key=lambda r: float(r["composite_score"]))

            stmt = pg_insert(class_summary_t).values(
                course_id=course_id,
                total_students=len(course_rows),
                avg_score=round(float(np.mean(scores)), 1),
                topper_score=float(topper["composite_score"]),
                topper_student_id=topper["student_id"],
            ).on_conflict_do_update(
                index_elements=["course_id"],
                set_={
                    "total_students": len(course_rows),
                    "avg_score": round(float(np.mean(scores)), 1),
                    "topper_score": float(topper["composite_score"]),
                    "topper_student_id": topper["student_id"],
                },
            )
            conn.execute(stmt)
    print("Done.")    


if __name__ == "__main__":
    persist_composite_and_band()
    persist_ranks()
    persist_streaks()
    persist_consistency()
    persist_score_trend()
    persist_class_summary()