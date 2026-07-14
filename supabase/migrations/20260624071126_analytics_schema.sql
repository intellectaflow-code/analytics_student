-- 0002_analytics_schema.sql
-- Computed tables. These are the actual deliverable of the analytics service.
-- All depend only on tables from 0001 (profiles, courses, quizzes), already created.

create table student_performance_summary (   -- M1, M2, M14, M15, M16
  id uuid primary key default gen_random_uuid(),
  student_id uuid references profiles(id),
  course_id uuid references courses(id),
  composite_score numeric(5,2),
  band_label text,
  consistency_score numeric(5,2),
  streak_count integer default 0,
  neg_marks_lost numeric,
  attempt_rate numeric(5,2),
  avg_time_per_question numeric(5,2),
  computed_at timestamp default now(),
  unique(student_id, course_id)
);

create table student_rank_summary (          -- M5, M6, M7
  id uuid primary key default gen_random_uuid(),
  student_id uuid references profiles(id),
  course_id uuid references courses(id),
  class_rank integer, class_percentile numeric(5,2),
  branch_rank integer, branch_percentile numeric(5,2),
  platform_rank integer, platform_percentile numeric(5,2),
  rank_delta_class integer default 0,
  rank_delta_branch integer default 0,
  computed_at timestamp default now(),
  unique(student_id, course_id)
);

create table speed_accuracy_matrix (         -- M3, M4
  id uuid primary key default gen_random_uuid(),
  student_id uuid references profiles(id),
  quiz_id uuid references quizzes(id),
  course_id uuid references courses(id),
  fast_correct integer default 0,
  fast_wrong integer default 0,
  slow_correct integer default 0,
  slow_wrong integer default 0,
  avg_time_seconds numeric,
  computed_at timestamp default now(),
  unique(student_id, quiz_id)
);

create table topic_mastery (                  -- M8, M9
  id uuid primary key default gen_random_uuid(),
  student_id uuid references profiles(id),
  course_id uuid references courses(id),
  topic text not null,
  mastery_pct numeric(5,2),
  trend_direction text check (trend_direction in ('up','down','stable')),
  attempt_count integer,
  correct_count integer,
  last_updated timestamp default now(),
  unique(student_id, course_id, topic)
);

create table topic_mastery_history (          -- feeds M11's mastery-drop rule
  id uuid primary key default gen_random_uuid(),
  student_id uuid references profiles(id),
  course_id uuid references courses(id),
  topic text not null,
  mastery_pct numeric(5,2),
  recorded_at timestamp default now()
);

create table adaptive_recommendations (       -- M11, M12
  id uuid primary key default gen_random_uuid(),
  student_id uuid references profiles(id),
  course_id uuid references courses(id),
  priority integer,
  category text check (category in ('CRITICAL','IMPROVE','REINFORCE')),
  action_text text,
  evidence_text text,
  topic text,
  is_dismissed boolean default false,
  generated_at timestamp default now(),
  unique(student_id, course_id, topic, category)
);

create table score_trend (                    -- M13
  id uuid primary key default gen_random_uuid(),
  student_id uuid references profiles(id),
  course_id uuid references courses(id),
  quiz_id uuid references quizzes(id),
  score numeric(5,2),
  taken_at timestamp,
  trend_slope numeric,
  unique(student_id, quiz_id)
);

create table class_analytics_summary (        -- M10
  id uuid primary key default gen_random_uuid(),
  course_id uuid references courses(id) unique,
  total_students integer,
  avg_score numeric,
  pass_rate numeric,
  engagement_score numeric,
  topper_score numeric,
  topper_student_id uuid references profiles(id),
  branch_avg_score numeric,
  platform_avg_score numeric,
  computed_at timestamp default now()
);

-- Operational table: every metrics job run logged here for debugging
create table job_run_log (
  id uuid primary key default gen_random_uuid(),
  job_name text,
  status text check (status in ('running','success','failed')),
  rows_affected integer,
  error_message text,
  started_at timestamp default now(),
  finished_at timestamp
);