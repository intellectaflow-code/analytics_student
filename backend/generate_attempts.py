import time
from sqlalchemy import select
from app.db import engine, metadata
from app.generator.ability_model import generate_ability_profiles
from app.generator.attempts import build_attempts_and_answers, insert_attempts_and_answers

profiles_t = metadata.tables["profiles"]

with engine.connect() as conn:
    students = conn.execute(
        select(profiles_t).where(profiles_t.c.role == "student")
    ).mappings().all()

print(f"Building ability profiles for {len(students)} students...")
profiles = generate_ability_profiles(students)

print("Simulating attempts and answers across all courses (this can take a minute)...")
start = time.time()
attempts, answers = build_attempts_and_answers(profiles)  # no course_id = every course
elapsed = time.time() - start
print(f"  Generated {len(attempts)} attempts, {len(answers)} answers in {elapsed:.1f}s")

print("Writing to the database...")
insert_attempts_and_answers(attempts, answers)
print("Done.")