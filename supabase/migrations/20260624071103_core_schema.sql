-- 0001_core_schema.sql
-- Source-shaped tables, modeled on the TestArena ER diagram.
-- Order matters: each table only references tables already created above it.

-- No dependencies
create table profiles (
  id uuid primary key default gen_random_uuid(),
  full_name text,
  role text check (role in ('student','teacher')),
  branch text,
  section text,
  sem smallint,
  is_active boolean default true
);

create table courses (
  id uuid primary key default gen_random_uuid(),
  name text,
  code text,
  semester integer,
  branch text
);

-- Depends on profiles + courses
create table enrollments (
  id uuid primary key default gen_random_uuid(),
  course_id uuid references courses(id),
  student_id uuid references profiles(id),
  enrolled_at timestamp default now()
);

-- Depends on courses
create table quizzes (
  id uuid primary key default gen_random_uuid(),
  course_id uuid references courses(id),
  title text,
  total_marks numeric,
  duration_minutes integer,
  start_time timestamp,
  end_time timestamp,
  is_published boolean default true
);

create table question_bank (
  id uuid primary key default gen_random_uuid(),
  course_id uuid references courses(id),
  topic text,
  difficulty text,
  marks numeric
);

-- Depends on quizzes + question_bank
create table quiz_questions (
  id uuid primary key default gen_random_uuid(),
  quiz_id uuid references quizzes(id),
  question_id uuid references question_bank(id),
  question_order integer
);

-- Depends on quizzes + profiles
create table quiz_attempts (
  id uuid primary key default gen_random_uuid(),
  quiz_id uuid references quizzes(id),
  student_id uuid references profiles(id),
  attempt_number integer default 1,
  total_score numeric,
  status text default 'submitted',
  created_at timestamp default now()
);

-- Depends on quiz_attempts + question_bank
create table student_answers (
  id uuid primary key default gen_random_uuid(),
  attempt_id uuid references quiz_attempts(id),
  question_id uuid references question_bank(id),
  is_correct boolean,
  score_awarded numeric,
  time_taken_seconds numeric,
  submitted_at timestamp default now()
);