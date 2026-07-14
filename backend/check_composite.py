from sqlalchemy import select
from app.db import engine, metadata
from app.metrics.composite_score import compute_composite_score, band_label_for

profiles_t = metadata.tables["profiles"]
enrollments_t = metadata.tables["enrollments"]
courses_t = metadata.tables["courses"]

with engine.connect() as conn:
    student = conn.execute(select(profiles_t).where(profiles_t.c.role == "student")).mappings().first()
    enrollment = conn.execute(
        select(enrollments_t).where(enrollments_t.c.student_id == student["id"])
    ).mappings().first()
    course = conn.execute(select(courses_t).where(courses_t.c.id == enrollment["course_id"])).mappings().first()

    result = compute_composite_score(conn, student["id"], course["id"])

print(f"Student: {student['full_name']} ({student['branch']}-{student['section']})")
print(f"Course:  {course['name']} ({course['code']})\n")

if result is None:
    print("No attempts found for this student/course pair.")
else:
    for key, value in result.items():
        print(f"  {key:18s} {value}")
    print(f"\n  band_label: {band_label_for(result['composite_score'])}")