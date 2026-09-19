# ClaudeTodo

## Project Overview
ClaudeTodo — a React + FastAPI todo app demonstrating Claude Code capabilities

## Tech Stack
- Backend: Python 3.10+, FastAPI, in-memory list storage (no database yet)
- Frontend: React 18 with Vite, plain CSS, functional components only

## Code Style
- Python: snake_case, type hints on all functions
- JavaScript: camelCase for variables, PascalCase for components
- No inline CSS — styles in .css files

## Architecture Rules
- All API routes in backend/main.py
- All frontend API calls go through frontend/src/api.js
- Frontend state with React hooks only (no Redux)

## Commands
- Backend: uvicorn main:app --reload (from backend/)
- Frontend: npm run dev (from frontend/)
