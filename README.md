# MyToDo App

**MyToDo App** (MyToDos) is a simple, lightweight to-do list application. Each user has their own account and their own private list of todos, with support for priority levels and due dates.

See [PRD.md](./PRD.md) for full product requirements.

## Features

- Sign up / log in with a username and password (JWT-based auth)
- Create, list, complete/uncomplete, and delete todos — each user only sees their own
- Priority (Low/Medium/High, color-coded badge) and optional due date per todo; overdue dates highlighted in red
- Filter todos by status: **All**, **Active**, or **Completed** — with live count badges
- Bulk select via per-row checkboxes + Select All toggle; **bulk complete** or **bulk delete** selected items in one click
- Delete (single or bulk) requires a custom animated modal confirmation — no browser `alert()`
- Modern, responsive UI with light/dark mode toggle

## Project Structure

```
backend/
  main.py              # FastAPI app, CORS, route registration
  database.py           # SQLAlchemy engine/session (SQLite)
  models.py              # User, Todo ORM models
  schemas.py              # Pydantic request/response schemas
  auth.py                  # Password hashing, JWT creation/validation
  routers/
    auth.py                 # /auth/signup, /auth/login
    todos.py                 # /todos CRUD
  tests/                      # pytest suite (auth, todos, ownership isolation)
  requirements.txt

frontend/
  src/
    api.js                  # fetch wrapper for the backend API
    App.jsx                  # top-level auth state / view switch
    App.css, index.css        # styling
    components/
      AuthPage.jsx              # login / signup form
      TodoPage.jsx              # main page: state, filter logic, bulk actions
      AddTodoForm.jsx           # new-task input card
      TodoList.jsx              # list wrapper with select-all header
      TodoItem.jsx              # single todo row (toggle, delete)
      ConfirmModal.jsx          # reusable animated modal for delete confirmations
  package.json
```

## Getting Started

### Backend

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate        # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
uvicorn main:app --reload
```

Runs on `http://localhost:8000`. A `claudetodo.db` SQLite file is created automatically on first run.

Run the test suite:

```bash
pytest -q
```

Optional environment variable:

- `SECRET_KEY` — JWT signing secret. Defaults to an insecure dev value; set this for anything beyond local development.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs on `http://localhost:5173` and expects the backend at `http://localhost:8000` (override via a `VITE_API_URL` env variable, e.g. in a `.env` file). The backend's CORS config allows `http://localhost:5173` by default.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|--------------|
| GET | `/health` | Health check |
| POST | `/auth/signup` | Create a new user account |
| POST | `/auth/login` | Authenticate, returns a JWT access token |
| GET | `/todos` | List the logged-in user's todos |
| POST | `/todos` | Create a todo |
| PATCH | `/todos/{id}` | Update a todo (e.g. toggle `completed`) |
| DELETE | `/todos/{id}` | Delete a todo |

All `/todos` endpoints require an `Authorization: Bearer <token>` header.
