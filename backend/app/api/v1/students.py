from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func
from app.db import engine, metadata
from app.metrics.trends_and_recs import build_recommendations, skill_rating_buckets

from app.metrics.groq_narrative import (
    generate_zone1_narrative,
    generate_zone2_narrative,
    generate_zone3_narrative,
    generate_zone4_narrative,
    generate_zone4_table,
    generate_zone5_narrative,
    generate_zone5_summary,
    generate_zone8_narrative,
    generate_summary_narrative,
    generate_adaptive_recommendations,
)

router = APIRouter()

profiles_t = metadata.tables["profiles"]
courses_t = metadata.tables["courses"]
quizzes_t = metadata.tables["quizzes"]
quiz_attempts_t = metadata.tables["quiz_attempts"]
student_answers_t = metadata.tables["student_answers"]
perf_summary_t = metadata.tables["student_performance_summary"]
rank_summary_t = metadata.tables["student_rank_summary"]
speed_matrix_t = metadata.tables["speed_accuracy_matrix"]
topic_mastery_t = metadata.tables["topic_mastery"]
score_trend_t = metadata.tables["score_trend"]
class_summary_t = metadata.tables["class_analytics_summary"]
enrollments_t = metadata.tables["enrollments"]


@router.get("/{student_id}/courses/{course_id}/overview")
def get_overview(student_id: str, course_id: str):
    with engine.connect() as conn:
        # Base summary row
        row = conn.execute(
            select(
                perf_summary_t.c.composite_score,
                perf_summary_t.c.band_label,
                perf_summary_t.c.streak_count,
                perf_summary_t.c.avg_time_per_question,
                perf_summary_t.c.consistency_score,
                profiles_t.c.full_name,
                profiles_t.c.branch,
                profiles_t.c.section,
                courses_t.c.name.label("course_name"),
                courses_t.c.code.label("course_code"),
            )
            .join(profiles_t, profiles_t.c.id == perf_summary_t.c.student_id)
            .join(courses_t, courses_t.c.id == perf_summary_t.c.course_id)
            .where(perf_summary_t.c.student_id == student_id,
                   perf_summary_t.c.course_id == course_id)
        ).mappings().first()

        if not row:
            raise HTTPException(status_code=404, detail="No data")

        # Attempt stats
        attempts = conn.execute(
            select(quiz_attempts_t.c.total_score, quizzes_t.c.total_marks)
            .join(quizzes_t, quizzes_t.c.id == quiz_attempts_t.c.quiz_id)
            .where(quiz_attempts_t.c.student_id == student_id,
                   quizzes_t.c.course_id == course_id)
        ).mappings().all()

        total_quizzes = conn.execute(
            select(func.count()).select_from(quizzes_t)
            .where(quizzes_t.c.course_id == course_id)
        ).scalar()

        # Negative marks lost
        neg_marks = conn.execute(
            select(func.sum(student_answers_t.c.score_awarded))
            .join(quiz_attempts_t, quiz_attempts_t.c.id == student_answers_t.c.attempt_id)
            .join(quizzes_t, quizzes_t.c.id == quiz_attempts_t.c.quiz_id)
            .where(
                quiz_attempts_t.c.student_id == student_id,
                quizzes_t.c.course_id == course_id,
                student_answers_t.c.score_awarded < 0,
            )
        ).scalar()

        # Class summary
        class_row = conn.execute(
            select(class_summary_t.c.avg_score, class_summary_t.c.topper_score)
            .where(class_summary_t.c.course_id == course_id)
        ).mappings().first()

    tests_taken = len(attempts)
    attempt_rate = round(100 * tests_taken / total_quizzes, 1) if total_quizzes else 0
    scores_pct = [
        round(100 * float(a["total_score"]) / float(a["total_marks"]), 1)
        for a in attempts if a["total_marks"]
    ]
    avg_score = round(sum(scores_pct) / len(scores_pct), 1) if scores_pct else 0
    best_score = max(scores_pct) if scores_pct else 0

    return {
        "student_name": row["full_name"],
        "branch": row["branch"],
        "section": row["section"],
        "course_name": row["course_name"],
        "course_code": row["course_code"],
        "composite_score": float(row["composite_score"]),
        "band_label": row["band_label"],
        "streak_count": row["streak_count"],
        "avg_time_per_question": float(row["avg_time_per_question"] or 0),
        "consistency_score": float(row["consistency_score"] or 0),
        "tests_taken": tests_taken,
        "attempt_rate": attempt_rate,
        "avg_score_pct": avg_score,
        "best_score_pct": best_score,
        "neg_marks_lost": abs(float(neg_marks or 0)),
        "class_avg": float(class_row["avg_score"]) if class_row else 0,
        "branch_topper": float(class_row["topper_score"]) if class_row else 0,
    }


