-- 0003_indexes.sql
-- Every metric query filters on student_id and/or course_id. Index them now,
-- before there's real data volume to make this painful to add later.

create index idx_enrollments_student on enrollments(student_id);
create index idx_enrollments_course on enrollments(course_id);

create index idx_quizzes_course on quizzes(course_id);
create index idx_question_bank_course on question_bank(course_id);
create index idx_quiz_questions_quiz on quiz_questions(quiz_id);

create index idx_quiz_attempts_student on quiz_attempts(student_id);
create index idx_quiz_attempts_quiz on quiz_attempts(quiz_id);

create index idx_student_answers_attempt on student_answers(attempt_id);
create index idx_student_answers_question on student_answers(question_id);

create index idx_perf_summary_student_course on student_performance_summary(student_id, course_id);
create index idx_rank_summary_student_course on student_rank_summary(student_id, course_id);
create index idx_speed_matrix_student_quiz on speed_accuracy_matrix(student_id, quiz_id);
create index idx_topic_mastery_student_course on topic_mastery(student_id, course_id);
create index idx_topic_mastery_history_student on topic_mastery_history(student_id, course_id, topic);
create index idx_recommendations_student_course on adaptive_recommendations(student_id, course_id);
create index idx_score_trend_student_course on score_trend(student_id, course_id);