import re
import uuid
import random
from datetime import timedelta
import numpy as np
from sqlalchemy import select, insert
from app.db import engine, metadata
from app import config

quizzes_t = metadata.tables["quizzes"]
quiz_questions_t = metadata.tables["quiz_questions"]
question_bank_t = metadata.tables["question_bank"]
enrollments_t = metadata.tables["enrollments"]
quiz_attempts_t = metadata.tables["quiz_attempts"]
student_answers_t = metadata.tables["student_answers"]

DIFFICULTY_PENALTY = {"easy": 0.0, "medium": 0.10, "hard": 0.20}   # was 0.15, 0.30
DIFFICULTY_BASE_TIME = {"easy": 20, "medium": 40, "hard": 65}  # seconds
NEG_MARK_FRACTION = 0.5
SKIP_QUESTION_PROB = 0.05
SKIP_QUIZ_PROB = 0.12
GUESS_FLOOR = 0.20  # baseline chance of a correct guess on an MCQ, even with no real knowledge


def _quiz_number(title):
    match = re.search(r"(\d+)$", title)
    return int(match.group(1)) if match else 1


def _load_reference_data():
    with engine.connect() as conn:
        quizzes = conn.execute(select(quizzes_t)).mappings().all()
        quiz_questions = conn.execute(select(quiz_questions_t)).mappings().all()
        questions = conn.execute(select(question_bank_t)).mappings().all()
        enrollments = conn.execute(select(enrollments_t)).mappings().all()

    questions_by_id = {q["id"]: q for q in questions}
    quiz_question_map = {}
    for qq in quiz_questions:
        quiz_question_map.setdefault(qq["quiz_id"], []).append(qq["question_id"])

    quizzes_by_course = {}
    for qz in quizzes:
        quizzes_by_course.setdefault(qz["course_id"], []).append(qz)

    students_by_course = {}
    for e in enrollments:
        students_by_course.setdefault(e["course_id"], []).append(e["student_id"])

    return questions_by_id, quiz_question_map, quizzes_by_course, students_by_course


def _simulate_one_attempt(student_id, profile, quiz, question_ids, questions_by_id):
    q_num = _quiz_number(quiz["title"])
    attempt_id = str(uuid.uuid4())
    submitted_at = (
        config.SEMESTER_START_DATE
        + timedelta(weeks=q_num - 1, hours=random.randint(0, 8))
    )

    answers = []
    total_score = 0.0

    for qid in question_ids:
        if random.random() < SKIP_QUESTION_PROB:
            continue

        question = questions_by_id[qid]
        topic = question["topic"]
        difficulty = question["difficulty"]
        marks = float(question["marks"])

        base_ability = profile["topic_ability"][topic]
        trend = profile["topic_trend"][topic]
        ability_now = float(np.clip(base_ability + trend * (q_num - 1), 0.0, 1.0))

        raw_skill = float(np.clip(ability_now - DIFFICULTY_PENALTY[difficulty], 0.0, 1.0))
        p_correct = GUESS_FLOOR + (1 - GUESS_FLOOR) * raw_skill

        base_time = DIFFICULTY_BASE_TIME[difficulty]
        time_factor = 1 + profile["speed_tendency"] * 0.35
        time_taken = max(5.0, float(np.random.normal(base_time * time_factor, base_time * 0.2)))

        if time_taken < base_time * 0.5:              # rushing makes mistakes more likely
            p_correct *= 0.6

        if random.random() > profile["consistency"]:   # occasional volatile attempt
            p_correct += random.uniform(-0.25, 0.1)

        p_correct = float(np.clip(p_correct, 0.05, 0.95))
        is_correct = random.random() < p_correct
        score_awarded = marks if is_correct else -NEG_MARK_FRACTION * marks
        total_score += score_awarded

        answers.append({
            "id": str(uuid.uuid4()),
            "attempt_id": attempt_id,
            "question_id": qid,
            "is_correct": bool(is_correct),
            "score_awarded": round(score_awarded, 2),
            "time_taken_seconds": round(time_taken, 1),
            "submitted_at": submitted_at,
        })

    if not answers:
        return None, []

    attempt = {
        "id": attempt_id,
        "quiz_id": quiz["id"],
        "student_id": student_id,
        "attempt_number": 1,
        "total_score": round(total_score, 2),
        "status": "submitted",
        "created_at": submitted_at,
    }
    return attempt, answers


def build_attempts_and_answers(profiles, course_id=None):
    """
    Pure computation, no DB writes yet. Pass course_id to restrict to one
    course for a quick check before running this against every course.
    """
    questions_by_id, quiz_question_map, quizzes_by_course, students_by_course = _load_reference_data()

    if course_id:
        quizzes_by_course = {course_id: quizzes_by_course[course_id]}

    attempts, answers = [], []

    for cid, quiz_list in quizzes_by_course.items():
        for student_id in students_by_course.get(cid, []):
            profile = profiles[student_id]
            for quiz in quiz_list:
                if random.random() < SKIP_QUIZ_PROB:
                    continue

                question_ids = quiz_question_map.get(quiz["id"], [])
                attempt, attempt_answers = _simulate_one_attempt(
                    student_id, profile, quiz, question_ids, questions_by_id
                )
                if attempt:
                    attempts.append(attempt)
                    answers.extend(attempt_answers)

    return attempts, answers


def insert_attempts_and_answers(attempts, answers, batch_size=1000):
    with engine.begin() as conn:
        for i in range(0, len(attempts), batch_size):
            conn.execute(insert(quiz_attempts_t), attempts[i:i + batch_size])
        for i in range(0, len(answers), batch_size):
            conn.execute(insert(student_answers_t), answers[i:i + batch_size])