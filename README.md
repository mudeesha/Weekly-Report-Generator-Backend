# Weekly Report Generator — FastAPI Backend

A real **FastAPI + Python** backend for the Weekly Report Generator and Team Dashboard. It provides authentication, role-based access, project management, weekly report workflow, report version history, dashboards, analytics, and the Gemini-backed AI assistant.

## Stack

- Python 3.12

- FastAPI

- SQLAlchemy Async

- asyncmy

- MySQL 8

- Alembic

- Pydantic

- JWT Authentication

- Argon2 password hashing

- Gemini AI

- pytest

## Local setup

Requirements: Python 3.12+, MySQL 8, and Git.

Create and activate a virtual environment.

```bash

python3.12 -m venv .venv

source .venv/bin/activate

```

Install all backend dependencies directly from `requirements.txt`.

```bash

pip install -r requirements.txt

```

Create the environment file.

```bash

cp .env.example .env

```

Update `.env` with your local configuration.

```env

DATABASE_URL=mysql+asyncmy://root@127.0.0.1:3306/weekly_report

JWT_SECRET_KEY=CHANGE_THIS_TO_A_SECURE_SECRET

JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=60

CORS_ORIGINS=http://127.0.0.1:3000

GEMINI_API_KEY=YOUR_GEMINI_API_KEY

GEMINI_MODEL=gemini-3.7-flash

AI_CONTEXT_WEEKS=12

```

Never commit database passwords, JWT signing secrets, Gemini API keys, or the `.env` file.

## Database setup

Start MySQL.

```bash

sudo systemctl start mysql

```

Login to MySQL.

```bash

mysql -u root -p

```

Create the database.

```sql

CREATE DATABASE weekly_report

CHARACTER SET utf8mb4

COLLATE utf8mb4_unicode_ci;

```

Exit MySQL.

```sql

EXIT;

```

Run database migrations.

```bash

alembic upgrade head

```

Seed the demo users and project after running the migrations.

```bash

uv run python -m app.db.seeders.demo_data

```

## Run backend

Start the FastAPI development server.

```bash

uvicorn app.main --reload

```

Open **http://127.0.0.1:8000**.

Swagger API documentation is available at:

```text

http://127.0.0.1:8000/docs

```

## Commands

```bash

pip install -r requirements.txt

alembic upgrade head

uv run python -m app.db.seeders.demo_data

uvicorn app.main --reload

pytest -q

```

## Architecture

```text

Router

↓

Service

↓

Repository

↓

SQLAlchemy

↓

MySQL

```

The router handles HTTP requests and authentication. The service layer contains business rules and workflow logic. The repository layer handles database queries and persistence.

## Main features

- JWT authentication

- Team Member, Manager, and Admin roles

- User management

- Project management and member assignment

- Weekly report creation and submission

- Report review and correction workflow

- Report version history

- Draft privacy

- Dashboard and analytics

- Gemini AI assistant

## Report workflow

```text

DRAFT

↓

SUBMITTED

↓

MANAGER REVIEW

├── APPROVED

└── NEEDS_CORRECTION

     ↓

EDIT NEW VERSION

     ↓

  SUBMITTED

     ↓

  APPROVED

```

Old submitted versions remain unchanged. Manager reviews are linked to the exact report version being reviewed.

## Role access

| Feature | Team Member | Manager | Admin |

|---|---:|---:|---:|

| Create/edit own reports | Yes | No | No |

| Submit own reports | Yes | No | No |

| View team reports | No | Yes | Yes |

| Request corrections | No | Yes | Yes |

| Approve reports | No | Yes | Yes |

| Dashboard and analytics | No | Yes | Yes |

| Manage projects | No | Yes | Yes |

| Manage users | No | No | Yes |

| AI assistant | No | Yes | Yes |

The backend remains the final authorization boundary. Role and active status are checked on protected requests.

## AI assistant

The backend exposes:

```text

POST /api/v1/ai/chat

```

The backend first loads relevant submitted report data, creates structured context, and then sends that context to Gemini.

The Gemini API key remains only in the FastAPI backend.

## Verification

After installing dependencies and configuring the database, run:

```bash

pytest -q

```

Then start the backend:

```bash

uvicorn app.main --reload

```