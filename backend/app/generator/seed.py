from app.generator import entities


def main():
    print("Generating profiles...")
    students, teachers = entities.generate_profiles()
    print(f"  {len(students)} students, {len(teachers)} teachers")

    print("Generating courses...")
    courses = entities.generate_courses()
    print(f"  {len(courses)} courses")

    print("Generating enrollments...")
    enrollments = entities.generate_enrollments(students, courses)
    print(f"  {len(enrollments)} enrollments")

    print("Generating question bank...")
    questions = entities.generate_question_bank(courses)
    print(f"  {len(questions)} questions")

    print("Generating quizzes...")
    quizzes = entities.generate_quizzes(courses)
    print(f"  {len(quizzes)} quizzes")

    print("Generating quiz questions...")
    quiz_questions = entities.generate_quiz_questions(quizzes, questions)
    print(f"  {len(quiz_questions)} quiz-question links")


if __name__ == "__main__":
    main()