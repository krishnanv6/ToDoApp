# Product Requirements Document: MyToDos

**Version:** 1.3
**Date:** September 19, 2026
**Author:** Product Team

---

## 1. Overview

**MyToDos** is a simple, lightweight to-do list application that allows users to create, complete, and delete tasks. Each user has their own account and their own private list of todos.

## 2. Problem Statement

Users need a quick, easy way to track personal tasks — with priority and due dates — without dealing with bloated, feature-heavy to-do apps.

## 3. Goals

- Provide a minimal, easy-to-use to-do list application.
- Support multiple users, each with their own login and private todo list.
- Allow users to create, mark complete, and delete todos.
- Support priority and due date on each todo.
- Persist data reliably using SQLite.

## 4. Non-Goals

- No password reset / email verification flows (v1) — basic login only.
- No categories, tags, reminders/notifications, or recurring todos (v1).
- No mobile app (web only for v1).
- No sharing/collaboration between users (v1).

## 5. Target Users

Individuals looking for a simple personal task tracker they can log into and access their own list.

## 6. Features & Requirements

### 6.1 User Accounts
- Users can sign up with a username/email and password.
- Users can log in and log out.
- Each user only sees and manages their own todos.
- Passwords stored securely (hashed, never plain text).

### 6.2 Create Todo
- Logged-in user can add a new todo with:
  - `id` (unique identifier)
  - `title` (text description, required)
  - `priority` (Low / Medium / High)
  - `due_date` (date, optional)
  - `completed` (boolean, default `false`)
  - `created_at` (timestamp)
  - `owner_id` (linked to logged-in user)
- Empty title should not be allowed (basic validation).

### 6.3 View Todos
- Display all todos belonging to the logged-in user.
- Show title, priority, due date, and completion status.
- Visually distinguish completed vs. incomplete todos (e.g., strikethrough).

### 6.3a Status Filter
- A **filter bar** is displayed above the todo list with three options: **All**, **Active**, **Completed**.
- Each filter option shows a count badge reflecting the current number of todos in that category.
- Selecting **Active** shows only todos where `completed = false`.
- Selecting **Completed** shows only todos where `completed = true`.
- Selecting **All** (default) shows every todo regardless of status.
- Filtering is performed client-side; no extra API requests are made.
- Changing the active filter clears any current bulk selection to prevent operating on hidden items.

### 6.4 Mark Todo as Complete
- User can toggle a todo between complete and incomplete states.
- UI updates immediately to reflect the state change.

### 6.5 Delete Todo
- User can delete their own todo from the list.
- A **custom modal confirmation dialog** (not a browser alert) is shown before deleting, displaying the todo title and a warning that the action cannot be undone.
- Deletion is immediate and permanent once confirmed (no undo in v1).

### 6.6 Bulk Delete
- User can select multiple todos simultaneously using per-row select checkboxes.
- A "Select All / Deselect All" control is available at the top of the list.
- When one or more todos are selected, a **bulk action bar** appears showing the selected count and a "Delete {n}" button.
- Confirming bulk delete shows a custom modal (same style as single-delete) that states the number of items being permanently deleted.
- All selected todos are deleted in a single operation; the list updates immediately on confirmation.

## 7. User Stories

| # | As a... | I want to... | So that... |
|---|---------|---------------|------------|
| 1 | User | Sign up and log in | I can access my own private todo list |
| 2 | User | Add a new todo with priority and due date | I can track a task and its urgency |
| 3 | User | Mark a todo as complete | I know what I've finished |
| 4 | User | Delete a todo | I can remove tasks I no longer need |
| 5 | User | See all my todos in one place | I can review my task list |
| 6 | User | Filter todos by status (All / Active / Completed) | I can focus on what still needs to be done or review what I've finished |

## 8. Technical Requirements

### 8.1 Architecture
- **Frontend:** React (single-page application)
- **Backend:** Python with FastAPI (REST API)
- **Data Storage:** SQLite (via SQLAlchemy or similar ORM)
- **Authentication:** JWT-based session tokens (login returns a token; frontend sends it on each request)

### 8.2 API Endpoints (Backend - FastAPI)

| Method | Endpoint | Description |
|--------|----------|--------------|
| POST | `/auth/signup` | Create a new user account |
| POST | `/auth/login` | Authenticate user, return access token |
| GET | `/todos` | Retrieve all todos for logged-in user |
| POST | `/todos` | Create a new todo for logged-in user |
| PATCH | `/todos/{id}` | Update todo (toggle complete, edit priority/due date) |
| DELETE | `/todos/{id}` | Delete a todo (only if owned by logged-in user) |