@router.get("/{student_id}/courses/{course_id}/rank")
def get_rank(student_id: str, course_id: str):
    with engine.connect() as conn:
        row = conn.execute(
            select(rank_summary_t).where(
                rank_summary_t.c.student_id == student_id,
                rank_summary_t.c.course_id == course_id,
            )
        ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="No rank data")
    return {
        "class_rank": row["class_rank"],
        "class_percentile": float(row["class_percentile"]),
        "branch_rank": row["branch_rank"],
        "branch_percentile": float(row["branch_percentile"]),
        "platform_rank": row["platform_rank"],
        "platform_percentile": float(row["platform_percentile"]),
    }


@router.get("/{student_id}/courses/{course_id}/speed-accuracy")
def get_speed_accuracy(student_id: str, course_id: str):
    with engine.connect() as conn:
        row = conn.execute(
            select(
                func.sum(speed_matrix_t.c.fast_correct).label("fast_correct"),
                func.sum(speed_matrix_t.c.fast_wrong).label("fast_wrong"),
                func.sum(speed_matrix_t.c.slow_correct).label("slow_correct"),
                func.sum(speed_matrix_t.c.slow_wrong).label("slow_wrong"),
            ).where(speed_matrix_t.c.student_id == student_id,
                    speed_matrix_t.c.course_id == course_id)
        ).mappings().first()
    if not row or row["fast_correct"] is None:
        raise HTTPException(status_code=404, detail="No speed-accuracy data")
    return {k: int(v or 0) for k, v in row.items()}


@router.get("/{student_id}/speed-accuracy-by-subject")
def get_speed_accuracy_by_subject(student_id: str):
    with engine.connect() as conn:
        rows = conn.execute(
            select(
                courses_t.c.code,
                func.sum(speed_matrix_t.c.fast_correct).label("fast_correct"),
                func.sum(speed_matrix_t.c.fast_wrong).label("fast_wrong"),
            )
            .join(courses_t, courses_t.c.id == speed_matrix_t.c.course_id)
            .where(speed_matrix_t.c.student_id == student_id)
            .group_by(courses_t.c.code)
        ).mappings().all()
    return [{"subject": r["code"], "fast_correct": int(r["fast_correct"] or 0),
             "fast_wrong": int(r["fast_wrong"] or 0)} for r in rows]


@router.get("/{student_id}/courses/{course_id}/topic-mastery")
def get_topic_mastery(student_id: str, course_id: str):
    with engine.connect() as conn:
        rows = conn.execute(
            select(topic_mastery_t)
            .where(topic_mastery_t.c.student_id == student_id,
                   topic_mastery_t.c.course_id == course_id)
            .order_by(topic_mastery_t.c.mastery_pct)
        ).mappings().all()
    return [{"topic": r["topic"], "mastery_pct": float(r["mastery_pct"]),
             "trend_direction": r["trend_direction"]} for r in rows]


@router.get("/{student_id}/courses/{course_id}/consistency")
def get_consistency(student_id: str, course_id: str):
    with engine.connect() as conn:
        row = conn.execute(
            select(perf_summary_t.c.consistency_score, perf_summary_t.c.streak_count)
            .where(perf_summary_t.c.student_id == student_id,
                   perf_summary_t.c.course_id == course_id)
        ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="No data")
    return {"consistency_score": float(row["consistency_score"] or 0),
            "streak_count": row["streak_count"]}


@router.get("/{student_id}/courses/{course_id}/trend")
def get_trend(student_id: str, course_id: str):
    with engine.connect() as conn:
        rows = conn.execute(
            select(score_trend_t.c.score, score_trend_t.c.taken_at, quizzes_t.c.title)
            .join(quizzes_t, quizzes_t.c.id == score_trend_t.c.quiz_id)
            .where(score_trend_t.c.student_id == student_id,
                   score_trend_t.c.course_id == course_id)
            .order_by(score_trend_t.c.taken_at)
        ).mappings().all()
    return [{"quiz": r["title"], "score": float(r["score"]),
             "taken_at": r["taken_at"].isoformat()} for r in rows]


@router.get("/{student_id}/courses/{course_id}/recommendations")
def get_recommendations(student_id: str, course_id: str):
    with engine.connect() as conn:
        topics = conn.execute(
            select(topic_mastery_t.c.topic, topic_mastery_t.c.mastery_pct)
            .where(topic_mastery_t.c.student_id == student_id,
                   topic_mastery_t.c.course_id == course_id)
        ).mappings().all()
        speed = conn.execute(
            select(
                func.sum(speed_matrix_t.c.fast_correct).label("fast_correct"),
                func.sum(speed_matrix_t.c.fast_wrong).label("fast_wrong"),
            ).where(speed_matrix_t.c.student_id == student_id,
                    speed_matrix_t.c.course_id == course_id)
        ).mappings().first()

    topic_rows = [{"topic": t["topic"], "mastery_pct": float(t["mastery_pct"])} for t in topics]
    speed_summary = {"fast_correct": int(speed["fast_correct"] or 0),
                     "fast_wrong": int(speed["fast_wrong"] or 0)} if speed else {}
    return build_recommendations(topic_rows, speed_summary)


