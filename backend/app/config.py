from datetime import datetime

SEMESTER_START_DATE = datetime(2026, 1, 12, 9, 0, 0)  # a Monday, 9 AM

COURSES = [
    {"name": "Design and Analysis of Algorithms", "code": "DAA",
     "topics": ["Greedy Algorithms", "Dynamic Programming", "Graph Traversal", "Divide and Conquer"]},
    {"name": "Database Management Systems", "code": "DBMS",
     "topics": ["SQL Joins", "Normalization", "Transactions", "Indexing"]},
    {"name": "Operating Systems", "code": "OS",
     "topics": ["OS Scheduling", "Memory Management", "Deadlocks", "File Systems"]},
    {"name": "Computer Networks", "code": "CN",
     "topics": ["TCP/IP Layers", "Routing", "Network Security", "Congestion Control"]},
    {"name": "Machine Learning", "code": "ML",
     "topics": ["Neural Networks", "Regression", "Classification", "Clustering"]},
]

BRANCHES = ["CSE", "ECE", "ME"]
SECTIONS_PER_BRANCH = ["A", "B"]
STUDENTS_PER_SECTION = 20   # 3 branches x 2 sections x 20 = 120 students total
SEMESTER = 4

QUIZZES_PER_COURSE = 12
QUESTIONS_PER_TOPIC = 5
DIFFICULTIES = ["easy", "medium", "hard"]