**Sample Todo Object (JSON):**
```json
{
  "id": 1,
  "title": "Buy groceries",
  "priority": "Medium",
  "due_date": "2026-09-25",
  "completed": false,
  "created_at": "2026-09-18T10:00:00Z",
  "owner_id": 7
}
```

**Sample User Object (JSON):**
```json
{
  "id": 7,
  "username": "jane_doe",
  "created_at": "2026-09-18T09:00:00Z"
}
```

### 8.3 Frontend (React)
- Login / Signup page.
- Main todo page (accessible only when logged in):
  - Input field for title, dropdown for priority, date picker for due date, "Add" button.
  - List view of todos with:
    - Per-row **select checkbox** (left) for bulk selection, and a **circular complete checkbox** for toggling done state.
    - Title (strikethrough when completed), color-coded priority badge, due date (highlighted red when overdue).
    - A left accent border on each card colored by priority (red/amber/green).
    - Trash **icon** button (SVG, no text) that triggers a **custom modal confirm dialog** before deleting.
  - **Status filter bar**: segmented pill control (All / Active / Completed) rendered between the add form and the todo list; each option includes a live count badge; defaults to "All" on load (see 6.3a).
  - **Bulk action bar**: appears when ≥1 todos are selected; shows count and "Delete {n}" button; triggers a custom modal before deleting all selected (see 6.6).
  - **Select All / Deselect All** checkbox at the top of the list.
  - Priority is shown as a color-coded pill badge (High=red, Medium=amber, Low=green).
- Store auth token (e.g., in memory or localStorage) and attach to API requests.
- Fully responsive design (usable on desktop and mobile browsers).
- **Polished, modern visual design** using the Inter typeface, indigo gradient accent, card-per-todo layout with left priority border, smooth hover/focus transitions, gradient "Add" button, and light/dark mode support. Auth page features a logo icon + tagline. No browser `alert()`/`confirm()` — all confirmations use an in-app animated modal.

## 9. Security Considerations

- Passwords hashed using a standard algorithm (e.g., bcrypt).
- API endpoints for todos require a valid auth token.
- Users can only access/modify their own todos (enforced on backend, not just UI).

## 10. Success Metrics

- User can successfully sign up, log in, create, complete, and delete a todo with no errors.
- Page load time under 2 seconds.
- Core actions (create/complete/delete) reflected in UI within 500ms.

## 11. Future Considerations (Out of Scope for v1)

- Password reset via email
- Categories/tags
- Reminders/notifications for due dates
- Recurring todos
- Sharing/collaboration between users
- Cloud-hosted database with backups

## 12. Timeline (Suggested)

| Phase | Duration |
|-------|----------|
| Backend API + Auth development | 4 days |
| Frontend UI development | 4 days |
| Integration & testing | 2 days |
| **Total** | **~2 weeks** |

## 13. Implementation Notes (v1 — as built)

Tracks concrete decisions made while implementing this PRD, so the document stays accurate as a reference.

- **App name:** implemented as "MyToDo App" in the UI/browser title.
- **Backend stack:** FastAPI + SQLAlchemy (SQLite file `claudetodo.db`), password hashing via `bcrypt`, JWT via `PyJWT` (HS256, 24h expiry, `SECRET_KEY` env var with a dev-only default).
- **Auth:** login/signup use JSON bodies (not OAuth2 form-encoded); `/todos` endpoints require a `Bearer` token via `HTTPBearer`; accessing/modifying another user's todo returns `404` (not `403`) to avoid leaking existence.
- **Backend tests:** pytest suite (`backend/tests/`) covers signup/login, auth enforcement, todo CRUD, empty-title validation, and cross-user isolation.
- **Frontend stack:** Vite + React, no router library (two views toggled by local auth state, per the "minimal app" goal). Auth token persisted in `localStorage`.
- **CORS:** backend allows `http://localhost:5173` (Vite dev server) for local development.
- **UI:** polished card-based layout with Inter typeface, indigo gradient accent, left priority-color border on each todo card, smooth hover/transition animations, and light/dark mode support. Priority shown as a color-coded pill badge. Delete uses an SVG trash icon (no text) and triggers a custom animated modal confirm dialog (no `window.confirm`). Overdue dates are highlighted red.
- **Status filter:** pill-style filter bar (All / Active / Completed) between the add form and the list; each tab shows a live count badge; filtering is purely client-side (no extra API calls); switching filter clears bulk selection.
- **Bulk delete:** select checkboxes on each row + "Select All" toggle; bulk action bar with count + "Delete {n}" button; custom modal confirmation before bulk delete executes.
- **Single-delete modal:** custom `ConfirmModal` component (animated backdrop + scaled card) used for both single and bulk deletes.
- **Auth page:** logo icon, app name, tagline, pill-style tab switcher, uppercase-label form fields.

---

**End of Document**
