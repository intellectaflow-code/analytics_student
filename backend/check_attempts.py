import numpy as np
from sqlalchemy import select
from app.db import engine, metadata
from app.generator.ability_model import generate_ability_profiles
from app.generator.attempts import build_attempts_and_answers, DIFFICULTY_BASE_TIME

profiles_t = metadata.tables["profiles"]
courses_t = metadata.tables["courses"]
question_bank_t = metadata.tables["question_bank"]

with engine.connect() as conn:
    students = conn.execute(select(profiles_t).where(profiles_t.c.role == "student")).mappings().all()
    one_course = conn.execute(select(courses_t).limit(1)).mappings().first()
    questions = conn.execute(
        select(question_bank_t).where(question_bank_t.c.course_id == one_course["id"])
    ).mappings().all()

difficulty_by_question = {q["id"]: q["difficulty"] for q in questions}

profiles = generate_ability_profiles(students)

print(f"Dry run on course: {one_course['name']} ({one_course['code']}-{one_course['branch']})")
attempts, answers = build_attempts_and_answers(profiles, course_id=one_course["id"])
print(f"Generated {len(attempts)} attempts, {len(answers)} answers (nothing written to DB yet)\n")

scores = [a["total_score"] for a in attempts]
print(f"Score range: {min(scores):.1f} to {max(scores):.1f}, mean {np.mean(scores):.1f}")

times = [a["time_taken_seconds"] for a in answers]
print(f"Time per question: {min(times):.1f}s to {max(times):.1f}s, mean {np.mean(times):.1f}s")

correct_rate = sum(a["is_correct"] for a in answers) / len(answers)
print(f"Overall correct rate: {correct_rate:.1%}\n")

# Measure time RELATIVE to that question's own difficulty-based expected time,
# instead of a single global cutoff — this controls for difficulty so we can
# actually see the speed_tendency effect on its own.
for a in answers:
    difficulty = difficulty_by_question[a["question_id"]]
    a["relative_time"] = a["time_taken_seconds"] / DIFFICULTY_BASE_TIME[difficulty]

rushed = [a for a in answers if a["relative_time"] < 0.5]       # the code's own rushing-penalty trigger
not_rushed = [a for a in answers if a["relative_time"] >= 0.5]

print(f"Answers under half the expected time for their difficulty: {len(rushed)} of {len(answers)}")
print(f"Accuracy when rushed:      {sum(a['is_correct'] for a in rushed) / len(rushed):.1%}")
print(f"Accuracy when not rushed:  {sum(a['is_correct'] for a in not_rushed) / len(not_rushed):.1%}")