@router.get("/{student_id}/peer-radar")
def get_peer_radar(student_id: str):
    with engine.connect() as conn:
        rows = conn.execute(
            select(
                courses_t.c.code,
                perf_summary_t.c.composite_score,
                class_summary_t.c.avg_score,
                class_summary_t.c.topper_score,
            )
            .join(courses_t, courses_t.c.id == perf_summary_t.c.course_id)
            .join(class_summary_t, class_summary_t.c.course_id == perf_summary_t.c.course_id)
            .where(perf_summary_t.c.student_id == student_id)
        ).mappings().all()
    return [{"subject": r["code"], "you": float(r["composite_score"]),
             "class_avg": float(r["avg_score"]), "topper": float(r["topper_score"])}
            for r in rows]


@router.get("/{student_id}/subject-ratings")
def get_subject_ratings(student_id: str):
    """Zone 6 — one skill-rating tile per enrolled course."""
    with engine.connect() as conn:
        rows = conn.execute(
            select(
                courses_t.c.code,
                func.avg(topic_mastery_t.c.mastery_pct).label("avg_mastery"),
            )
            .join(courses_t, courses_t.c.id == topic_mastery_t.c.course_id)
            .where(topic_mastery_t.c.student_id == student_id)
            .group_by(courses_t.c.code)
            .order_by(func.avg(topic_mastery_t.c.mastery_pct))
        ).mappings().all()

    def label(avg):
        if avg < 40:
            return "Need Training"
        elif avg < 70:
            return "Need Practice"
        return "Good to Go"

    def action(code, avg):
        actions = {
            "ML": "Start from basics before attempting more questions.",
            "OS": "Revise process scheduling and memory management.",
            "DBMS": "Practice normalization problems under timed conditions.",
            "CN": "Revise TCP/IP layer model and subnetting exercises.",
            "DAA": "Take full mock tests under exam conditions.",
        }
        return actions.get(code, "Continue practising and revising regularly.")

    return [
        {
            "subject": r["code"],
            "avg_mastery": round(float(r["avg_mastery"]), 1),
            "label": label(float(r["avg_mastery"])),
            "action": action(r["code"], float(r["avg_mastery"])),
        }
        for r in rows
    ]


@router.get("/{student_id}/all-trends")
def get_all_trends(student_id: str):
    """Zone 8 — multi-subject score trend, aligned by quiz number."""
    import re

    def quiz_num(title):
        m = re.search(r"(\d+)$", title)
        return int(m.group(1)) if m else 1

    with engine.connect() as conn:
        rows = conn.execute(
            select(
                courses_t.c.code,
                quizzes_t.c.title,
                score_trend_t.c.score,
            )
            .join(quizzes_t, quizzes_t.c.id == score_trend_t.c.quiz_id)
            .join(courses_t, courses_t.c.id == score_trend_t.c.course_id)
            .where(score_trend_t.c.student_id == student_id)
            .order_by(courses_t.c.code, score_trend_t.c.taken_at)
        ).mappings().all()

    # Build {quiz_num: {subject: score}} — align across subjects by quiz number
    from collections import defaultdict
    by_num = defaultdict(dict)
    subjects = set()
    for r in rows:
        num = quiz_num(r["title"])
        by_num[num][r["code"]] = round(float(r["score"]), 1)
        subjects.add(r["code"])

    result = []
    for num in sorted(by_num.keys()):
        point = {"quiz": f"Quiz {num}"}
        point.update(by_num[num])
        result.append(point)

    return {"data": result, "subjects": sorted(subjects)}

@router.get("/{student_id}/courses/{course_id}/full-report")
def get_full_report(student_id: str, course_id: str):
    overview = get_overview(student_id, course_id)
    rank = get_rank(student_id, course_id)
    quadrant = get_speed_accuracy(student_id, course_id)
    by_subject = get_speed_accuracy_by_subject(student_id)
    mastery = get_topic_mastery(student_id, course_id)
    radar = get_peer_radar(student_id)
    subject_ratings = get_subject_ratings(student_id)
    all_trends = get_all_trends(student_id)

    # AI-generated narrative + recommendations
    recommendations = generate_adaptive_recommendations(mastery, quadrant, overview)

    return {
        "overview": overview,
        "rank": rank,
        "quadrant": quadrant,
        "by_subject": by_subject,
        "mastery": mastery,
        "radar": radar,
        "subject_ratings": subject_ratings,
        "recommendations": recommendations,
        "all_trends": all_trends,
        "narrative": {
            "zone1": generate_zone1_narrative(overview),
            "zone2": generate_zone2_narrative(rank),
            "zone3": generate_zone3_narrative(quadrant),
            "zone4": generate_zone4_narrative(mastery),
            "zone4_table": generate_zone4_table(mastery),
            "zone5": generate_zone5_narrative(radar),
            "zone5_summary": generate_zone5_summary(radar),
            "zone8": generate_zone8_narrative(overview),
            "summary": generate_summary_narrative(overview, rank, radar),
        }
    }