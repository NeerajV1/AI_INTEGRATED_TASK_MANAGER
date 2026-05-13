# TaskFlow — AI-Powered Task Manager

A full-stack task management web app built with **FastAPI** and **PostgreSQL**, featuring JWT-based authentication and AI-powered task creation via Google Gemini.

---

## Features

- **User Authentication** — Signup, login, and logout with bcrypt-hashed passwords and JWT cookies
- **Task CRUD** — Create, view, update, and delete tasks with title, description, deadline, priority, and status
- **Auto-archiving** — Tasks marked as completed or failed are automatically moved to separate archive tables
- **Overdue Detection** — Tasks past their deadline are automatically moved to `failed_tasks` on the next check
- **AI Task Creation** — Paste any natural-language text (e.g. an email) and let Google Gemini extract a structured task from it

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Database | PostgreSQL via psycopg2 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| AI | Google Gemini (google-genai) |
| Frontend | HTML, CSS, Vanilla JavaScript |
| Config | python-dotenv |

---

## Project Structure

```
├── main.py              # FastAPI app entry point, router registration
├── login.py             # Login & logout endpoints
├── signup.py            # Signup endpoints
├── tasks.py             # Task CRUD + AI task creation endpoints
├── ai_agent.py          # Google Gemini integration for parsing tasks from text
├── auth_utils.py        # JWT create/decode helpers
├── security.py          # Password hashing and verification
├── databaseConnection.py# PostgreSQL connection helper
├── static/
│   ├── script.js        # Auth-related frontend logic (login, signup, logout)
│   └── tasks.js         # Task management frontend logic
└── templates/
    ├── hello.html       # Main dashboard (shown after login)
    ├── signup.html      # Signup form
    └── startup.html     # Login/landing page
```

---

## Database Schema

You need four tables in your PostgreSQL database:

```sql
CREATE TABLE users (
    userid SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    phoneno TEXT
);

CREATE TABLE tasks (
    taskid SERIAL PRIMARY KEY,
    userid INT REFERENCES users(userid),
    title TEXT NOT NULL,
    task_description TEXT,
    deadline DATE,
    status TEXT DEFAULT 'pending',
    priority TEXT DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE completed_tasks (
    taskid INT, userid INT, title TEXT,
    task_description TEXT, deadline DATE,
    status TEXT, completed_at DATE
);

CREATE TABLE failed_tasks (
    taskid INT, userid INT, title TEXT,
    task_description TEXT, deadline DATE,
    status TEXT, created_at TIMESTAMP, failed_at DATE
);
```

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <project-folder>
```

### 2. Install dependencies

```bash
pip install fastapi uvicorn psycopg2-binary python-jose passlib[bcrypt] python-dotenv google-genai pydantic[email] jinja2 python-multipart
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```
password=your_postgres_password
API_KEY=your_google_gemini_api_key
```

Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/).

### 4. Set up the database

Create a PostgreSQL database named `mydb` and run the schema above. The app connects to `localhost` as user `postgres` by default — edit `databaseConnection.py` if your setup differs.

### 5. Run the server

```bash
uvicorn main:app --reload
```

Then open `http://localhost:8000` in your browser.

---

## API Endpoints

### Auth

| Method | Endpoint | Description |
|---|---|---|
| POST | `/signup` | Register a new user |
| GET | `/signup2` | Render the signup page |
| POST | `/login` | Login and set session cookie |
| POST | `/logout` | Clear session cookie and redirect |

### Tasks

| Method | Endpoint | Description |
|---|---|---|
| GET | `/alltasks` | Fetch all active tasks for the logged-in user |
| POST | `/sendtask` | Create a new task manually |
| PUT | `/update_task/{task_id}` | Update a task; auto-archives if completed/failed |
| DELETE | `/delete/{taskid}` | Delete a task |
| POST | `/gettaskid` | Look up a task's ID by title |
| POST | `/check/{taskid}` | Check if a task is overdue or completed |
| POST | `/createTaskViaAI` | Create a task by pasting free-form text |

---

## AI Task Creation

The `/createTaskViaAI` endpoint accepts a plain-text input (such as a forwarded email or a rough note) and uses Google Gemini to extract:

- **Title** — short summary
- **Description** — brief details
- **Deadline** — parsed date (`YYYY-MM-DD`), defaults to the near future if none is found
- **Priority** — High / Medium / Low
- **Status** — always starts as Pending

The agent tries models in this order: `gemini-3-flash` → `gemini-2.5-flash` → `gemini-2.0-flash`.

---

## Security Notes

- Passwords are hashed with bcrypt and never stored in plaintext.
- JWTs are stored in `httponly` cookies (not accessible to JavaScript) and expire after 24 hours.
- The `secret_key` in `auth_utils.py` should be replaced with a long, random secret in production and loaded from an environment variable.

---

## License

MIT
