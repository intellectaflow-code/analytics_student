import numpy as np
from collections import defaultdict


def compute_consistency(attempts):
    """M14 — reuses the same logic as composite_score's internal consistency
    calc, exposed standalone so we can show the raw number, not just its
    weighted contribution to M1."""
    scores = [a["total_score"] for a in attempts]
    total_marks = attempts[0]["total_marks"] if attempts else 1
    if len(scores) < 2 or not total_marks:
        return 100.0, 0.0
    std_dev = float(np.std(scores))
    consistency_pct = float(np.clip((1 - std_dev / total_marks) * 100, 0, 100))
    return round(consistency_pct, 1), round(std_dev, 1)


def build_recommendations(topic_rows, speed_summary):
    """M11 — rule-based, no ML. Three buckets matching the sample report's
    CRITICAL/IMPROVE/REINFORCE language."""
    recs = []

    for t in topic_rows:
        mastery = t["mastery_pct"]
        if mastery < 35:
            recs.append({
                "priority": 1, "category": "CRITICAL", "topic": t["topic"],
                "evidence_text": f"{t['topic']} mastery is {mastery}% — needs immediate attention.",
                "action_text": "Revise fundamentals and solve beginner-level practice questions.",
            })
        elif mastery < 60:
            recs.append({
                "priority": 2, "category": "IMPROVE", "topic": t["topic"],
                "evidence_text": f"{t['topic']} mastery is {mastery}% — developing, not yet solid.",
                "action_text": "Targeted practice and topic-wise quizzes.",
            })

    if speed_summary and speed_summary.get("fast_wrong", 0) > speed_summary.get("fast_correct", 1) * 0.15:
        recs.append({
            "priority": 1, "category": "CRITICAL", "topic": None,
            "evidence_text": f"{speed_summary['fast_wrong']} answers were fast & wrong — a rushing pattern.",
            "action_text": "Slow down on questions you're unsure about; avoid guessing under time pressure.",
        })

    strong_topics = [t for t in topic_rows if t["mastery_pct"] >= 75]
    if strong_topics:
        best = max(strong_topics, key=lambda t: t["mastery_pct"])
        recs.append({
            "priority": 3, "category": "REINFORCE", "topic": best["topic"],
            "evidence_text": f"{best['topic']} mastery is {best['mastery_pct']}% — your strongest area.",
            "action_text": "Sustain performance through periodic revision and advanced challenges.",
        })

    recs.sort(key=lambda r: r["priority"])
    return recs[:6]  # cap so the UI doesn't get cluttered


def skill_rating_buckets(topic_rows):
    """M9 — reshape per-topic mastery into named bands, matching the sample
    report's 'Need Training / Need Practice / Good to Go' tiles."""
    if not topic_rows:
        return []
    avg = round(float(np.mean([t["mastery_pct"] for t in topic_rows])), 1)
    if avg < 40:
        label = "Need Training"
    elif avg < 70:
        label = "Need Practice"
    else:
        label = "Good to Go"
    return {"avg_mastery": avg, "label": label}