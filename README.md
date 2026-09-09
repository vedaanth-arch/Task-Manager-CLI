# Task Manager API

FastAPI + PostgreSQL + JWT Auth — a portfolio-grade backend REST API for managing personal tasks.

**Version:** 1.0
**Type:** RESTful Backend API
**Status:** Draft for Development

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [System Overview](#2-system-overview)
3. [Main Tasks, Roles & Usage](#3-main-tasks-roles--usage)
4. [Functional Requirements](#4-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Data Model](#6-data-model)
7. [API Contract](#7-api-contract)
8. [Project Folder Structure](#8-project-folder-structure)
9. [Out of Scope (v1)](#9-out-of-scope-v1)
10. [Acceptance Criteria (Definition of Done)](#10-acceptance-criteria-definition-of-done)

---

## 1. Introduction

### 1.1 Purpose
This document specifies the functional and non-functional requirements, system architecture, data model, and API contract for a Task Manager API. It serves as the reference for implementation, so requirements are unambiguous enough to code directly from.

### 1.2 Scope
The system is a backend-only REST API that lets registered users create accounts, authenticate, and manage their own personal task lists. No frontend is included — the API is designed to be consumed by any client (web, mobile, CLI, Postman) via HTTP/JSON.

### 1.3 Intended Audience
Solo/portfolio developer implementing the project, and any reviewer (interviewer, collaborator) assessing it against professional backend standards.

### 1.4 Definitions
| Term | Meaning |
|---|---|
| JWT | JSON Web Token — signed token used for stateless authentication |
| ORM | Object-Relational Mapper (SQLAlchemy) |
| CRUD | Create, Read, Update, Delete |
| Owner | The user who created a given task; the only user allowed to modify/delete it |

---

## 2. System Overview

### 2.1 High-Level Architecture

```
Client (Postman/Browser/App)
        │  HTTPS/JSON
        ▼
   FastAPI Application
   ├── Routers (auth, tasks)
   ├── Dependency Layer (get_db, get_current_user)
   ├── Pydantic Schemas (validation)
   ├── CRUD Layer (business logic)
   └── SQLAlchemy ORM Models
        │
        ▼
   PostgreSQL Database
```

### 2.2 Technology Stack
| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Web Framework | FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| DB Driver | asyncpg |
| Database | PostgreSQL |
| Migrations | Alembic |
| Auth | OAuth2 Password Flow + JWT (python-jose) |
| Password Hashing | passlib[bcrypt] |
| Validation | Pydantic v2 |
| Server | Uvicorn (ASGI) |
| Testing | Pytest + httpx.AsyncClient |
| Config | pydantic-settings + `.env` |
| Containerization | Docker + docker-compose |

---

## 3. Main Tasks, Roles & Usage

### 3.1 Main Tasks (What the App Actually Does)

**User Account Management**
- Register a new account (email + password)
- Log in and receive a JWT token
- View own profile

**Task (To-Do) Management — the core feature**
- Create a task (title, description)
- View all your tasks (with pagination/filtering)
- View one task in detail
- Update a task (edit text, mark done/undone)
- Delete a task

**Security Enforcement**
- Block anyone without a valid token from touching `/tasks`
- Make sure User A can never see, edit, or delete User B's tasks

### 3.2 Roles

This is a simple single-role system — there's no "admin vs regular user" split in v1.

| Role | Can Do |
|---|---|
| **Authenticated User** | Full CRUD on their *own* tasks only |
| **Anonymous/Unauthenticated** | Can only register or log in — nothing else |

**Future extension (Phase 2, not in v1 scope):** an **Admin role** that can view/manage all users' tasks — a natural next step for demonstrating role-based access control (RBAC).

### 3.3 Usage — Who/What This API Is For

This is the **backend engine for any to-do app**. It has no UI — it's meant to be called by:
- A web frontend (React/Vue) built later
- A mobile app
- A CLI tool
- Postman/curl, for testing and demoing

**Typical real-world usage flow:**
1. User signs up via a frontend form → hits `POST /auth/register`
2. User logs in → hits `POST /auth/login` → frontend stores the JWT
3. Every subsequent request (create/view/edit/delete tasks) sends that JWT in the header
4. Frontend renders the task list by calling `GET /tasks`

This mirrors the same architectural pattern used in real production backends — auth → ownership-scoped resources → database-backed CRUD — the same shape as Trello's, Todoist's, or Jira's issue-tracking backend, just simplified.

---

## 4. Functional Requirements

### 4.1 User Management
| ID | Requirement |
|---|---|
| FR-1 | System shall allow a new user to register with email + password |
| FR-2 | System shall reject registration with a duplicate email (409 Conflict) |
| FR-3 | System shall hash passwords with bcrypt before storage — never store plaintext |
| FR-4 | System shall authenticate a user via email + password and issue a JWT access token |
| FR-5 | System shall reject invalid login credentials (401 Unauthorized) |
| FR-6 | System shall expose a `/users/me` endpoint returning the logged-in user's profile |

### 4.2 Task Management
| ID | Requirement |
|---|---|
| FR-7 | Authenticated users shall be able to create a task (title required, description optional) |
| FR-8 | Authenticated users shall be able to list only their own tasks |
| FR-9 | Authenticated users shall be able to retrieve a single task by ID (only if they own it) |
| FR-10 | Authenticated users shall be able to update a task's title/description/completion status |
| FR-11 | Authenticated users shall be able to delete their own task |
| FR-12 | System shall return 404 if a task doesn't exist, and 403 if it exists but belongs to another user |
| FR-13 | Task list endpoint shall support pagination via `limit`/`offset` query params |
| FR-14 | Task list endpoint shall support filtering by completion status (`?done=true/false`) |

### 4.3 Authorization
| ID | Requirement |
|---|---|
| FR-15 | All `/tasks/*` endpoints shall require a valid JWT in the `Authorization: Bearer <token>` header |
| FR-16 | Requests with missing/expired/invalid tokens shall return 401 |

---

## 5. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-1 | All DB I/O shall be async (non-blocking) end-to-end |
| NFR-2 | API responses shall follow consistent JSON error format `{"detail": "..."}` |
| NFR-3 | Sensitive fields (hashed_password) shall never appear in any response schema |
| NFR-4 | System shall auto-generate OpenAPI docs at `/docs` and `/redoc` |
| NFR-5 | Configuration (DB URL, JWT secret, token expiry) shall be environment-variable driven, never hardcoded |
| NFR-6 | Database schema changes shall be managed via Alembic migrations, not `create_all()` |
| NFR-7 | Application shall be containerized and runnable via `docker-compose up` |
| NFR-8 | Core CRUD and auth flows shall have automated test coverage |

---

## 6. Data Model

### 6.1 Entity-Relationship Overview
```
User (1) ──────< (many) Task
```
One user owns many tasks; each task belongs to exactly one user.

### 6.2 `users` Table
| Column | Type | Constraints |
|---|---|---|
| id | Integer / UUID | Primary Key |
| email | String | Unique, Not Null, Indexed |
| hashed_password | String | Not Null |
| created_at | Timestamp | Default now() |

### 6.3 `tasks` Table
| Column | Type | Constraints |
|---|---|---|
| id | Integer / UUID | Primary Key |
| title | String | Not Null |
| description | Text | Nullable |
| done | Boolean | Default False |
| owner_id | Integer / UUID | Foreign Key → users.id, Not Null |
| created_at | Timestamp | Default now() |
| updated_at | Timestamp | Auto-updated on change |

---

## 7. API Contract

Base URL: `/api/v1`

### 7.1 Auth Endpoints
| Method | Path | Auth Required | Description |
|---|---|---|---|
| POST | `/auth/register` | No | Create new user |
| POST | `/auth/login` | No | Returns `{access_token, token_type}` |
| GET | `/users/me` | Yes | Current user profile |

### 7.2 Task Endpoints
| Method | Path | Auth Required | Description |
|---|---|---|---|
| POST | `/tasks` | Yes | Create task |
| GET | `/tasks?limit=&offset=&done=` | Yes | List current user's tasks |
| GET | `/tasks/{task_id}` | Yes | Get single task |
| PUT | `/tasks/{task_id}` | Yes | Update task |
| DELETE | `/tasks/{task_id}` | Yes | Delete task |

### 7.3 Sample Schemas

**TaskCreate (request)**
```json
{ "title": "Finish SRS doc", "description": "Optional details" }
```

**TaskOut (response)**
```json
{
  "id": 1,
  "title": "Finish SRS doc",
  "description": "Optional details",
  "done": false,
  "created_at": "2026-09-01T10:00:00Z"
}
```

### 7.4 Status Codes Used
| Code | Meaning |
|---|---|
| 200 | Success |
| 201 | Resource created |
| 204 | Deleted, no content |
| 401 | Not authenticated |
| 403 | Authenticated but not authorized (not the owner) |
| 404 | Resource not found |
| 409 | Conflict (duplicate email) |
| 422 | Validation error (auto from Pydantic) |

---

## 8. Project Folder Structure

```
app/
├── main.py
├── core/
│   ├── config.py
│   └── security.py
├── db/
│   ├── base.py
│   └── session.py
├── models/
│   ├── user.py
│   └── task.py
├── schemas/
│   ├── user.py
│   └── task.py
├── api/routes/
│   ├── auth.py
│   └── tasks.py
├── crud/
│   ├── user.py
│   └── task.py
└── deps.py
tests/
alembic/
docker-compose.yml
Dockerfile
.env
requirements.txt
```

---

## 9. Out of Scope (v1)
- Frontend/UI
- Task sharing between users
- Email verification / password reset flow
- Refresh token rotation (access token only for v1)
- Rate limiting (noted as future NFR)

---

## 10. Acceptance Criteria (Definition of Done)
- [ ] User can register, login, and receive a JWT
- [ ] All task endpoints reject unauthenticated requests (401)
- [ ] A user cannot access/modify another user's task (403)
- [ ] Alembic migration history exists and matches models
- [ ] `/docs` renders complete, accurate OpenAPI schema
- [ ] `docker-compose up` boots API + DB with zero manual steps
- [ ] Pytest suite covers register, login, and full task CRUD lifecycle
