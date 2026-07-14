# TestArena Student Analytics

A comprehensive analytics dashboard and automated PDF report generator for evaluating student performance, speed vs. accuracy metrics, peer comparison, and adaptive recommendations.

## Tech Stack
- **Backend:** Python, FastAPI, Supabase (PostgreSQL), Groq (LLM for narrative generation)
- **Frontend:** React, Vite, Recharts, `@react-pdf/renderer`

## Project Structure
```text
testArena_Student_Analytics/
├── backend/                  # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/           # API endpoints (students routing)
│   │   ├── generator/        # Scripts for generating mock data & attempts
│   │   ├── jobs/             # Background jobs & scheduled tasks (APScheduler)
│   │   ├── metrics/          # Analytics logic & Groq LLM integration
│   │   ├── config.py         # Configuration settings
│   │   ├── db.py             # Database connection setup
│   │   └── main.py           # FastAPI entry point
│   └── .env                  # Backend environment variables
├── frontend/                 # React Frontend (Vite)
│   ├── src/
│   │   ├── App.jsx           # Main dashboard UI component
│   │   ├── ReportPDF.jsx     # PDF layout template
│   │   ├── App.css           # Glassmorphism & animation styles
│   │   └── index.css         # Global variables & dark mode theme
│   └── package.json          # Node dependencies
└── supabase/                 # Database definitions
    └── migrations/           # SQL scripts for DB schema setup
```

## Setup Instructions

### 1. Database Setup (Supabase)
This project uses Supabase as a Postgres database provider. You can run it locally using the Supabase CLI, or link to a remote Supabase project.

If running locally with Docker:
```bash
supabase start
```
*Note: Make sure your migrations from `supabase/migrations/` have been applied.*

### 2. Backend Setup (FastAPI)
Navigate to the backend directory, set up your Python virtual environment, and install the required dependencies (FastAPI, psycopg2, groq, etc.).

```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install requirements (make sure FastAPI, Uvicorn, psycopg2-binary, groq are installed)
pip install fastapi uvicorn psycopg2-binary groq python-dotenv
```

**Environment Variables (`backend/.env`)**
Create a `.env` file in the `backend/` directory with the following variables:
```ini
# Supabase PostgreSQL Database URL
DATABASE_URL="postgresql://postgres:postgres@localhost:54322/postgres"

# Groq API Key (used for LLM narrative generation)
GROQ_API_KEY="gsk_your_api_key_here"
```

**Run the Backend Server:**
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`.

### 3. Frontend Setup (React)
Open a new terminal window, navigate to the frontend directory, and install dependencies.

```bash
cd frontend
npm install
```

**Run the Frontend Development Server:**
```bash
npm run dev
```
The frontend dashboard will be accessible at `http://localhost:5173`.

## Features
- **Premium UI Dashboard:** Built with a modern dark mode, glassmorphism (`backdrop-filter: blur`), glowing neon accents, and smooth micro-animations.
- **Dynamic PDF Generation:** Downloads a comprehensive multi-page PDF report generated directly in the browser using `@react-pdf/renderer`.
- **AI-Powered Recommendations:** Analyzes student weaknesses and rushing patterns, sending data to the Groq API to generate hyper-personalized learning advice.
- **Speed vs. Accuracy Quadrants:** Groups quiz answers into 4 quadrants (fast & correct, fast & wrong, slow & correct, slow & wrong) to identify bad habits like rushing.
- **Peer Comparison:** Visualizes the student's standing against class averages and branch toppers using radar charts and percentile rankings.
