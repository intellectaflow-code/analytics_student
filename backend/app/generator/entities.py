import uuid
from faker import Faker
from sqlalchemy import insert
from app.db import engine, metadata
from app import config

fake = Faker()

profiles_t = metadata.tables["profiles"]
courses_t = metadata.tables["courses"]
enrollments_t = metadata.tables["enrollments"]
question_bank_t = metadata.tables["question_bank"]
quizzes_t = metadata.tables["quizzes"]
quiz_questions_t = metadata.tables["quiz_questions"]


def generate_profiles():
    students = []
    for branch in config.BRANCHES:
        for section in config.SECTIONS_PER_BRANCH:
            for _ in range(config.STUDENTS_PER_SECTION):
                students.append({
                    "id": str(uuid.uuid4()),
                    "full_name": fake.name(),
                    "role": "student",
                    "branch": branch,
                    "section": section,
                    "sem": config.SEMESTER,
                    "is_active": True,
                })

    teachers = [{
        "id": str(uuid.uuid4()),
        "full_name": fake.name(),
        "role": "teacher",
        "branch": branch,
        "section": None,
        "sem": None,
        "is_active": True,
    } for branch in config.BRANCHES for _ in range(2)]

    with engine.begin() as conn:
        conn.execute(insert(profiles_t), students + teachers)
    return students, teachers


def generate_courses():
    courses = []
    for c in config.COURSES:
        for branch in config.BRANCHES:
            courses.append({
                "id": str(uuid.uuid4()),
                "name": c["name"],
                "code": c["code"],
                "semester": config.SEMESTER,
                "branch": branch,
            })
    with engine.begin() as conn:
        conn.execute(insert(courses_t), courses)
    return courses


def generate_enrollments(students, courses):
    enrollments = []
    for course in courses:
        for student in students:
            if student["branch"] == course["branch"]:
                enrollments.append({
                    "id": str(uuid.uuid4()),
                    "course_id": course["id"],
                    "student_id": student["id"],
                })
    with engine.begin() as conn:
        conn.execute(insert(enrollments_t), enrollments)
    return enrollments


def generate_question_bank(courses):
    questions = []
    topics_by_code = {c["code"]: c["topics"] for c in config.COURSES}
    for course in courses:
        for topic in topics_by_code[course["code"]]:
            for _ in range(config.QUESTIONS_PER_TOPIC):
                questions.append({
                    "id": str(uuid.uuid4()),
                    "course_id": course["id"],
                    "topic": topic,
                    "difficulty": fake.random_element(config.DIFFICULTIES),
                    "marks": 2,
                })
    with engine.begin() as conn:
        conn.execute(insert(question_bank_t), questions)
    return questions


def generate_quizzes(courses):
    quizzes = []
    for course in courses:
        for i in range(config.QUIZZES_PER_COURSE):
            quizzes.append({
                "id": str(uuid.uuid4()),
                "course_id": course["id"],
                "title": f"{course['code']} Quiz {i + 1}",
                "total_marks": 50,
                "duration_minutes": 30,
                "is_published": True,
            })
    with engine.begin() as conn:
        conn.execute(insert(quizzes_t), quizzes)
    return quizzes


def generate_quiz_questions(quizzes, questions):
    quiz_questions = []
    by_course = {}
    for q in questions:
        by_course.setdefault(q["course_id"], []).append(q)

    for quiz in quizzes:
        pool = by_course[quiz["course_id"]]
        chosen = fake.random_elements(pool, length=min(15, len(pool)), unique=True)
        for order, q in enumerate(chosen, start=1):
            quiz_questions.append({
                "id": str(uuid.uuid4()),
                "quiz_id": quiz["id"],
                "question_id": q["id"],
                "question_order": order,
            })
    with engine.begin() as conn:
        conn.execute(insert(quiz_questions_t), quiz_questions)
    return quiz_questions