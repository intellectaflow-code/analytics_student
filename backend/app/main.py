from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import students

app = FastAPI(title="TestArena Student Analytics")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for an internal 3-day demo, tighten later
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(students.router, prefix="/api/v1/students")